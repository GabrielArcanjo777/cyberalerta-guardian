import './globals.css'
import React from 'react'
import Header from '@/components/Header'

export const metadata = {
  title: 'CyberAlerta Guardian',
  description: 'Antes do Pix. Antes do clique. Antes do prejuizo.'
}

export default function RootLayout({children}:{children:React.ReactNode}){
  return (
    <html lang="pt-BR">
      <body>
        <div className="min-h-screen bg-gray-50">
          <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
            <Header />
            <main className="mt-8 mb-12">{children}</main>
          </div>
        </div>
      </body>
    </html>
  )
}
