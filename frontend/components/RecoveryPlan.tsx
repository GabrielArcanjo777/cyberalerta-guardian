import React from 'react'
import Card from '@/components/Card'
import type {RecoveryResponse} from '@/lib/types'

const priorityOrder = ['immediate','high','medium','preventive']

function priorityClass(priority:string){
  if(priority === 'immediate') return 'border-red-200 bg-red-50 text-red-700'
  if(priority === 'high') return 'border-amber-200 bg-amber-50 text-amber-700'
  if(priority === 'medium') return 'border-sky-200 bg-sky-50 text-sky-700'
  return 'border-emerald-200 bg-emerald-50 text-emerald-700'
}

function severityClass(severity:string){
  if(severity === 'critical') return 'border-red-200 bg-red-50 text-red-700'
  if(severity === 'high') return 'border-amber-200 bg-amber-50 text-amber-700'
  if(severity === 'medium') return 'border-sky-200 bg-sky-50 text-sky-700'
  return 'border-emerald-200 bg-emerald-50 text-emerald-700'
}

function ListSection({title,items,tone}:{title:string,items:string[],tone:string}){
  return (
    <div className={`rounded-lg border p-5 ${tone}`}>
      <div className="text-xs font-bold uppercase tracking-wide opacity-80">{title}</div>
      <ul className="mt-3 space-y-2">
        {items.map((item,index)=> (
          <li key={`${item}-${index}`} className="flex items-start gap-2 text-sm font-medium leading-5 text-slate-700">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-current" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default function RecoveryPlan({result}:{result:RecoveryResponse}){
  const sortedPlan = [...result.recovery_plan].sort((a,b)=> {
    return priorityOrder.indexOf(a.priority) - priorityOrder.indexOf(b.priority)
  })

  return (
    <div className="space-y-5">
      {result.__mock && (
        <Card className="border-sky-200 bg-sky-50">
          <p className="text-sm font-semibold text-sky-800">Modo demonstracao: usando dados simulados.</p>
        </Card>
      )}

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Recovery Mode</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Plano de recuperacao</h2>
            <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-600">{result.summary}</p>
          </div>
          <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${severityClass(result.severity)}`}>
            {result.severity}
          </span>
        </div>
      </Card>

      <div className="grid gap-4 lg:grid-cols-2">
        {sortedPlan.map((step,index)=> (
          <div key={`${step.title}-${index}`} className="rounded-lg border border-slate-200 bg-white p-5 shadow-[0_10px_26px_rgba(15,23,42,0.05)]">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Passo {index + 1}</div>
                <h3 className="mt-2 text-lg font-black tracking-tight text-slate-950">{step.title}</h3>
              </div>
              <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${priorityClass(step.priority)}`}>
                {step.priority}
              </span>
            </div>
            <p className="mt-3 text-sm leading-6 text-slate-600">{step.description}</p>
            <div className="mt-4 inline-flex rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
              {step.category}
            </div>
          </div>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-3">
        <ListSection title="Evidencias para salvar" items={result.evidence_to_save} tone="border-cyan-200 bg-cyan-50 text-cyan-700" />
        <ListSection title="Contas para proteger" items={result.accounts_to_secure} tone="border-emerald-200 bg-emerald-50 text-emerald-700" />
        <ListSection title="O que nao fazer agora" items={result.what_not_to_do} tone="border-red-200 bg-red-50 text-red-700" />
      </div>

      <Card className="border-amber-200 bg-amber-50">
        <div className="text-xs font-bold uppercase tracking-wide text-amber-700">Aviso importante</div>
        <p className="mt-2 text-sm font-semibold leading-6 text-slate-800">{result.disclaimer}</p>
        <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-amber-800">
          Nao substitui banco, autoridades ou orientacao profissional. Nao prometa recuperacao de dinheiro.
        </p>
      </Card>
    </div>
  )
}
