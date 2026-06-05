"use client"

import React, {useCallback, useState} from 'react'
import Button from '@/components/Button'
import Card from '@/components/Card'
import ProofOfTrustChecklist from '@/components/ProofOfTrustChecklist'
import VerificationStepCard from '@/components/VerificationStepCard'
import {AppBadge} from '@/components/AppPrimitives'
import {
  postAssistedProofSession,
  postAssistedProofSessionStep,
  proofTrustRecommendedForRisk,
} from '@/lib/api'
import type {
  AdminCase,
  AssistedProofFinalDecision,
  AssistedProofSessionResponse,
} from '@/lib/types'

const sessionStatusLabels: Record<string, string> = {
  not_started: 'Não iniciada',
  in_progress: 'Em andamento',
  verified_safe: 'Verificado seguro',
  confirmed_scam: 'Golpe confirmado',
  inconclusive: 'Inconclusivo',
  blocked: 'Pausa mantida',
}

const decisionOptions: Array<{value: AssistedProofFinalDecision, label: string}> = [
  {value: 'verified_safe', label: 'Verificado seguro — liberar com cautela'},
  {value: 'confirmed_scam', label: 'Golpe confirmado — manter pausa'},
  {value: 'inconclusive', label: 'Inconclusivo — manter pausa'},
  {value: 'blocked', label: 'Manter pausa protetiva (bloqueado)'},
]

function suspectedRequestFromCase(caseItem: AdminCase): string {
  if (caseItem.scam_category === 'golpe_pix') {
    return 'Pix urgente com identidade não verificada'
  }
  return caseItem.received_content_summary.slice(0, 120)
}

