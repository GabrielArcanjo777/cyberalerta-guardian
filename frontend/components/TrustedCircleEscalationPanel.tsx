"use client"

import React, {useMemo, useState} from 'react'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppBadge} from '@/components/AppPrimitives'
import {escalationRecommendedForRisk, postTrustedCircleEscalate} from '@/lib/api'
import type {AdminCase, TrustedCircleEscalateResponse} from '@/lib/types'

const statusLabels: Record<string, string> = {
  pending: 'Aguardando',
  not_required: 'Não necessário',
  review_suggested: 'Revisão sugerida',
  simulated_notified: 'Escalonamento simulado',
  notified: 'Notificado (demo)',
  resolved: 'Resolvido',
}

function defaultReason(caseItem: AdminCase): string {
  const signals = caseItem.detected_signals.slice(0, 3).join(', ').replace(/_/g, ' ')
  if (caseItem.scam_category === 'golpe_pix') {
    return 'pedido de Pix urgente com identidade não verificada'
  }
  return signals || caseItem.received_content_summary.slice(0, 80)
}

export default function TrustedCircleEscalationPanel({
  caseItem,
  onCaseUpdated,
}:{
  caseItem: AdminCase
  onCaseUpdated?: (updated: AdminCase) => void
}){
  const [escalation,setEscalation]=useState<TrustedCircleEscalateResponse | null>(null)
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState('')

  const canEscalate = useMemo(
    ()=> escalationRecommendedForRisk(caseItem.risk_level),
    [caseItem.risk_level],
  )

  const trustedContacts = useMemo(()=>{
    const base = [caseItem.guardian_alias]
    if(escalation?.trusted_contacts?.length){
      return escalation.trusted_contacts
    }
    return Array.from(new Set(base.filter(Boolean)))
  },[caseItem.guardian_alias, escalation?.trusted_contacts])

  async function handleEscalate(){
    setLoading(true)
    setError('')
    try{
      const result = await postTrustedCircleEscalate({
        case_id: caseItem.case_id,
        risk_level: caseItem.risk_level,
        protected_person_alias: caseItem.protected_person_alias,
        trusted_contacts: trustedContacts,
        reason: defaultReason(caseItem),
      })
      setEscalation(result)
      onCaseUpdated?.({
        ...caseItem,
        trusted_circle_status:
          result.status === 'simulated_notified'
            ? 'simulated_notified'
            : result.status === 'review_suggested'
              ? 'review_suggested'
              : result.status === 'not_escalated'
                ? 'not_required'
                : caseItem.trusted_circle_status,
        proof_of_trust_status: result.proof_of_trust_recommended
          ? 'recommended'
          : caseItem.proof_of_trust_status,
      })
    }catch{
      setError('Não foi possível acionar o círculo de confiança.')
    }finally{
      setLoading(false)
    }
  }

  const displayStatus = escalation?.status || caseItem.trusted_circle_status
  const statusLabel = statusLabels[displayStatus] || displayStatus

  return (
    <Card className="card-risk border-amber-400/20">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="app-label text-amber-200/90">Círculo de confiança</div>
          <p className="mt-2 text-sm text-slate-300">
            Acionamento para contatos de confiança por <strong className="text-white">alias</strong> — sem telefone real.
          </p>
        </div>
        <AppBadge className="app-badge-warn">{statusLabel}</AppBadge>
      </div>

      <div className="mt-4 grid gap-3 sm:grid-cols-2">
        <div className="app-action-panel">
          <div className="app-label">Contatos confiáveis</div>
          <div className="mt-2 flex flex-wrap gap-2">
            {trustedContacts.map(name=> (
              <AppBadge key={name}>{name}</AppBadge>
            ))}
          </div>
        </div>
        <div className="app-action-panel">
          <div className="app-label">Motivo do acionamento</div>
          <p className="app-body-text mt-2">{defaultReason(caseItem)}</p>
        </div>
      </div>

      {(escalation?.message_to_guardian || caseItem.recommended_action) && (
        <div className="mt-4 app-action-panel border-amber-400/15">
          <div className="app-label">Mensagem sugerida</div>
          <p className="mt-2 text-base font-medium leading-7 text-amber-50">
            {escalation?.message_to_guardian ||
              `${caseItem.protected_person_alias}: ${caseItem.recommended_action}`}
          </p>
        </div>
      )}

      {escalation?.proof_of_trust_recommended && (
        <p className="mt-3 text-sm font-medium text-emerald-200/90">
          Verificação segura recomendada (Proof of Trust).
        </p>
      )}

      <p className="mt-4 text-xs font-semibold uppercase tracking-wide text-amber-200/80">
        MVP: nenhuma notificação real foi enviada
      </p>

      {!canEscalate && !escalation && (
        <p className="mt-3 text-sm text-slate-400">
          Risco {caseItem.risk_level}: escalonamento automático do círculo não é recomendado. Use revisão do responsável.
        </p>
      )}

      {error && <p className="mt-3 text-sm text-amber-200">{error}</p>}

      <div className="mt-5 flex flex-wrap gap-2">
        <Button
          className="h-11"
          disabled={loading}
          onClick={handleEscalate}
        >
          {canEscalate ? 'Acionar círculo de confiança' : 'Registrar revisão / simulação'}
        </Button>
        {escalation?.escalation_id && (
          <span className="self-center text-xs text-slate-500">ID: {escalation.escalation_id}</span>
        )}
      </div>

      {escalation?.__mock && (
        <p className="app-muted-text mt-2 text-xs">Resposta mock local — backend offline.</p>
      )}
    </Card>
  )
}
