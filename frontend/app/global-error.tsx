"use client"

import {useEffect} from 'react'

export default function GlobalError({error, reset}: {error: Error & {digest?: string}, reset: () => void}){
  useEffect(()=>{
    console.error(error)
  },[error])

  return (
    <html lang="pt-BR">
      <body style={{fontFamily:'-apple-system, Segoe UI, Roboto, sans-serif', background:'#0d1117', color:'#eef1f3', margin:0}}>
        <main role="alert" style={{maxWidth:560, margin:'0 auto', padding:'80px 24px', textAlign:'center'}}>
          <h1 style={{fontSize:26, marginBottom:8}}>O aplicativo precisou reiniciar</h1>
          <p style={{color:'#8b96a3', marginBottom:24}}>
            Encontramos um erro inesperado. Você pode recarregar para continuar com segurança.
          </p>
          <button
            onClick={reset}
            style={{padding:'10px 18px', borderRadius:8, border:'1px solid #4db3ac', background:'#4db3ac', color:'#08201e', fontWeight:700, cursor:'pointer'}}
          >
            Recarregar
          </button>
        </main>
      </body>
    </html>
  )
}
