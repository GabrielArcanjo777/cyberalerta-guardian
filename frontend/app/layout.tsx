import './globals.css'
import React from 'react'
import Header from '@/components/Header'
import GlobalAmbientBackground from '@/components/GlobalAmbientBackground'

const antiFlashScript = `
(function(){
  try{
    var v=window.localStorage.getItem('cyberalerta-motion-preference')||window.localStorage.getItem('cyberalerta:a11y:reduced-motion');
    // In development, default to 'enabled' so animations always run.
    // Production should use 'system' as default.
    if(!v||v==='system') v='enabled';
    document.documentElement.setAttribute('data-motion',v);
  }catch(e){}
})();
`

export const metadata = {
  title: 'CyberAlerta Guardian',
  description: 'Antes do Pix. Antes do clique. Antes do prejuízo.'
}

export default function RootLayout({children}:{children:React.ReactNode}){
  return (
    <html lang="pt-BR" suppressHydrationWarning>
      <head>
        <script dangerouslySetInnerHTML={{__html: antiFlashScript}} />
      </head>
      <body>
        <div className="guardian-app-shell">
          <GlobalAmbientBackground />
          <a
            href="#conteudo-principal"
            className="sr-only focus:not-sr-only focus:fixed focus:left-4 focus:top-4 focus:z-[120] focus:rounded-md focus:bg-white focus:px-4 focus:py-3 focus:text-sm focus:font-bold focus:text-slate-950 focus:shadow-lg focus:outline focus:outline-2 focus:outline-offset-2 focus:outline-slate-950"
          >
            Pular para o conteúdo principal
          </a>
          <div className="guardian-content-shell mx-auto w-full max-w-[1760px] px-4 sm:px-6 lg:px-10 xl:px-14 overflow-x-hidden">
            <Header />
            <main id="conteudo-principal" className="relative z-10 mb-14 mt-8" tabIndex={-1}>{children}</main>
          </div>
        </div>
      </body>
    </html>
  )
}
