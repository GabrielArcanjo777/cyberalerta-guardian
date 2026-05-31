import React from 'react'

export default function RiskScore({score,level}:{score:number,level:string}){
  const normalized = Math.max(0, Math.min(Number(score) || 0, 100))
  const tone = level === 'critical'
    ? 'border-red-200 bg-red-50 text-red-700'
    : level === 'high'
      ? 'border-amber-200 bg-amber-50 text-amber-700'
      : 'border-emerald-200 bg-emerald-50 text-emerald-700'
  const bar = level === 'critical' ? 'bg-red-600' : level === 'high' ? 'bg-amber-500' : 'bg-emerald-500'

  return (
    <div className={`rounded-lg border p-5 shadow-[0_12px_32px_rgba(15,23,42,0.06)] ${tone}`}>
      <div className="flex items-start justify-between gap-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Risk Score</div>
          <div className="mt-3 flex items-baseline gap-2">
            <span className="text-5xl font-black tracking-tight text-slate-950">{normalized}</span>
            <span className="text-sm font-bold text-slate-500">/100</span>
          </div>
        </div>
        <span className="rounded border border-current px-3 py-1 text-xs font-bold uppercase">{level}</span>
      </div>
      <div className="mt-5 h-2 overflow-hidden rounded-full bg-white/80">
        <div className={`h-full rounded-full ${bar}`} style={{width: `${normalized}%`}} />
      </div>
    </div>
  )
}
