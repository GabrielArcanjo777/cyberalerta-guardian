import React from 'react'
import Card from '@/components/Card'

export default function ProofOfTrust({items}:{items:string[]}){
  return (
    <Card>
      <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Proof of Trust</div>
      <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Checklist de verificação</h3>

      <div className="mt-5 grid gap-3">
        {items.map((item,index)=> (
          <div key={`${item}-${index}`} className="flex items-start gap-3 rounded-lg border border-slate-200 bg-white p-4">
            <span className="mt-0.5 flex h-6 w-6 shrink-0 items-center justify-center rounded-md border border-emerald-200 bg-emerald-50">
              <span className="h-2.5 w-2.5 rounded-full bg-emerald-500" />
            </span>
            <div>
              <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Step {index + 1}</div>
              <p className="mt-1 text-sm font-medium leading-5 text-slate-700">{item}</p>
            </div>
          </div>
        ))}
      </div>
    </Card>
  )
}
