import React from 'react'
import Card from '@/components/Card'
import type {MLAnalysis, UrlAnalysis} from '@/lib/types'

export default function MLScamIntelligenceCard({ml, url}:{ml?:MLAnalysis, url?:UrlAnalysis | null}){
  if(!ml) return null

  return (
    <Card>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">ML Scam Intelligence</div>
          <h3 className="mt-2 text-xl font-black tracking-tight text-slate-950">{ml.categoria}</h3>
        </div>
        <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${ml.risco === 'alto' ? 'border-red-200 bg-red-50 text-red-700' : 'border-slate-200 bg-slate-50 text-slate-600'}`}>
          {ml.risco} · {ml.score}
        </span>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Classe</div>
          <div className="mt-1 text-sm font-black text-slate-950">{ml.classe}</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Confianca</div>
          <div className="mt-1 text-sm font-black text-slate-950">{Math.round(ml.confianca * 100)}%</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Motores</div>
          <div className="mt-1 text-sm font-black text-slate-950">{ml.ml_used ? 'ML + regras' : 'regras'}</div>
        </div>
      </div>
      {ml.sinais_detectados?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {ml.sinais_detectados.slice(0, 6).map((signal)=> (
            <span key={signal} className="rounded border border-slate-200 bg-white px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">{signal}</span>
          ))}
        </div>
      )}
      {url && (
        <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
          <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">URL Security</div>
          <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">
            Link analisado com risco {url.risco}, score {url.score}
            {url.brand_impersonation?.brand ? `, possivel imitacao de ${url.brand_impersonation.brand}` : ''}.
          </p>
        </div>
      )}
    </Card>
  )
}
