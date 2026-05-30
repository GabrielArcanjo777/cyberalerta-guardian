"use client"
import React from 'react'
import Link from 'next/link'
import Card from '@/components/Card'
import Button from '@/components/Button'

const scenarios = [
  {title:'Falso filho pedindo Pix', desc:'Mensagem urgente de alguém se passando por familiar'},
  {title:'Falso banco com link', desc:'Pedido para atualizar dados em site falso'},
  {title:'Pedido de código SMS', desc:'Solicitação de código de segurança'},
  {title:'Falso suporte técnico', desc:'App remoto para "resolver problemas"'},
]

export default function Simulator(){
  return (
    <main>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Simulador de Ações</h1>
        <p className="text-gray-600 mt-2">Teste cenários de golpe e veja como o Guardian responde</p>
      </div>

      <div className="grid gap-4 grid-cols-1 sm:grid-cols-2">
        {scenarios.map(s=> (
          <Card key={s.title} className="p-5 flex flex-col">
            <h4 className="font-semibold text-lg">{s.title}</h4>
            <p className="text-sm text-gray-600 mt-2 flex-1">{s.desc}</p>
            <div className="mt-4">
              <Link href="/before-pix"><Button>Testar</Button></Link>
            </div>
          </Card>
        ))}
      </div>
    </main>
  )
}
