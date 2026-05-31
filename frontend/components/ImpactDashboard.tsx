import React from 'react'
import Card from '@/components/Card'
import {
  demonstratedScenarios,
  globalApplicability,
  globalThreatPatterns,
  impactMetrics,
  impactNote,
  manipulationPatterns,
} from '@/lib/impactMockData'

const metricCards = [
  {
    label: 'Decisoes perigosas pausadas',
    value: impactMetrics.dangerous_decisions_paused,
    detail: 'Intervencoes antes da acao',
    tone: 'border-slate-200 bg-white',
  },
  {
    label: 'Tentativas de Pix interrompidas',
    value: impactMetrics.pix_attempts_interrupted,
    detail: 'Pagamentos colocados em pausa',
    tone: 'border-red-200 bg-red-50',
  },
  {
    label: 'Alertas familiares gerados',
    value: impactMetrics.family_alerts_generated,
    detail: 'Trusted Circle acionado',
    tone: 'border-amber-200 bg-amber-50',
  },
  {
    label: 'Planos de recuperacao criados',
    value: impactMetrics.recovery_plans_created,
    detail: 'Orientacao pos-dano',
    tone: 'border-emerald-200 bg-emerald-50',
  },
  {
    label: 'Cenarios analisados',
    value: impactMetrics.scenarios_analyzed,
    detail: 'Simulacoes de risco',
    tone: 'border-slate-200 bg-white',
  },
  {
    label: 'Taticas detectadas',
    value: impactMetrics.manipulation_tactics_detected,
    detail: 'Padroes de manipulacao',
    tone: 'border-slate-200 bg-white',
  },
  {
    label: 'Casos criticos identificados',
    value: impactMetrics.critical_cases_identified,
    detail: 'Risco alto ou critico',
    tone: 'border-red-200 bg-red-50',
  },
  {
    label: 'Acoes em Trust Lock',
    value: impactMetrics.trust_locks_activated,
    detail: 'Bloqueios preventivos',
    tone: 'border-slate-800 bg-slate-950 text-white',
  },
]

const maxPatternCount = Math.max(...manipulationPatterns.map(pattern=>pattern.count))
const maxGlobalPatternCount = Math.max(...globalThreatPatterns.map(pattern=>pattern.count))

export default function ImpactDashboard(){
  return (
    <section className="space-y-6">
      <div className="guardian-panel-dark overflow-hidden rounded-lg text-white">
        <div className="grid lg:grid-cols-[1.18fr_0.82fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="guardian-kicker">
              Impact Dashboard
            </div>
            <h1 className="mt-5 max-w-3xl text-4xl font-black tracking-tight text-white sm:text-5xl">
              Valor de intervencao pre-dano
            </h1>
            <p className="mt-4 max-w-3xl text-base font-semibold leading-7 text-slate-300">
              O CyberAlerta Guardian mostra impacto antes, durante e depois da tentativa de golpe: pausa a decisao, aciona o contato de confianca e gera um plano de recuperacao quando necessario.
            </p>
          </div>
          <div className="border-t border-white/10 bg-white/[0.04] p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">MVP data status</div>
            <p className="mt-4 text-2xl font-black tracking-tight">{impactNote}</p>
            <p className="mt-4 text-sm leading-6 text-slate-300">
              Sem analytics real, sem banco de dados e sem integracao externa nesta sprint.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metricCards.map((metric)=> (
          <div key={metric.label} className={`rounded-lg border p-5 shadow-[0_10px_26px_rgba(15,23,42,0.05)] ${metric.tone}`}>
            <div className="text-xs font-bold uppercase tracking-wide opacity-70">{metric.detail}</div>
            <div className="mt-4 text-5xl font-black tracking-tight">{metric.value}</div>
            <div className="mt-3 text-sm font-bold leading-5">{metric.label}</div>
          </div>
        ))}
      </div>

      <Card>
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Por que isso importa</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">A pausa certa muda o resultado</h2>
          </div>
          <p className="text-base leading-7 text-slate-600">
            Golpes digitais acontecem no intervalo entre a manipulacao e a decisao da vitima. O CyberAlerta Guardian cria uma pausa de seguranca antes do Pix, do clique, do envio de senha ou do compartilhamento de documentos.
          </p>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Padroes de manipulacao</div>
              <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Taticas detectadas na demo</h2>
            </div>
            <span className="rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
              simulado
            </span>
          </div>

          <div className="mt-6 space-y-4">
            {manipulationPatterns.map((pattern)=> {
              const width = `${Math.max(8, Math.round((pattern.count / maxPatternCount) * 100))}%`
              const criticalTone = pattern.label === 'Pedido financeiro' || pattern.label === 'Falso vinculo familiar'

              return (
                <div key={pattern.label}>
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <span className="text-sm font-bold text-slate-700">{pattern.label}</span>
                    <span className="text-sm font-black text-slate-950">{pattern.count}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                    <div className={`h-full rounded-full ${criticalTone ? 'bg-red-500' : 'bg-slate-900'}`} style={{width}} />
                  </div>
                </div>
              )
            })}
          </div>
        </Card>

        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Cenarios demonstrados</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Cobertura do MVP</h2>
          <div className="mt-6 grid gap-3">
            {demonstratedScenarios.map((scenario,index)=> (
              <div key={scenario} className="flex items-center gap-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-lg bg-slate-950 text-xs font-black text-white">
                  {index + 1}
                </span>
                <span className="text-sm font-bold leading-5 text-slate-700">{scenario}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Global applicability</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">From Pix to global pre-damage intervention</h2>
          </div>
          <span className="rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
            MVP strategy
          </span>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {globalApplicability.map((item)=> (
            <div key={item.region} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">{item.region}</div>
              <div className="mt-2 text-sm font-black leading-5 text-slate-950">{item.focus}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Global threat patterns</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Taticas que funcionam em qualquer mercado</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              O trilho de pagamento muda, mas os sinais de manipulacao se repetem: urgencia, autoridade falsa, isolamento, pedido financeiro e credenciais.
            </p>
          </div>
          <div className="space-y-4">
            {globalThreatPatterns.map((pattern)=> {
              const width = `${Math.max(8, Math.round((pattern.count / maxGlobalPatternCount) * 100))}%`
              return (
                <div key={pattern.label}>
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <span className="text-sm font-bold text-slate-700">{pattern.label}</span>
                    <span className="text-sm font-black text-slate-950">{pattern.count}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded-full bg-slate-100">
                    <div className="h-full rounded-full bg-slate-900" style={{width}} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </Card>

      <Card className="border-dashed border-slate-300 bg-slate-50/70">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Transparencia</div>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">{impactNote}</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-bold text-slate-600">
            Sem persistencia real
          </div>
        </div>
      </Card>
    </section>
  )
}
