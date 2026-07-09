"use client"

import React, {useEffect, useState, useRef} from 'react'
import {useInView} from 'framer-motion'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'

const DEMO_LOGS = [
  {level:'INFO', msg:'sistema iniciado — DEMO LOCAL'},
  {level:'OK', msg:'webhook recebido'},
  {level:'RISK', msg:'padrão de urgência financeira detectado'},
  {level:'TRACE', msg:'decisão registrada no painel'},
  {level:'SKIP', msg:'duplicidade bloqueada por idempotência'},
  {level:'N8N', msg:'workflow validado localmente'},
  {level:'OK', msg:'WhatsApp via Evolution (não-oficial) pronto'},
]

export default function TerminalLogPanel(){
  const reduceMotion = usePrefersReducedMotion()
  const [visible, setVisible] = useState(reduceMotion ? DEMO_LOGS.length : 0)
  const [cursorVisible, setCursorVisible] = useState(true)
  const wrapperRef = useRef<HTMLDivElement>(null)
  const containerRef = useRef<HTMLDivElement>(null)
  const inView = useInView(wrapperRef, {once:true, amount:0.38})

  useEffect(()=>{
    if(reduceMotion){
      setVisible(DEMO_LOGS.length)
      return
    }
    if(!inView || visible >= DEMO_LOGS.length) return
    const timer = setTimeout(()=>setVisible(v=>v+1), visible === 0 ? 180 : 520)
    return ()=>clearTimeout(timer)
  },[visible, reduceMotion, inView])

  useEffect(()=>{
    if(reduceMotion) return
    const interval = setInterval(()=>setCursorVisible(v=>!v), 530)
    return ()=>clearInterval(interval)
  },[reduceMotion])

  useEffect(()=>{
    if(containerRef.current){
      containerRef.current.scrollTop = containerRef.current.scrollHeight
    }
  },[visible])

  return (
    <div ref={wrapperRef} className="cyber-terminal-integrated" role="log" aria-label="Log de demonstração do sistema">
      <div className="cyber-terminal-header">
        <div className="cyber-terminal-dots">
          <span className="cyber-dot cyber-dot-red" />
          <span className="cyber-dot cyber-dot-yellow" />
          <span className="cyber-dot cyber-dot-green" />
        </div>
        <span className="cyber-terminal-title">guardian — demo local</span>
        <span className="cyber-terminal-status-badge">LIVE_SYS_EVAL</span>
      </div>
      <div className="cyber-terminal-body" ref={containerRef}>
        {DEMO_LOGS.slice(0, visible).map((log, i)=>(
          <div key={i} className={`cyber-terminal-line cyber-terminal-line-${log.level.toLowerCase()}`}>
            <span className={`cyber-terminal-level cyber-level-${log.level.toLowerCase()}`}>[{log.level}]</span>
            <span className="cyber-terminal-msg">{log.msg}</span>
          </div>
        ))}
        <div className="cyber-terminal-line">
          <span className="cyber-terminal-prompt">{`$>`}</span>
          <span className={`cyber-terminal-cursor ${cursorVisible ? 'cyber-cursor-visible' : 'cyber-cursor-hidden'}`}>_</span>
        </div>
      </div>
    </div>
  )
}
