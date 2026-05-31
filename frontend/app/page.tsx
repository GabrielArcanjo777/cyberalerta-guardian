"use client"

import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import Shield3DScene from '@/components/Shield3DScene'
import AttackGlobe3D from '@/components/AttackGlobe3D'

const trustIndicators = [
  {label: 'TRUST LOCK', value: 'pausa protetiva antes da decisão'},
  {label: 'AUDITORIA', value: 'trace explicável dos agentes'},
  {label: 'REDE DE AJUDA', value: 'família e instituições acionáveis'},
]

const productPillars = [
  {
    title: 'Intervenção antes do Pix',
    body: 'Detecta urgência, pedido financeiro, identidade não verificada e tentativa de isolamento antes da transferência.',
  },
  {
    title: 'Decisão auditável',
    body: 'Exibe evidências, confiança, decisão de cada agente e motivo do Trust Lock em linguagem clara.',
  },
  {
    title: 'Ponte de proteção',
    body: 'Converte risco em ação para contatos de confiança, escolas, ONGs, condomínios e instituições.',
  },
  {
    title: 'Privacidade por design',
    body: 'Analisa somente conteúdo compartilhado voluntariamente, com avisos claros de simulação no MVP.',
  },
]

const operatingModel = [
  'Mensagem suspeita enviada voluntariamente',
  'Sinais de risco e manipulação são classificados',
  'Trust Lock interrompe a ação perigosa',
  'Contato de confiança recebe orientação simulada',
  'Relatório explica a decisão para auditoria',
]

export default function Home(){
  return (
    <main className="mx-auto max-w-7xl space-y-8 pb-16">
      <section className="guardian-panel-dark guardian-motion-in overflow-hidden rounded-md">
        <div className="grid min-h-[630px] lg:grid-cols-[1.02fr_0.98fr]">
          <div className="relative z-10 flex flex-col justify-center p-6 sm:p-8 lg:p-12">
            <div className="guardian-kicker">Console de proteção pré-dano</div>
            <h1 className="guardian-text-balance mt-6 max-w-4xl text-4xl font-extrabold leading-[1.02] text-white sm:text-5xl lg:text-6xl">
              Proteção antes do golpe virar prejuízo.
            </h1>
            <p className="mt-6 max-w-3xl text-base font-semibold leading-8 text-slate-300 sm:text-lg">
              O CyberAlerta Guardian ajuda responsáveis, famílias e instituições a revisar mensagens suspeitas, pausar ações perigosas e proteger pessoas vulneráveis antes de Pix, cliques, senhas ou acesso remoto.
            </p>

            <div className="mt-8 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Link href="/before-pix">
                <Button className="h-12 w-full !border-white !bg-white px-6 !text-slate-950 hover:!bg-cyan-50 sm:w-auto">
                  Abrir análise principal
                </Button>
              </Link>
              <Link href="/global">
                <Button variant="ghost" className="h-12 w-full px-6 sm:w-auto">
                  Ver plataforma global
                </Button>
              </Link>
            </div>

            <div className="mt-9 grid gap-3 sm:grid-cols-3">
              {trustIndicators.map((item)=> (
                <div key={item.label} className="rounded-md border border-white/10 bg-white/[0.06] p-4 backdrop-blur">
                  <div className="text-xs font-bold uppercase text-cyan-200">{item.label}</div>
                  <div className="mt-2 text-sm font-semibold leading-5 text-slate-200">{item.value}</div>
                </div>
              ))}
            </div>
          </div>

          <div className="relative flex min-h-[500px] items-center p-4 sm:p-6 lg:p-8">
            <div className="absolute inset-y-8 left-0 hidden w-px bg-gradient-to-b from-transparent via-white/15 to-transparent lg:block" />
            <div className="w-full">
              <Shield3DScene />
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                {[
                  {label:'RISCO', value:'crítico'},
                  {label:'MODO', value:'MVP seguro'},
                  {label:'DADOS', value:'opt-in'},
                ].map((item)=> (
                  <div key={item.label} className="rounded-md border border-white/10 bg-white/[0.06] p-4 text-white backdrop-blur">
                    <div className="text-xs font-bold uppercase text-slate-400">{item.label}</div>
                    <div className="mt-2 text-lg font-black">{item.value}</div>
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="guardian-motion-in grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
        {productPillars.map((pillar)=> (
          <Card key={pillar.title} className="p-5">
            <div className="flex h-10 w-10 items-center justify-center rounded-md bg-slate-950 text-sm font-black text-white">
              {pillar.title.slice(0, 1)}
            </div>
            <h2 className="mt-5 text-lg font-black text-slate-950">{pillar.title}</h2>
            <p className="mt-3 text-sm font-semibold leading-6 text-slate-600">{pillar.body}</p>
          </Card>
        ))}
      </section>

      <div className="guardian-motion-in">
        <AttackGlobe3D />
      </div>

      <section className="guardian-motion-in grid gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <div className="guardian-panel rounded-md p-6 text-slate-950 sm:p-8">
          <div className="text-xs font-bold uppercase text-slate-500">Modelo operacional</div>
          <h2 className="guardian-text-balance mt-3 text-3xl font-black text-slate-950">
            Uma camada de segurança humana, não apenas um analisador.
          </h2>
          <p className="mt-4 text-base font-semibold leading-7 text-slate-600">
            O produto cria uma pausa no intervalo mais perigoso: quando a manipulação vira decisão. O sistema mostra o risco, explica a evidência e orienta a próxima ação.
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link href="/dashboard"><Button className="w-full sm:w-auto">Ver impacto</Button></Link>
            <Link href="/help-network"><Button variant="ghost" className="w-full sm:w-auto">Rede de ajuda</Button></Link>
          </div>
        </div>

        <div className="guardian-panel rounded-md p-5 text-slate-950 sm:p-6">
          <div className="space-y-3">
            {operatingModel.map((step,index)=> (
              <div key={step} className="flex gap-4 rounded-md border border-slate-200/80 bg-white/72 p-4">
                <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md bg-slate-950 text-xs font-black text-white">
                  {index + 1}
                </span>
                <div>
                  <div className="text-sm font-black text-slate-950">{step}</div>
                  <div className="mt-1 text-sm leading-6 text-slate-600">
                    {index === 0 && 'Sem monitoramento automático e sem coleta silenciosa.'}
                    {index === 1 && 'Heurísticas, ML mockado e trace defensivo trabalham juntos.'}
                    {index === 2 && 'A experiência interrompe a pressa antes de pagamento, clique ou envio de senha.'}
                    {index === 3 && 'No MVP, alertas e mensagens são simulados para demonstração segura.'}
                    {index === 4 && 'O avaliador enxerga justificativa, evidência e responsabilidade.'}
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </main>
  )
}
