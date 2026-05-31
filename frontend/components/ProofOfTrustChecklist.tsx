"use client"

import React from 'react'
import VerificationStepCard from '@/components/VerificationStepCard'
import type {ProofTrustStepItem} from '@/lib/types'

export default function ProofOfTrustChecklist({
  steps,
  currentStepId,
  title = 'Verificação segura',
  subtitle,
}:{
  steps: ProofTrustStepItem[]
  currentStepId?: string
  title?: string
  subtitle?: string
}){
  return (
    <div className="space-y-3">
      <div>
        <div className="app-label text-emerald-200/90">{title}</div>
        {subtitle && <p className="app-muted-text mt-2 text-sm">{subtitle}</p>}
        <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-slate-500">
          Não use o contato suspeito · confirme por canal independente
        </p>
      </div>
      {steps.map(step=> (
        <VerificationStepCard
          key={step.id}
          step={step}
          isCurrent={currentStepId ? step.id === currentStepId : step.status === 'pending'}
        />
      ))}
    </div>
  )
}
