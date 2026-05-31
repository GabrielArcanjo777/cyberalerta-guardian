"use client"

import React from 'react'
import Card from '@/components/Card'
import Button from '@/components/Button'
import type {TrustedCircleAlert as TrustedCircleAlertModel} from '@/lib/types'

export default function TrustedCircleAlert({
  alert,
  onOpenConsole,
}:{alert:TrustedCircleAlertModel,onOpenConsole?:()=>void}){
  if(!alert.should_alert) return null

  return (
    <Card className="border-amber-200 bg-amber-50">
      <div className="flex items-start gap-3">
        <span className="mt-1 h-3 w-3 shrink-0 rounded-full bg-amber-500 shadow-[0_0_14px_rgba(245,158,11,0.65)]" />
        <div className="min-w-0 flex-1">
          <div className="text-sm font-bold uppercase tracking-wide text-amber-800">Trusted Circle Alert</div>
          <p className="mt-2 text-sm leading-6 text-slate-700">{alert.risk_summary}</p>
          <div className="mt-3 grid gap-2 text-sm">
            <div className="font-bold text-amber-900">Contato: {alert.contact_name} ({alert.relationship})</div>
            <div className="font-semibold text-slate-700">Urgencia: {alert.urgency}</div>
          </div>
          {onOpenConsole && (
            <Button onClick={onOpenConsole} className="mt-4 h-11 w-full">
              Abrir Family Console
            </Button>
          )}
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-amber-800">
            Alerta simulado no MVP
          </p>
        </div>
      </div>
    </Card>
  )
}
