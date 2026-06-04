import React from 'react'
import Card from '@/components/Card'
import {MetricPanel, PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'
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
    detail: 'Intervenções antes da ação',
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
    label: 'Planos de recuperação criados',
    value: impactMetrics.recovery_plans_created,
    detail: 'Orientação pós-dano',
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
    detail: 'Padrões de manipulação',
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

function metricTone(label:string){
  if(label.includes('Pix') || label.includes('criticos')) return 'risk' as const
  if(label.includes('recuperação') || label.includes('familiares')) return 'safe' as const
  if(label.includes('Trust Lock') || label.includes('pausadas')) return 'cyan' as const
  return 'default' as const
}

export default function ImpactDashboard(){
  return (
    <PageShell>
      <PageHeader
        eyebrow="Impact Dashboard"
        title="Valor de intervenção pré-dano"
        description="O CyberAlerta Guardian mostra impacto antes, durante e depois da tentativa de golpe: pausa a decisão, aciona o contato de confiança e gera um plano de recuperação quando necessário."
        detail="Dados simulados para demonstração do MVP. Sem analytics real, banco de dados ou integração externa nesta sprint."
        aside={
          <div className="space-y-5">
            <div className="text-2xl font-semibold tracking-tight text-white">{impactNote}</div>
            <StatusRail
              items={[
                {label:'Analytics', value:'simulado', tone:'neutral'},
                {label:'Persistencia', value:'sem banco', tone:'ready'},
                {label:'Escopo', value:'MVP demo', tone:'warn'},
              ]}
            />
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        {metricCards.map((metric)=> (
          <MetricPanel key={metric.label} label={metric.label} value={metric.value} detail={metric.detail} tone={metricTone(metric.label)} />
        ))}
      </div>

      <Card className="card-primary">
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Por que isso importa</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">A pausa certa muda o resultado</h2>
          </div>
          <p className="text-base leading-7 text-slate-600">
            Golpes digitais acontecem no intervalo entre a manipulação e a decisão da vítima. O CyberAlerta Guardian cria uma pausa de segurança antes do Pix, do clique, do envio de senha ou do compartilhamento de documentos.
          </p>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card className="card-evidence">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Padrões de manipulação</div>
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

        <Card className="card-muted">
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

      <Card className="card-evidence">
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

      <Card className="card-secondary">
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Global threat patterns</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Taticas que funcionam em qualquer mercado</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              O trilho de pagamento muda, mas os sinais de manipulação se repetem: urgência, autoridade falsa, isolamento, pedido financeiro e credenciais.
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

      <Card className="card-muted border-dashed border-slate-300 bg-slate-50/70">
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
    </PageShell>
  )
}
