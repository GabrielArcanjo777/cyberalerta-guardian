import React from 'react'

export default function DemoModeBanner(){
  return (
    <div
      role="status"
      className="border-b border-white/10 bg-slate-950/72 px-4 py-2 text-center text-sm font-bold text-slate-100 backdrop-blur"
    >
      Demo Mode local: dados simulados, sem coleta de dados reais e sem envio real de mensagens.
    </div>
  )
}
