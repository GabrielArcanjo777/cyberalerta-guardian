"use client"

import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import Shield3DScene from '@/components/Shield3DScene'
import AttackGlobe3D from '@/components/AttackGlobe3D'
import GuardianInterventionConsole from '@/components/GuardianInterventionConsole'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

const trustIndicators = [
  {label: 'Pausa ativa', value: 'interrompe a decisão no momento de maior pressão'},
  {label: 'Demonstração segura', value: 'fluxos simulados sem envio real de mensagens'},
  {label: 'Privacidade por consentimento', value: 'a pessoa escolhe o que compartilhar'},
]

const productPillars = [
  {
    title: 'Risco traduzido em ação',
    body: 'O Guardian transforma uma mensagem suspeita em decisão explicável, orientação clara e próxima ação defensiva.',
    meta: 'Camada de decisão',
  },
  {
    title: 'Confiança acionável',
    body: 'O contato de confiança recebe contexto suficiente para agir rápido, sem expor dados além do necessário.',
    meta: 'Ponte familiar',
  },
  {
    title: 'Auditoria para avaliação',
    body: 'Cada agente deixa evidências, confiança e justificativa para mostrar por que o Trust Lock foi ativado.',
    meta: 'IA rastreável',
  },
]

const operatingModel = [
  ['01', 'Entrada voluntária', 'A pessoa cola apenas o trecho que quer revisar.'],
  ['02', 'Classificação defensiva', 'Intent, manipulação e identidade não verificada são analisados.'],
  ['03', 'Pausa protetiva', 'O fluxo interrompe pagamento, clique, senha ou acesso remoto.'],
  ['04', 'Ação humana', 'Família, escola ou instituição recebe um caminho claro de resposta.'],
]

