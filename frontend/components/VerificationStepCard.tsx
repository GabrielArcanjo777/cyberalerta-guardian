"use client"

import React from 'react'
import {AppBadge} from '@/components/AppPrimitives'
import type {ProofTrustStepItem} from '@/lib/types'

const statusLabel: Record<ProofTrustStepItem['status'], string> = {
  pending: 'Pendente',
  completed: 'Concluído',
  skipped: 'Ignorado',
}

export default function VerificationStepCard({
  step,
  isCurrent,
  children,
}:{
  step: ProofTrustStepItem
  isCurrent?: boolean
  children?: React.ReactNode
}){
  return (
    <div
      className={`rounded-md border p-4 transition ${
        isCurrent
          ? 'border-cyan-400/35 bg-cyan-950/20'
          : step.status === 'completed'
            ? 'border-emerald-400/20 bg-emerald-950/15'
            : 'border-white/10 bg-slate-950/30'
      }`}
    >
      <div className="flex flex-wrap items-start justify-between gap-2">
        <div>
          <div className="text-sm font-semibold text-white">{step.title}</div>
          {step.guidance && (
            <p className="mt-2 text-sm leading-6 text-slate-400">{step.guidance}</p>
          )}
        </div>
        <AppBadge
          className={
            step.status === 'completed'
              ? 'border-emerald-400/30 bg-emerald-950/30 text-emerald-100'
              : isCurrent
                ? 'app-badge-accent'
                : ''
          }
        >
          {statusLabel[step.status]}
        </AppBadge>
      </div>
      {step.note && (
        <p className="mt-3 text-sm text-slate-300">
          <span className="font-medium text-slate-200">Nota do responsável:</span> {step.note}
        </p>
      )}
      {children && <div className="mt-4">{children}</div>}
    </div>
  )
}
