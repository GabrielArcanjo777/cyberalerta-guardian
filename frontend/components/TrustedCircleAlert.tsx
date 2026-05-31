"use client"

import React from 'react'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {AppBadge} from '@/components/AppPrimitives'
import type {TrustedCircleAlert as TrustedCircleAlertModel} from '@/lib/types'

export default function TrustedCircleAlert({
  alert,
  onOpenConsole,
}:{alert:TrustedCircleAlertModel,onOpenConsole?:()=>void}){
  if(!alert.should_alert) return null

  return (
    <Card className="border-amber-400/25 bg-amber-950/20">
      <div className="flex items-start gap-3">
        <span className="mt-1 h-3 w-3 shrink-0 rounded-full bg-amber-400 shadow-[0_0_14px_rgba(251,191,36,0.55)]" />
        <div className="min-w-0 flex-1">
          <div className="app-label text-amber-200/90">Círculo de confiança</div>
          <AppBadge className="app-badge-warn mt-2">Escalonamento simulado</AppBadge>
          <p className="mt-3 text-sm leading-6 text-slate-300">{alert.risk_summary}</p>
          <div className="mt-4 grid gap-2 text-sm">
            <div>
              <span className="app-label">Contato confiável</span>
              <p className="mt-1 font-medium text-white">
                {alert.contact_name} ({alert.relationship})
              </p>
            </div>
            {alert.suggested_message && (
              <div className="app-action-panel border-amber-400/15">
                <span className="app-label">Mensagem sugerida</span>
                <p className="mt-2 text-sm font-medium text-amber-50">{alert.suggested_message}</p>
              </div>
            )}
            <p className="text-slate-400">Urgência: {alert.urgency}</p>
          </div>
          {alert.recommended_action && (
            <p className="mt-3 text-sm text-emerald-200/90">
              Verificação segura recomendada: {alert.recommended_action}
            </p>
          )}
          {onOpenConsole && (
            <Button onClick={onOpenConsole} className="mt-4 h-11 w-full">
              Abrir Guardian Console
            </Button>
          )}
          <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-amber-200/80">
            Nenhuma notificação real foi enviada no MVP
          </p>
        </div>
      </div>
    </Card>
  )
}
