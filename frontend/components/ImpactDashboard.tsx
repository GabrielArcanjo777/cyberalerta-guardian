import React from 'react'
import Card from '@/components/Card'
import {StatusBadge} from '@/components/AppPrimitives'
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
    label: 'Decisões perigosas pausadas',
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
    label: 'Cenários analisados',
    value: impactMetrics.scenarios_analyzed,
    detail: 'Simulações de risco',
    tone: 'border-slate-200 bg-white',
  },
  {
    label: 'Táticas detectadas',
    value: impactMetrics.manipulation_tactics_detected,
    detail: 'Padrões de manipulação',
    tone: 'border-slate-200 bg-white',
  },
  {
    label: 'Casos críticos identificados',
    value: impactMetrics.critical_cases_identified,
    detail: 'Risco alto ou critico',
    tone: 'border-red-200 bg-red-50',
  },
  {
    label: 'Ações em Trust Lock',
    value: impactMetrics.trust_locks_activated,
    detail: 'Bloqueios preventivos',
    tone: 'border-slate-800 bg-slate-950 text-white',
  },
]

const maxPatternCount = Math.max(...manipulationPatterns.map(pattern=>pattern.count))
const maxGlobalPatternCount = Math.max(...globalThreatPatterns.map(pattern=>pattern.count))

function metricTone(label:string){
  if(label.includes('Pix') || label.includes('críticos')) return 'risk' as const
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
                {label:'Persistência', value:'sem banco', tone:'ready'},
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

      <Card>
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr] lg:items-center">
          <div>
            <div className="app-label">Por que isso importa</div>
            <h2 className="app-section-title mt-2">A pausa certa muda o resultado</h2>
          </div>
          <p className="app-body-text text-base leading-7">
            Golpes digitais acontecem no intervalo entre a manipulação e a decisão da vítima. O CyberAlerta Guardian cria uma pausa de segurança antes do Pix, do clique, do envio de senha ou do compartilhamento de documentos.
          </p>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <Card>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="app-label">Padrões de manipulação</div>
              <h2 className="app-section-title mt-2">Táticas detectadas na demo</h2>
            </div>
            <StatusBadge tone="warning">Simulado</StatusBadge>
          </div>

          <div className="mt-6 space-y-4">
            {manipulationPatterns.map((pattern)=> {
              const width = `${Math.max(8, Math.round((pattern.count / maxPatternCount) * 100))}%`
              const criticalTone = pattern.label === 'Pedido financeiro' || pattern.label === 'Falso vínculo familiar'

              return (
                <div key={pattern.label}>
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <span className="text-sm font-bold text-slate-200">{pattern.label}</span>
                    <span className="text-sm font-black text-white">{pattern.count}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded bg-slate-950/80 ring-1 ring-white/10">
                    <div className={`h-full ${criticalTone ? 'bg-red-500' : 'bg-cyan-300'}`} style={{width}} />
                  </div>
                </div>
              )
            })}
          </div>
        </Card>

        <Card>
          <div className="app-label">Cenários demonstrados</div>
          <h2 className="app-section-title mt-2">Cobertura do MVP</h2>
          <div className="mt-6 grid gap-3">
            {demonstratedScenarios.map((scenario,index)=> (
              <div key={scenario} className="app-card-row flex-row items-center">
                <span className="flex h-8 w-8 shrink-0 items-center justify-center rounded-md border border-cyan-300/30 bg-cyan-300/10 text-xs font-black text-cyan-100">
                  {index + 1}
                </span>
                <span className="text-sm font-bold leading-5 text-slate-200">{scenario}</span>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="app-label">Aplicabilidade global</div>
            <h2 className="app-section-title mt-2">Do Pix à intervenção global pré-dano</h2>
          </div>
          <StatusBadge tone="locked">Estratégia MVP</StatusBadge>
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2 xl:grid-cols-3">
          {globalApplicability.map((item)=> (
            <div key={item.region} className="app-card-compact">
              <div className="app-label">{item.region}</div>
              <div className="mt-2 text-sm font-black leading-5 text-slate-100">{item.focus}</div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <div className="app-label">Padrões globais de ameaça</div>
            <h2 className="app-section-title mt-2">Táticas que funcionam em qualquer mercado</h2>
            <p className="app-body-text mt-3">
              O trilho de pagamento muda, mas os sinais de manipulação se repetem: urgência, autoridade falsa, isolamento, pedido financeiro e credenciais.
            </p>
          </div>
          <div className="space-y-4">
            {globalThreatPatterns.map((pattern)=> {
              const width = `${Math.max(8, Math.round((pattern.count / maxGlobalPatternCount) * 100))}%`
              return (
                <div key={pattern.label}>
                  <div className="mb-2 flex items-center justify-between gap-4">
                    <span className="text-sm font-bold text-slate-200">{pattern.label}</span>
                    <span className="text-sm font-black text-white">{pattern.count}</span>
                  </div>
                  <div className="h-3 overflow-hidden rounded bg-slate-950/80 ring-1 ring-white/10">
                    <div className="h-full bg-cyan-300" style={{width}} />
                  </div>
                </div>
              )
            })}
          </div>
        </div>
      </Card>

      <Card className="border-dashed border-white/20">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="app-label">Transparência</div>
            <p className="app-body-text mt-2 text-sm font-semibold">{impactNote}</p>
          </div>
          <StatusBadge tone="neutral">Sem persistência real</StatusBadge>
        </div>
      </Card>
    </PageShell>
  )
}
