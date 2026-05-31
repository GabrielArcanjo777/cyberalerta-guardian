import React from 'react'
import Card from '@/components/Card'

export default function TrustEvidenceCard({confidence,evidence}:{confidence:number,evidence:string[]}){
  const normalized = Math.max(0, Math.min(Number(confidence) || 0, 100))

  return (
    <Card>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Trust Evidence</div>
          <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Sinais que sustentam a decisao</h3>
        </div>
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 px-4 py-3 text-right">
          <div className="text-2xl font-black text-emerald-700">{normalized}%</div>
          <div className="text-xs font-semibold uppercase tracking-wide text-emerald-700">confidence</div>
        </div>
      </div>

      <div className="mt-5 h-2 overflow-hidden rounded-full bg-slate-100">
        <div className="h-full rounded-full bg-emerald-500" style={{width: `${normalized}%`}} />
      </div>

      <div className="mt-5 grid gap-3 sm:grid-cols-2">
        {evidence.map((item,index)=> (
          <div key={index} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="flex items-start gap-3">
              <span className="mt-1 h-2.5 w-2.5 shrink-0 rounded-full bg-emerald-500" />
              <p className="text-sm font-medium leading-5 text-slate-700">{item}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
