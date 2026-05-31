"use client"

import React, {useState} from 'react'
import Link from 'next/link'
import Card from '@/components/Card'
import Button from '@/components/Button'
import type {TrustedCircleAlert} from '@/lib/types'

function urgencyClass(urgency:string){
  if(urgency === 'critical') return 'border-red-200 bg-red-50 text-red-700'
  if(urgency === 'high') return 'border-amber-200 bg-amber-50 text-amber-700'
  if(urgency === 'medium') return 'border-sky-200 bg-sky-50 text-sky-700'
  return 'border-emerald-200 bg-emerald-50 text-emerald-700'
}

function statusLabel(status:string){
  if(status === 'contact_completed') return 'contato realizado'
  if(status === 'alert_generated') return 'alerta gerado'
  return status.replace(/_/g, ' ')
}

export default function FamilyConsole({
  alert,
  backHref = '/before-pix',
  backLabel = 'Voltar para analise',
}:{alert:TrustedCircleAlert,backHref?:string,backLabel?:string}){
  const [contactDone,setContactDone]=useState(false)
  const visibleStatus = contactDone ? 'contact_completed' : alert.status

  return (
    <Card className="overflow-hidden p-0">
      <div className="border-b border-slate-200 bg-slate-950 px-5 py-5 text-white sm:px-6">
        <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-cyan-300">Family Console</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight">Acao rapida para contato de confianca</h2>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Painel simulado para {alert.contact_name} agir antes que {alert.person_at_risk} realize uma acao de risco.
            </p>
          </div>
          <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${urgencyClass(alert.urgency)}`}>
            {alert.urgency}
          </span>
        </div>
      </div>

      <div className="space-y-4 p-5 sm:p-6">
        <div className="grid gap-4 lg:grid-cols-[1fr_0.86fr]">
          <div className="rounded-lg border border-red-200 bg-red-50 p-5">
            <div className="text-xs font-bold uppercase tracking-wide text-red-500">Pessoa em risco</div>
            <div className="mt-3 flex items-center gap-4">
              <div className="flex h-14 w-14 shrink-0 items-center justify-center rounded-lg bg-red-600 text-lg font-black text-white">
                {alert.person_at_risk.split(' ').map(part=>part[0]).join('').slice(0,2)}
              </div>
              <div>
                <p className="text-xl font-black tracking-tight text-slate-950">{alert.person_at_risk} esta em risco {alert.urgency}.</p>
                <p className="mt-1 text-sm font-semibold text-red-700">Contato: {alert.contact_name} ({alert.relationship})</p>
              </div>
            </div>
          </div>

          <div className="rounded-lg border border-slate-200 bg-slate-50 p-5">
            <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Status do alerta</div>
            <p className="mt-3 text-lg font-black tracking-tight text-slate-950">{statusLabel(visibleStatus)}</p>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              {alert.is_simulated ? 'MVP simulado: nenhum SMS, WhatsApp ou e-mail real foi enviado.' : 'Alerta real registrado pelo sistema.'}
            </p>
          </div>
        </div>

        <div className="grid gap-4 lg:grid-cols-2">
          <div className="rounded-lg border border-slate-200 bg-white p-5 shadow-sm">
            <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Golpe provavel</div>
            <p className="mt-2 text-lg font-black tracking-tight text-slate-950">{alert.scam_type}</p>
            <p className="mt-3 text-sm leading-6 text-slate-600">{alert.risk_summary}</p>
          </div>

          <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-5">
            <div className="text-xs font-bold uppercase tracking-wide text-emerald-700">Acao recomendada</div>
            <p className="mt-2 text-lg font-black tracking-tight text-slate-950">{alert.recommended_action}</p>
          </div>
        </div>

        <div className="rounded-lg border border-cyan-200 bg-cyan-50 p-5">
          <div className="text-xs font-bold uppercase tracking-wide text-cyan-700">Mensagem sugerida para {alert.contact_name}</div>
          <p className="mt-3 text-base font-semibold leading-7 text-slate-900">"{alert.suggested_message}"</p>
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-cyan-800">
            Copia orientativa. Envio real nao implementado neste MVP.
          </p>
        </div>

        <div className="flex flex-col gap-3 sm:flex-row">
          <Button
            onClick={()=>setContactDone(true)}
            disabled={contactDone}
            className="h-12"
          >
            {contactDone ? 'Contato marcado como realizado' : 'Marcar como contato realizado'}
          </Button>
          <Link href={backHref}>
            <Button variant="ghost" className="h-12 w-full sm:w-auto">{backLabel}</Button>
          </Link>
        </div>
      </div>
    </Card>
  )
}
