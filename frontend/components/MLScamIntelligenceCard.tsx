import React from 'react'
import Card from '@/components/Card'
import {StatusBadge} from '@/components/AppPrimitives'
import type {MLAnalysis, UrlAnalysis} from '@/lib/types'

export default function MLScamIntelligenceCard({ml, url}:{ml?:MLAnalysis, url?:UrlAnalysis | null}){
  if(!ml) return null

  return (
    <Card className={ml.risco === 'alto' ? 'card-danger' : 'card-evidence'}>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="app-label">ML Scam Intelligence</div>
          <h3 className="app-section-title mt-2">{ml.categoria}</h3>
        </div>
        <StatusBadge tone={ml.risco === 'alto' ? 'danger' : 'neutral'}>
          {ml.risco} · {ml.score}
        </StatusBadge>
      </div>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="app-card-compact">
          <div className="app-label">Classe</div>
          <div className="mt-1 text-sm font-black text-slate-100">{ml.classe}</div>
        </div>
        <div className="app-card-compact">
          <div className="app-label">Confiança</div>
          <div className="mt-1 text-sm font-black text-slate-100">{Math.round(ml.confianca * 100)}%</div>
        </div>
        <div className="app-card-compact">
          <div className="app-label">Motores</div>
          <div className="mt-1 text-sm font-black text-slate-100">{ml.ml_used ? 'ML + regras' : 'regras'}</div>
        </div>
      </div>
      {ml.sinais_detectados?.length > 0 && (
        <div className="mt-4 flex flex-wrap gap-2">
          {ml.sinais_detectados.slice(0, 6).map((signal)=> (
            <StatusBadge key={signal} tone="warning">{signal}</StatusBadge>
          ))}
        </div>
      )}
      {url && (
        <div className="app-action-panel mt-4">
          <div className="app-label">URL Security</div>
          <p className="app-body-text mt-2 text-sm font-semibold">
            Link analisado com risco {url.risco}, score {url.score}
            {url.brand_impersonation?.brand ? `, possível imitação de ${url.brand_impersonation.brand}` : ''}.
          </p>
        </div>
      )}
    </Card>
  )
}
