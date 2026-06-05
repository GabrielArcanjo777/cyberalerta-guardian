"use client"

import React, {useState} from 'react'
import Link from 'next/link'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {AppCardTitle} from '@/components/AppPrimitives'
import {riskStatusClass} from '@/lib/appStatus'
import type {TrustedCircleAlert} from '@/lib/types'

function urgencyLabel(urgency:string){
  if(urgency === 'critical') return 'crítico'
  if(urgency === 'high') return 'alto'
  if(urgency === 'medium') return 'médio'
  return urgency
}

function statusLabel(status:string){
  if(status === 'contact_completed') return 'contato realizado'
  if(status === 'alert_generated') return 'alerta gerado'
  return status.replace(/_/g, ' ')
}

export default function FamilyConsole({
  alert,
  backHref = '/before-pix',
  backLabel = 'Voltar para análise',
}:{alert:TrustedCircleAlert,backHref?:string,backLabel?:string}){
  const [contactDone,setContactDone]=useState(false)
  const visibleStatus = contactDone ? 'contact_completed' : alert.status

  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-white/10 bg-slate-950/80 px-5 py-5 sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="app-label text-cyan-300/90">Console da família</div>
            <AppCardTitle className="mt-2 text-xl">Ação rápida para contato de confiança</AppCardTitle>
            <p className="app-body-text mt-2">
              Painel simulado para {alert.contact_name} agir antes que {alert.person_at_risk} realize uma ação de risco.
            </p>
          </div>
          <span className={riskStatusClass(alert.urgency)}>
            Urgência {urgencyLabel(alert.urgency)}
          </span>
        </div>
      </div>

      <div className="space-y-4 p-5 sm:p-6">
        <div className="grid gap-4 lg:grid-cols-[1fr_0.86fr]">
          <div className="app-card-highlight border-red-400/30">
            <div className="app-label text-red-300/90">Pessoa em risco</div>
            <div className="mt-3 flex items-center gap-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-md border border-red-400/40 bg-red-950/50 text-lg font-semibold text-red-100">
                {alert.person_at_risk.split(' ').map(part=>part[0]).join('').slice(0,2)}
              </div>
              <div>
                <p className="text-lg font-semibold leading-7 text-white">
                  {alert.person_at_risk} está em risco {urgencyLabel(alert.urgency)}.
                </p>
                <p className="app-muted-text mt-1">
                  Contato: {alert.contact_name} ({alert.relationship})
                </p>
              </div>
            </div>
          </div>

          <div className="app-action-panel">
            <div className="app-label">Status do alerta</div>
            <p className="mt-2 text-lg font-semibold text-white">{statusLabel(visibleStatus)}</p>
            <p className="app-body-text mt-2">
              {alert.is_simulated ? 'MVP simulado: nenhum SMS, WhatsApp ou e-mail real foi enviado.' : 'Alerta real registrado pelo sistema.'}
            </p>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="app-card-compact">
            <div className="app-label">Golpe provável</div>
            <p className="mt-2 text-base font-semibold text-white">{alert.scam_type}</p>
            <p className="app-body-text mt-3">{alert.risk_summary}</p>
          </div>

          <div className="app-callout">
            <div className="app-callout-label">Ação recomendada</div>
            <p className="app-callout-body">{alert.recommended_action}</p>
          </div>
        </div>

        <div className="app-action-panel border-cyan-400/20">
          <div className="app-label text-cyan-200/90">Mensagem sugerida para {alert.contact_name}</div>
          <p className="mt-3 text-base font-medium leading-7 text-slate-200">&ldquo;{alert.suggested_message}&rdquo;</p>
          <p className="app-muted-text mt-3 text-xs uppercase tracking-wide">
            Cópia orientativa. Envio real não implementado neste MVP.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button onClick={()=>setContactDone(true)} className="h-12 flex-1">
            Marcar contato como realizado
          </Button>
          <Link href={backHref} className="flex-1">
            <Button variant="ghost" className="h-12 w-full">{backLabel}</Button>
          </Link>
        </div>
      </div>
    </Card>
  )
}
