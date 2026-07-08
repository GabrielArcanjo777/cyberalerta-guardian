"use client"

import Link from 'next/link'
import {useEffect} from 'react'

export default function Error({error, reset}: {error: Error & {digest?: string}, reset: () => void}){
  useEffect(()=>{
    // Client-side render error — log for diagnostics, never show internals to the user.
    console.error(error)
  },[error])

  return (
    <main role="alert" style={{maxWidth:560, margin:'0 auto', padding:'64px 24px', textAlign:'center'}}>
      <h1 style={{fontSize:26, marginBottom:8}}>Algo não carregou como esperado</h1>
      <p style={{color:'#8b96a3', marginBottom:24}}>
        Tivemos um problema ao abrir esta parte do CyberAlerta. Nada foi perdido —
        você pode tentar de novo ou voltar para o início.
      </p>
      <div style={{display:'flex', gap:12, justifyContent:'center'}}>
        <button
          onClick={reset}
          style={{padding:'10px 18px', borderRadius:8, border:'1px solid #2f8f8a', background:'#2f8f8a', color:'#fff', fontWeight:700, cursor:'pointer'}}
        >
          Tentar novamente
        </button>
        <Link
          href="/"
          style={{padding:'10px 18px', borderRadius:8, border:'1px solid #d2d6cf', color:'#1f5f5b', textDecoration:'none', fontWeight:700}}
        >
          Voltar ao início
        </Link>
      </div>
    </main>
  )
}