export default function Home(){
  return (
    <PageShell className="space-y-9 pb-16">
      <PageHeader
        eyebrow="Guardian Command Center"
        title="Antes do golpe, uma pausa segura."
        description="O CyberAlerta Guardian transforma mensagens suspeitas em uma decisão rastreável: sinais, risco, pausa protetiva e próxima ação segura para o responsável."
        detail="Uma plataforma defensiva para famílias, instituições e pilotos de hackathon demonstrarem intervenção antes do dano, sem monitoramento automático e sem envio real."
        actions={
          <>
              <Link href="/before-pix">
                <Button className="h-12 w-full !border-cyan-100 !bg-cyan-50 px-6 !text-slate-950 hover:!bg-white sm:w-auto">
                  Testar console de intervenção
                </Button>
              </Link>
            <Link href="/global">
                <Button variant="ghost" className="h-12 w-full px-6 sm:w-auto">
                  Ver visão global
                </Button>
              </Link>
          </>
        }
        aside={
          <div className="space-y-5">
            <Shield3DScene />
            <StatusRail
              items={[
                {label:'Resposta', value:'Pausa ativa', tone:'warn'},
                {label:'Modo', value:'Demo segura', tone:'ready'},
                {label:'Dados', value:'Consentimento', tone:'neutral'},
              ]}
            />
          </div>
        }
      />

      <section className="guardian-motion-in grid items-start gap-6 xl:grid-cols-[0.92fr_1.08fr]">
        <div className="guardian-panel rounded-md p-6 sm:p-8">
          <div className="guardian-kicker">Product signal</div>
          <h2 className="guardian-text-balance mt-5 text-3xl font-semibold leading-tight text-white">
            Não é apenas análise: é uma camada operacional de intervenção.
          </h2>
          <p className="mt-4 text-base leading-7 text-slate-300">
            O Guardian mostra o que foi detectado, por que a decisão deve pausar e qual contato seguro deve ser usado antes de qualquer transferência.
          </p>
          <div className="mt-6 grid gap-px overflow-hidden rounded-md border border-white/10 bg-white/10">
            {trustIndicators.map((item)=> (
              <div key={item.label} className="bg-slate-950/64 p-4">
                <div className="text-sm font-semibold text-white">{item.label}</div>
                <div className="mt-2 text-sm leading-6 text-slate-400">{item.value}</div>
              </div>
            ))}
          </div>
        </div>
        <GuardianInterventionConsole />
      </section>

      <section className="guardian-home-hero guardian-motion-in overflow-hidden rounded-md">
        <div className="relative min-h-[480px] p-4 sm:p-6 lg:p-8">
          <div className="pointer-events-none absolute inset-0 bg-[radial-gradient(circle_at_52%_42%,rgba(14,165,233,0.14),transparent_34%)]" />
          <div className="relative w-full">
              <Shield3DScene />
              <div className="mt-4 grid gap-3 sm:grid-cols-3">
                {[
                  {label:'Resposta', value:'Pausa ativa'},
                  {label:'Modo', value:'Demo segura'},
                  {label:'Dados', value:'Consentimento'},
                ].map((item)=> (
                  <div key={item.label} className="rounded-md border border-white/10 bg-slate-950/58 p-4 text-white">
                    <div className="text-[11px] font-semibold uppercase tracking-[0.14em] text-slate-500">{item.label}</div>
                    <div className="mt-2 text-base font-semibold">{item.value}</div>
                  </div>
                ))}
              </div>
            </div>
        </div>
      </section>

      <section className="guardian-motion-in grid gap-4 lg:grid-cols-[1.12fr_0.88fr]">
        <Card className="guardian-feature-card p-6 sm:p-7">
          <div className="text-sm font-semibold text-cyan-200">Operating layer</div>
          <h2 className="guardian-text-balance mt-4 text-3xl font-semibold leading-tight text-white">
            Proteção antes da ação, não apenas depois do alerta.
          </h2>
          <p className="mt-4 max-w-2xl text-base leading-7 text-slate-300">
            O produto atua no intervalo em que a pressão vira decisão. Ele reduz velocidade, mostra evidências e cria uma ponte de ajuda antes de pagamento, clique ou envio de credencial.
          </p>
        </Card>

        <div className="grid gap-4">
          {productPillars.map((pillar)=> (
            <Card key={pillar.title} className="p-5">
              <div className="flex items-start justify-between gap-4">
                <div>
                  <div className="text-xs font-semibold uppercase tracking-[0.16em] text-slate-500">{pillar.meta}</div>
                  <h3 className="mt-2 text-lg font-semibold text-white">{pillar.title}</h3>
                </div>
                <span className="h-8 w-px bg-cyan-300/30" />
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-300">{pillar.body}</p>
            </Card>
          ))}
        </div>
      </section>

      <div className="guardian-motion-in">
        <AttackGlobe3D />
      </div>

      <section className="guardian-motion-in grid gap-6 lg:grid-cols-[0.82fr_1.18fr]">
        <div className="guardian-panel rounded-md p-6 sm:p-8">
          <div className="text-sm font-semibold text-cyan-200">Modelo operacional</div>
          <h2 className="guardian-text-balance mt-3 text-3xl font-semibold leading-tight text-white">
            Uma camada de segurança humana com rastro técnico.
          </h2>
          <p className="mt-4 text-base leading-7 text-slate-300">
            O Guardian explica por que uma decisão foi pausada e qual resposta humana deve acontecer agora.
          </p>
          <div className="mt-6 flex flex-col gap-3 sm:flex-row">
            <Link href="/dashboard"><Button className="w-full sm:w-auto">Ver impacto</Button></Link>
            <Link href="/help-network"><Button variant="ghost" className="w-full sm:w-auto">Rede de ajuda</Button></Link>
          </div>
        </div>

        <div className="guardian-panel rounded-md p-5 sm:p-6">
          <div className="grid gap-px overflow-hidden rounded-md border border-white/10 bg-white/10">
            {operatingModel.map(([number,title,body])=> (
              <div key={number} className="grid gap-4 bg-slate-950/58 p-4 sm:grid-cols-[3.5rem_1fr]">
                <span className="text-sm font-semibold text-cyan-200">{number}</span>
                <div>
                  <div className="text-base font-semibold text-white">{title}</div>
                  <div className="mt-1 text-sm leading-6 text-slate-400">{body}</div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>
    </PageShell>
  )
}
