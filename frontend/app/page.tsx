"use client"
import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'

export default function Home(){
  return (
    <main>
      <Card className="hero">
        <h1 className="text-4xl font-extrabold">CyberAlerta Guardian</h1>
        <p className="text-gray-700 mt-3 text-lg">Antes do Pix. Antes do clique. Antes do prejuizo.</p>
        <p className="mt-4 text-gray-600">Um agente de intervencao pre-dano contra golpes digitais.</p>
        <div className="mt-6 flex gap-3">
          <Link href="/before-pix"><Button>Antes do Pix</Button></Link>
          <Link href="/simulator"><Button variant="ghost">Simulador de Acoes</Button></Link>
          <Link href="/recovery"><Button variant="ghost">Ja cai em um golpe</Button></Link>
        </div>
      </Card>
      <div className="mt-6">
        <Card>
          <h3 className="text-lg font-semibold">Como funciona</h3>
          <p className="text-sm text-gray-600 mt-2">O Guardian analisa mensagens e ações suspeitas, interrompe decisões perigosas e orienta a familia.</p>
        </Card>
      </div>
    </main>
  )
}
