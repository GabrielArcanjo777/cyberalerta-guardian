"use client"

import Image from 'next/image'
import Link from 'next/link'
import React, {useCallback, useEffect, useRef, useState} from 'react'
import Button from '@/components/Button'
import ProtectedRoute from '@/components/ProtectedRoute'
import {getEvolutionStatus, getEvolutionQr, postEvolutionReconnect} from '@/lib/api'
import {EvolutionConnectionState} from '@/lib/types'

const STATE_LABEL: Record<string, string> = {
  not_configured: 'Não configurado',
  unreachable: 'Evolution offline',
  close: 'Desconectado',
  connecting: 'Aguardando pareamento',
  open: 'Conectado',
  unknown: 'Desconhecido',
}

const STATE_COLOR: Record<string, string> = {
  not_configured: '#9aa0a6',
  unreachable: '#c9791f',
  close: '#c23b34',
  connecting: '#2f8f8a',
  open: '#2e9e5b',
  unknown: '#9aa0a6',
}

export default function WhatsAppSetupPage(){
  const [status,setStatus] = useState<EvolutionConnectionState | null>(null)
  const [loading,setLoading] = useState(false)
  const [error,setError] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setInterval> | null>(null)

  const refresh = useCallback(async (withQr:boolean)=>{
    try{
      const next = withQr ? await getEvolutionQr() : await getEvolutionStatus()
      setStatus(next)
      setError(null)
      return next
    }catch{
      setError('Não foi possível falar com o backend. Faça login novamente e confirme se a API está no ar.')
      return null
    }
  },[])

  // Poll while not connected so the QR / status stays fresh during pairing.
  useEffect(()=>{
    let active = true
    const tick = async ()=>{
      const current = await refresh(true)
      if(!active) return
      if(current && current.connected && timer.current){
        clearInterval(timer.current)
        timer.current = null
      }
    }
    tick()
    timer.current = setInterval(tick, 4000)
    return ()=>{ active = false; if(timer.current) clearInterval(timer.current) }
  },[refresh])

  async function reconnect(){
    setLoading(true)
    setError(null)
    try{
      setStatus(await postEvolutionReconnect())
    }catch{
      setError('Falha ao reconectar. Confirme se a Evolution API está rodando.')
    }finally{
      setLoading(false)
    }
  }

  const state = status?.state ?? 'unknown'
  const label = STATE_LABEL[state] ?? state
  const color = STATE_COLOR[state] ?? '#9aa0a6'

  return (
    <ProtectedRoute>
      <main style={{maxWidth:720, margin:'0 auto', padding:'40px 20px'}}>
        <p style={{fontSize:12, letterSpacing:'0.08em', textTransform:'uppercase', color:'#8b96a3'}}>
          Canal WhatsApp · Evolution API
        </p>
        <h1 style={{fontSize:28, margin:'8px 0 4px'}}>Conectar WhatsApp</h1>
        <p style={{color:'#8b96a3', maxWidth:560}}>
          Pareie um número de WhatsApp escaneando o QR code, igual ao WhatsApp Web.
          O CyberAlerta usa esse número para receber mensagens suspeitas e alertar o responsável.
        </p>

        <div style={{display:'flex', alignItems:'center', gap:10, margin:'20px 0'}}>
          <span aria-hidden style={{width:10, height:10, borderRadius:'50%', background:color, display:'inline-block'}} />
          <strong>{label}</strong>
          {status?.instance && <span style={{color:'#8b96a3'}}>· instância {status.instance}</span>}
        </div>

        {error && (
          <p role="alert" style={{background:'#fbe9e7', color:'#c23b34', padding:'10px 14px', borderRadius:8}}>{error}</p>
        )}

        {status?.state === 'not_configured' && (
          <div style={{border:'1px solid #d2d6cf', borderRadius:10, padding:16}}>
            <p style={{margin:0}}>
              Configure <code>EVOLUTION_API_URL</code>, <code>EVOLUTION_API_KEY</code> e{' '}
              <code>EVOLUTION_INSTANCE_NAME</code> no <code>.env</code> do backend e suba a Evolution API
              (Docker) para habilitar o pareamento.
            </p>
          </div>
        )}

        {status?.connected && (
          <div style={{border:'1px solid #cfe8d8', background:'#eef7f1', borderRadius:10, padding:16}}>
            <strong style={{color:'#2e7d4f'}}>WhatsApp conectado.</strong>
            <p style={{margin:'6px 0 0', color:'#3a4450'}}>
              O número está pareado e pronto para receber mensagens. Você pode fechar esta página.
            </p>
          </div>
        )}

        {status && !status.connected && status.qr_base64 && (
          <div style={{display:'flex', flexDirection:'column', alignItems:'center', gap:12, border:'1px solid #d2d6cf', borderRadius:12, padding:20}}>
            <Image src={status.qr_base64} alt="QR code para parear o WhatsApp" width={260} height={260} unoptimized />
            <p style={{margin:0, textAlign:'center', color:'#3a4450'}}>
              {status.detail ?? 'Abra o WhatsApp > Aparelhos conectados > Conectar aparelho e escaneie.'}
            </p>
            {status.pairing_code && (
              <p style={{margin:0}}>Código de pareamento: <code>{status.pairing_code}</code></p>
            )}
          </div>
        )}

        {status && !status.connected && !status.qr_base64 && status.state !== 'not_configured' && (
          <div style={{border:'1px solid #d2d6cf', borderRadius:10, padding:16}}>
            <p style={{margin:0}}>{status.detail ?? 'Sessão indisponível. Tente reconectar.'}</p>
          </div>
        )}

        <div style={{display:'flex', gap:10, marginTop:20}}>
          <Button onClick={()=>refresh(true)} disabled={loading}>Atualizar</Button>
          <Button onClick={reconnect} disabled={loading || status?.state === 'not_configured'}>
            {loading ? 'Reconectando…' : 'Reconectar'}
          </Button>
        </div>

        <p style={{marginTop:24, fontSize:13, color:'#8b96a3', borderTop:'1px dashed #d2d6cf', paddingTop:16}}>
          ⚠️ {status?.limitation_notice ?? 'Canal não-oficial (WhatsApp Web/Baileys): risco de bloqueio do número e de queda de sessão. Uso de portfólio/demo, não produção.'}
        </p>

        <p style={{marginTop:8}}>
          <Link href="/admin" style={{color:'#1f5f5b'}}>← Voltar ao painel</Link>
        </p>
      </main>
    </ProtectedRoute>
  )
}
