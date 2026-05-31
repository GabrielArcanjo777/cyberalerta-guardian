import React from 'react'
import Card from '@/components/Card'

export default function InterventionPlaybook({playbook}:{playbook:{immediate_action:string,verification:string,family_escalation:string,recovery_fallback:string}}){
  const steps = [
    {label: 'Immediate action', value: playbook.immediate_action, tone: 'border-red-200 bg-red-50 text-red-700'},
    {label: 'Verification', value: playbook.verification, tone: 'border-sky-200 bg-sky-50 text-sky-700'},
    {label: 'Family escalation', value: playbook.family_escalation, tone: 'border-amber-200 bg-amber-50 text-amber-700'},
    {label: 'Recovery fallback', value: playbook.recovery_fallback, tone: 'border-emerald-200 bg-emerald-50 text-emerald-700'},
  ]

  return (
    <Card>
      <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Intervention Playbook</div>
      <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Resposta recomendada</h3>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {steps.map((step)=> (
          <div key={step.label} className={`rounded-lg border p-4 ${step.tone}`}>
            <div className="text-xs font-bold uppercase tracking-wide">{step.label}</div>
            <p className="mt-2 text-sm font-medium leading-5 text-slate-700">{step.value}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}
