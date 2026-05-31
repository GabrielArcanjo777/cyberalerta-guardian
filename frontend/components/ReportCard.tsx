import React from 'react'
import Card from '@/components/Card'

export default function ReportCard({report}:{report:{title:string,summary:string,agent_decision:string,recommended_next_step:string}}){
  const sections = [
    {label: 'Resumo', value: report.summary},
    {label: 'Decisao do agente', value: report.agent_decision},
    {label: 'Proximo passo', value: report.recommended_next_step},
  ]

  return (
    <Card>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Report</div>
          <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">{report.title}</h3>
        </div>
        <span className="rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
          generated
        </span>
      </div>

      <div className="mt-5 grid gap-3">
        {sections.map((section)=> (
          <div key={section.label} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="text-xs font-bold uppercase tracking-wide text-slate-400">{section.label}</div>
            <p className="mt-2 text-sm leading-6 text-slate-700">{section.value}</p>
          </div>
        ))}
      </div>
    </Card>
  )
}