export default function AssistedProofSession({
  caseItem,
  trustedCircleActive,
  onCaseUpdated,
}:{
  caseItem: AdminCase
  trustedCircleActive?: boolean
  onCaseUpdated?: (updated: AdminCase) => void
}){
  const [session,setSession]=useState<AssistedProofSessionResponse | null>(null)
  const [loading,setLoading]=useState(false)
  const [stepLoading,setStepLoading]=useState(false)
  const [error,setError]=useState('')
  const [note,setNote]=useState('')
  const [decision,setDecision]=useState<AssistedProofFinalDecision>('confirmed_scam')

  const canStart = proofTrustRecommendedForRisk(caseItem.risk_level)

  const startSession = useCallback(async ()=>{
    setLoading(true)
    setError('')
    try{
      const created = await postAssistedProofSession({
        case_id: caseItem.case_id,
        protected_person_alias: caseItem.protected_person_alias,
        guardian_alias: caseItem.guardian_alias,
        risk_level: caseItem.risk_level,
        suspected_request: suspectedRequestFromCase(caseItem),
        trusted_contact_alias: caseItem.guardian_alias,
      })
      setSession(created)
      onCaseUpdated?.({
        ...caseItem,
        proof_of_trust_status: 'in_progress',
      })
    }catch(err){
      if(err instanceof Error && err.message === 'proof-risk-not-allowed'){
        setError('Verificação segura recomendada apenas para risco alto ou crítico.')
      }else{
        setError('Não foi possível iniciar a verificação segura.')
      }
    }finally{
      setLoading(false)
    }
  },[caseItem, onCaseUpdated])

  async function completeCurrentStep(){
    if(!session) return
    const current = session.steps.find(s=>s.id === session.current_step)
    if(!current) return

    if(current.id === 'record_decision' && !decision){
      setError('Selecione uma decisão antes de registrar.')
      return
    }

    setStepLoading(true)
    setError('')
    try{
      const updated = await postAssistedProofSessionStep(session.session_id, {
        step_id: current.id,
        status: 'completed',
        note: note.trim() || undefined,
        final_decision: current.id === 'record_decision' ? decision : undefined,
      })
      setSession(updated)
      setNote('')
      if(updated.status !== 'in_progress'){
        onCaseUpdated?.({
          ...caseItem,
          proof_of_trust_status: 'completed',
          trust_lock_status:
            updated.final_decision === 'verified_safe' ? 'released' : 'recommended',
          status:
            updated.final_decision === 'verified_safe'
              ? 'verified_safe'
              : updated.final_decision === 'confirmed_scam'
                ? 'confirmed_scam'
                : caseItem.status,
        })
      }
    }catch{
      setError('Não foi possível atualizar o passo da verificação.')
    }finally{
      setStepLoading(false)
    }
  }

  const currentStep = session?.steps.find(s=>s.id === session.current_step)

  return (
    <Card className="card-action border-emerald-400/20">
      <div className="flex flex-wrap items-start justify-between gap-3">
        <div>
          <div className="app-label text-emerald-200/90">Verificação segura</div>
          <p className="mt-2 text-sm text-slate-300">
            Protocolo conduzido pelo responsável <strong className="text-white">{caseItem.guardian_alias}</strong> —
            a pessoa protegida não opera checklist complexo.
          </p>
        </div>
        {session && (
          <AppBadge className="border-emerald-400/30 bg-emerald-950/30 text-emerald-100">
            {sessionStatusLabels[session.status] || session.status}
          </AppBadge>
        )}
      </div>

      {trustedCircleActive && (
        <p className="mt-3 text-sm text-amber-200/90">
          Círculo de confiança acionado (simulado) — use canal independente para confirmar antes de liberar qualquer ação.
        </p>
      )}

      <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-slate-500">
        MVP: sem consulta a banco, governo, CPF ou documentos reais
      </p>

      {!session && (
        <>
          {!canStart && (
            <p className="mt-3 text-sm text-slate-400">
              Recomendado para casos de risco alto ou crítico. Este caso está em risco {caseItem.risk_level}.
            </p>
          )}
          {error && <p className="mt-3 text-sm text-amber-200">{error}</p>}
          <Button className="mt-4 h-11" disabled={loading || !canStart} onClick={startSession}>
            Iniciar verificação segura
          </Button>
        </>
      )}

      {session && (
        <div className="mt-5 space-y-5">
          {session.final_decision && (
            <div className="app-action-panel border-emerald-400/15">
              <div className="app-label">Decisão registrada</div>
              <p className="mt-2 font-medium text-white">
                {decisionOptions.find(o=>o.value === session.final_decision)?.label || session.final_decision}
              </p>
            </div>
          )}

          {session.guardian_note && (
            <div className="app-action-panel">
              <div className="app-label">Nota do responsável</div>
              <p className="app-body-text mt-2 whitespace-pre-wrap">{session.guardian_note}</p>
            </div>
          )}

          <ProofOfTrustChecklist
            steps={session.steps}
            currentStepId={session.current_step}
            subtitle={session.demo_note}
          />

          {session.status === 'in_progress' && currentStep && (
            <VerificationStepCard step={currentStep} isCurrent>
              <label className="block text-sm text-slate-400">
                Nota (opcional, sem dados sensíveis)
                <textarea
                  className="mt-2 w-full rounded-md border border-white/10 bg-slate-950/50 p-3 text-sm text-white"
                  rows={2}
                  value={note}
                  onChange={e=>setNote(e.target.value)}
                  placeholder="Ex.: Confirmado pelo telefone salvo que o pedido não era real."
                />
              </label>

              {currentStep.id === 'record_decision' && (
                <fieldset className="mt-4 space-y-2">
                  <legend className="text-sm font-medium text-slate-300">Decisão final</legend>
                  {decisionOptions.map(option=> (
                    <label key={option.value} className="flex cursor-pointer items-start gap-2 text-sm text-slate-300">
                      <input
                        type="radio"
                        name="proof-decision"
                        checked={decision === option.value}
                        onChange={()=>setDecision(option.value)}
                        className="mt-1"
                      />
                      {option.label}
                    </label>
                  ))}
                </fieldset>
              )}

              {error && <p className="mt-3 text-sm text-amber-200">{error}</p>}

              <Button className="mt-4 h-11" disabled={stepLoading} onClick={completeCurrentStep}>
                Concluir passo: {currentStep.title}
              </Button>
            </VerificationStepCard>
          )}

          {session.__mock && (
            <p className="app-muted-text text-xs">Sessão mock local — backend offline.</p>
          )}
        </div>
      )}
    </Card>
  )
}
