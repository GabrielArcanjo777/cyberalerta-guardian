import React from 'react'
import Card from '@/components/Card'

type TraceItem = {
  agent: string
  input_summary: string
  decision: string
  confidence: number
  evidence: string[]
  next_action: string
}

type DecisionLedger = {
  final_decision: string
  decision_reason: string
  safety_level: string
  escalation_required: boolean
  audit_summary: string
}

function formatConfidence(value:number){
  const normalized = value <= 1 ? value * 100 : value
  return Math.round(Math.max(0, Math.min(normalized, 100)))
}

function levelClass(level:string){
  if(level === 'critical') return 'border-red-200 bg-red-50 text-red-700'
  if(level === 'high') return 'border-amber-200 bg-amber-50 text-amber-700'
  if(level === 'medium') return 'border-sky-200 bg-sky-50 text-sky-700'
  return 'border-emerald-200 bg-emerald-50 text-emerald-700'
}

export default function AgentDecisionTrace({items, decisionLedger}:{items:TraceItem[],decisionLedger?:DecisionLedger}){
  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-slate-200/80 bg-slate-950 px-5 py-5 text-white sm:px-6">
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Agent Decision Trace</div>
          <h3 className="mt-2 text-xl font-bold tracking-tight text-white">Linha do tempo auditavel</h3>
          <p className="mt-2 max-w-2xl text-sm leading-6 text-slate-300">
            Cada agente registra o que recebeu, a decisao tomada, as evidencias defensivas e o proximo passo.
          </p>
        </div>
        <span className="rounded border border-white/10 bg-white/[0.08] px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-200">
          {items.length} agentes
        </span>
      </div>
      </div>

      <div className="space-y-5 p-5 sm:p-6">
        {items.map((item,index)=> {
          const confidence = formatConfidence(item.confidence)

          return (
            <div key={`${item.agent}-${index}`} className="relative pl-8">
              {index < items.length - 1 && <span className="absolute bottom-[-1.25rem] left-[9px] top-5 w-px bg-gradient-to-b from-cyan-300 via-slate-300 to-slate-200" />}
              <span className="absolute left-0 top-1 flex h-5 w-5 items-center justify-center rounded-full border border-cyan-200 bg-white shadow-[0_0_0_4px_rgba(14,165,233,0.1)]">
                <span className="h-2 w-2 rounded-full bg-cyan-500" />
              </span>

              <div className="rounded-lg border border-slate-200/80 bg-white/[0.82] p-4 shadow-[0_12px_34px_rgba(15,23,42,0.07)] backdrop-blur">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="inline-flex rounded border border-slate-200 bg-slate-50 px-2.5 py-1 text-xs font-bold uppercase tracking-wide text-slate-500">Step {index + 1}</div>
                    <h4 className="mt-1 text-base font-black tracking-tight text-slate-950">{item.agent}</h4>
                    <p className="mt-2 text-sm leading-6 text-slate-600">{item.input_summary}</p>
                  </div>
                  <div className="min-w-[132px] rounded-lg border border-slate-200 bg-slate-50/90 px-3 py-2">
                    <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Confianca</div>
                    <div className="mt-1 flex items-baseline gap-1">
                      <span className="text-2xl font-black text-slate-950">{confidence}</span>
                      <span className="text-xs font-bold text-slate-500">%</span>
                    </div>
                    <div className="mt-2 h-1.5 overflow-hidden rounded-full bg-slate-200">
                      <div className="h-full rounded-full bg-gradient-to-r from-cyan-500 to-slate-950" style={{width: `${confidence}%`}} />
                    </div>
                  </div>
                </div>

                <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50/90 p-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Decisao</div>
                  <p className="mt-2 text-sm font-bold leading-6 text-slate-900">{item.decision}</p>
                </div>

                <div className="mt-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Evidencias encontradas</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {item.evidence.map((evidence,evidenceIndex)=> (
                      <span key={`${evidence}-${evidenceIndex}`} className="rounded border border-slate-200 bg-white/[0.85] px-3 py-1 text-xs font-semibold text-slate-700 shadow-sm">
                        {evidence}
                      </span>
                    ))}
                  </div>
                </div>

                <div className="mt-4 flex items-center gap-3 rounded-lg border border-cyan-200 bg-cyan-50/90 px-4 py-3">
                  <span className="h-2.5 w-2.5 shrink-0 rounded-full bg-cyan-500" />
                  <div>
                    <div className="text-xs font-bold uppercase tracking-wide text-cyan-700">Proxima acao</div>
                    <p className="mt-1 text-sm font-semibold leading-5 text-slate-700">{item.next_action}</p>
                  </div>
                </div>
              </div>
            </div>
          )
        })}
      </div>

      {decisionLedger && (
        <div className="mx-5 mb-5 rounded-lg border border-slate-800 bg-slate-950 p-5 text-white sm:mx-6 sm:mb-6">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Decision Ledger</div>
              <h4 className="mt-2 text-2xl font-black tracking-tight">{decisionLedger.final_decision}</h4>
            </div>
            <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${levelClass(decisionLedger.safety_level)}`}>
              {decisionLedger.safety_level}
            </span>
          </div>

          <div className="mt-5 grid gap-3 lg:grid-cols-2">
            <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
              <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Motivo da decisao</div>
              <p className="mt-2 text-sm leading-6 text-slate-200">{decisionLedger.decision_reason}</p>
            </div>
            <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
              <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Escalonamento</div>
              <p className="mt-2 text-sm font-semibold leading-6 text-slate-200">
                {decisionLedger.escalation_required ? 'Contato de confianca deve ser acionado.' : 'Apenas monitoramento preventivo.'}
              </p>
            </div>
          </div>

          <div className="mt-3 rounded-lg border border-white/10 bg-white/[0.04] p-4">
            <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Resumo auditavel</div>
            <p className="mt-2 text-sm leading-6 text-slate-200">{decisionLedger.audit_summary}</p>
          </div>
        </div>
      )}
    </Card>
  )
}
