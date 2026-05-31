import React from 'react'
import type {AIMode} from '@/lib/types'

export default function AIModeIndicator({mode}:{mode?:AIMode}){
  if(!mode) return null

  const label = mode.use_llm ? 'Modo de análise: IA assistida' : 'Modo de análise: Heurístico'

  return (
    <div className="flex flex-col gap-2 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 sm:flex-row sm:items-center sm:justify-between">
      <div>
        <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">Analysis mode</div>
        <div className="mt-1 text-sm font-black text-slate-950">{label}</div>
      </div>
      <div className="flex flex-wrap gap-2 text-[11px] font-bold uppercase tracking-wide">
        <span className="rounded border border-slate-200 bg-white px-3 py-1 text-slate-600">provider: {mode.provider}</span>
        <span className="rounded border border-emerald-200 bg-emerald-50 px-3 py-1 text-emerald-700">SafetyPolicy {mode.safety_policy}</span>
        {mode.fallback_enabled && (
          <span className="rounded border border-slate-200 bg-white px-3 py-1 text-slate-600">fallback ativo</span>
        )}
      </div>
    </div>
  )
}
