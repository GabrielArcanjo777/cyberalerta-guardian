"use client"

import React, {useEffect, useRef, useState} from 'react'

type Props = {
  children: React.ReactNode
  className?: string
  delay?: number
  as?: React.ElementType
}

export default function HomeScrollReveal({children,className='',delay=0,as='section'}:Props){
  const ref = useRef<HTMLElement | null>(null)
  const [visible,setVisible]=useState(false)

  useEffect(()=>{
    const node = ref.current
    if(!node) return

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if(reducedMotion){
      setVisible(true)
      return
    }

    const observer = new IntersectionObserver(([entry])=>{
      if(entry.isIntersecting){
        setVisible(true)
        observer.disconnect()
      }
    }, {threshold:0.16, rootMargin:'0px 0px -8% 0px'})

    observer.observe(node)
    return ()=>observer.disconnect()
  },[])

  const Component = as as any

  return (
    <Component
      ref={ref}
      className={`home-reveal ${visible ? 'is-visible' : ''} ${className}`.trim()}
      style={{transitionDelay: visible ? `${delay}ms` : '0ms'}}
    >
      {children}
    </Component>
  )
}
