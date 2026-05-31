"use client"

import React, {useCallback, useEffect, useState} from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppBadge, AppCardTitle, AppSectionTitle} from '@/components/AppPrimitives'
import {riskStatusClass} from '@/lib/appStatus'
import {
  getGuardianConsoleCases,
  getGuardianConsoleStatus,
  patchGuardianCaseStatus,
} from '@/lib/api'
import TrustedCircleEscalationPanel from '@/components/TrustedCircleEscalationPanel'
import AssistedProofSession from '@/components/AssistedProofSession'
import type {AdminCase, AdminCaseStatus, GuardianConsoleStatusResponse} from '@/lib/types'

const statusLabels: Record<AdminCaseStatus, string> = {
  open: 'Aberto',
  reviewing: 'Em análise',
  verified_safe: 'Verificado seguro',
  confirmed_scam: 'Golpe confirmado',
  resolved: 'Resolvido',
  recovery_needed: 'Recovery necessário',
}

const categoryLabels: Record<string, string> = {
  golpe_pix: 'Golpe Pix',
  link_suspeito: 'Link suspeito',
  codigo_senha: 'Código / senha',
  falso_banco: 'Falso banco',
  risco_baixo: 'Risco baixo',
  generico: 'Genérico',
}

function formatTime(iso:string){
  try{
    return new Date(iso).toLocaleString('pt-BR', {dateStyle: 'short', timeStyle: 'short'})
  }catch{
    return iso
  }
}

export default function GuardianAdminConsole(){
  const [consoleStatus,setConsoleStatus]=useState<GuardianConsoleStatusResponse | null>(null)
  const [cases,setCases]=useState<AdminCase[]>([])
  const [selectedId,setSelectedId]=useState<string | null>(null)
  const [selected,setSelected]=useState<AdminCase | null>(null)
  const [loading,setLoading]=useState(true)
  const [updating,setUpdating]=useState(false)
  const [error,setError]=useState('')

  const loadCases = useCallback(async ()=>{
    setLoading(true)
    setError('')
    try{
      const [status, list] = await Promise.all([
        getGuardianConsoleStatus(),
        getGuardianConsoleCases(),
      ])
      setConsoleStatus(status)
      setCases(list.cases)
      const firstId = list.cases[0]?.case_id ?? null
      setSelectedId(prev=> prev && list.cases.some(item=>item.case_id === prev) ? prev : firstId)
    }catch{
      setError('Não foi possível carregar os casos do Guardian Console.')
    }finally{
      setLoading(false)
    }
  },[])

  useEffect(()=>{
    loadCases()
  },[loadCases])

  useEffect(()=>{
    if(!selectedId){
      setSelected(null)
      return
    }
    const match = cases.find(item=>item.case_id === selectedId)
    setSelected(match ?? null)
  },[cases, selectedId])

  async function updateStatus(status:AdminCaseStatus){
    if(!selected) return
    setUpdating(true)
    setError('')
    try{
      const updated = await patchGuardianCaseStatus(selected.case_id, status)
      setCases(prev=>prev.map(item=>item.case_id === updated.case_id ? updated : item))
      setSelected(updated)
    }catch{
      setError('Não foi possível atualizar o status do caso.')
    }finally{
      setUpdating(false)
    }
  }

  return (
    <div className="space-y-6">
      <div className="grid gap-4 sm:grid-cols-3">
        <Card>
          <div className="app-label">Modo</div>
          <p className="mt-2 text-lg font-semibold text-white">{consoleStatus?.mode || '—'}</p>
        </Card>
        <Card>
          <div className="app-label">Casos na fila</div>
          <p className="mt-2 text-lg font-semibold text-white">{consoleStatus?.case_count ?? cases.length}</p>
        </Card>
        <Card>
          <div className="app-label">Notificações</div>
          <p className="mt-2 text-sm text-slate-300">
            {consoleStatus?.notifications_enabled ? 'Ativas' : 'Simuladas (sem envio real)'}
          </p>
        </Card>
      </div>

      {consoleStatus?.__mock && (
        <p className="app-muted-text text-sm">Modo demonstração local — dados mock do console.</p>
      )}
      {error && <p className="text-sm font-medium text-amber-200">{error}</p>}

      <div className="grid gap-6 xl:grid-cols-[minmax(280px,0.95fr)_minmax(0,1.35fr)]">
        <Card className="p-0 overflow-hidden">
          <div className="border-b border-white/10 px-4 py-3 sm:px-5">
            <AppSectionTitle className="text-lg">Fila de casos</AppSectionTitle>
            <p className="app-muted-text mt-1 text-sm">Caso recebido pelo canal simples</p>
          </div>
          <div className="max-h-[520px] overflow-y-auto p-2">
            {loading && <p className="app-muted-text p-3 text-sm">Carregando casos...</p>}
            {!loading && cases.length === 0 && (
              <p className="app-muted-text p-3 text-sm">Nenhum caso na fila.</p>
            )}
            {cases.map(item=> (
              <button
                key={item.case_id}
                type="button"
                onClick={()=>setSelectedId(item.case_id)}
                className={`mb-2 w-full rounded-md border p-3 text-left transition ${
                  selectedId === item.case_id
                    ? 'border-cyan-400/40 bg-cyan-950/25'
                    : 'border-white/10 bg-slate-950/30 hover:border-white/20'
                }`}
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="text-sm font-semibold text-white">{item.protected_person_alias}</div>
                    <div className="app-muted-text mt-0.5 text-xs">{categoryLabels[item.scam_category] || item.scam_category}</div>
                  </div>
                  <span className={riskStatusClass(item.risk_level)}>{item.risk_level}</span>
                </div>
                <div className="mt-2 flex flex-wrap gap-2 text-xs text-slate-400">
                  <span>{statusLabels[item.status]}</span>
                  <span>·</span>
                  <span>{item.source_channel}</span>
                  <span>·</span>
                  <span>{formatTime(item.updated_at)}</span>
                </div>
                {item.trust_lock_status === 'recommended' && (
                  <div className="mt-2">
                    <AppBadge className="app-badge-accent">Pausa protetiva</AppBadge>
                  </div>
                )}
              </button>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          {selected ? (
            <>
              <Card>
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="app-label">Detalhe do caso · {selected.case_id}</div>
                    <AppCardTitle className="mt-2 text-xl">
                      {selected.protected_person_alias} → responsável {selected.guardian_alias}
                    </AppCardTitle>
                    <p className="app-muted-text mt-2 text-sm">
                      Status do caso: <span className="text-slate-200">{statusLabels[selected.status]}</span>
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <span className={riskStatusClass(selected.risk_level)}>Risco {selected.risk_level}</span>
                    <AppBadge>Score {selected.risk_score}</AppBadge>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 sm:grid-cols-2">
                  <div className="app-action-panel">
                    <div className="app-label">Resumo recebido</div>
                    <p className="app-body-text mt-2">{selected.received_content_summary}</p>
                  </div>
                  <div className="app-action-panel">
                    <div className="app-label">Resposta à pessoa protegida</div>
                    <p className="app-body-text mt-2">
                      {selected.protected_person_short_reply || 'Resposta curta não registrada neste caso.'}
                    </p>
                  </div>
                </div>

                <div className="mt-4 app-action-panel">
                  <div className="app-label">Ação recomendada</div>
                  <p className="mt-2 text-base font-medium text-emerald-100">{selected.recommended_action}</p>
                </div>

                <div className="mt-4 app-action-panel">
                  <div className="app-label">Decisão do agente</div>
                  <p className="app-body-text mt-2">{selected.agent_decision}</p>
                </div>

                <div className="mt-4">
                  <div className="app-label">Sinais detectados</div>
                  <div className="mt-2 flex flex-wrap gap-2">
                    {selected.detected_signals.map(signal=> (
                      <AppBadge key={signal}>{signal.replace(/_/g, ' ')}</AppBadge>
                    ))}
                  </div>
                </div>
              </Card>

              <TrustedCircleEscalationPanel
                caseItem={selected}
                onCaseUpdated={updated=>{
                  setCases(prev=>prev.map(item=>item.case_id === updated.case_id ? updated : item))
                  setSelected(updated)
                }}
              />

              <AssistedProofSession
                caseItem={selected}
                trustedCircleActive={
                  selected.trusted_circle_status === 'simulated_notified' ||
                  selected.trusted_circle_status === 'notified'
                }
                onCaseUpdated={updated=>{
                  setCases(prev=>prev.map(item=>item.case_id === updated.case_id ? updated : item))
                  setSelected(updated)
                }}
              />

              <Card>
                <div className="app-label">Trilha da decisão</div>
                <ol className="guardian-operational-timeline mt-4">
                  {selected.agent_decision_trace.map((step,index)=> (
                    <li key={`${step.step}-${index}`} className="guardian-timeline-item">
                      <span className="guardian-timeline-index">{String(index + 1).padStart(2,'0')}</span>
                      <div>
                        <div className="text-sm font-semibold text-white">{step.step}</div>
                        <p className="mt-1 text-sm leading-6 text-slate-400">{step.detail}</p>
                      </div>
                    </li>
                  ))}
                </ol>
              </Card>

              <Card>
                <div className="app-label">Ações do responsável</div>
                <p className="app-muted-text mt-2 text-sm">
                  Operação simulada — sem envio real de mensagens ou notificações.
                </p>
                <div className="mt-4 grid gap-2 sm:grid-cols-2">
                  <Button disabled={updating} variant="ghost" className="h-11" onClick={()=>updateStatus('reviewing')}>
                    Marcar em análise
                  </Button>
                  <Button disabled={updating} variant="ghost" className="h-11" onClick={()=>updateStatus('verified_safe')}>
                    Verificação segura
                  </Button>
                  <Button disabled={updating} className="h-11" onClick={()=>updateStatus('confirmed_scam')}>
                    Golpe confirmado
                  </Button>
                  <Button disabled={updating} variant="ghost" className="h-11" onClick={()=>updateStatus('recovery_needed')}>
                    Mover para Recovery
                  </Button>
                  <Link href="/recovery" className="sm:col-span-1">
                    <Button variant="ghost" className="h-11 w-full">Abrir Recovery Mode</Button>
                  </Link>
                  <Link href="/report" className="sm:col-span-1">
                    <Button variant="ghost" className="h-11 w-full">Gerar relatório</Button>
                  </Link>
                  <Link href="/report" className="sm:col-span-2">
                    <Button variant="ghost" className="h-11 w-full">Ver relatório após verificação</Button>
                  </Link>
                  <Button disabled={updating} variant="ghost" className="h-11 sm:col-span-2" onClick={()=>updateStatus('resolved')}>
                    Marcar como resolvido
                  </Button>
                </div>
              </Card>

              <div className="grid gap-3 sm:grid-cols-2 xl:grid-cols-4">
                <Card className="!p-4">
                  <div className="app-label">Trust Lock</div>
                  <p className="mt-2 text-sm text-slate-200">{selected.trust_lock_status}</p>
                </Card>
                <Card className="!p-4">
                  <div className="app-label">Círculo de confiança</div>
                  <p className="mt-2 text-sm text-slate-200">
                    {selected.trusted_circle_status === 'simulated_notified'
                      ? 'Escalonamento simulado'
                      : selected.trusted_circle_status}
                  </p>
                </Card>
                <Card className="!p-4">
                  <div className="app-label">Verificação segura</div>
                  <p className="mt-2 text-sm text-slate-200">{selected.proof_of_trust_status}</p>
                </Card>
                <Card className="!p-4">
                  <div className="app-label">Recovery</div>
                  <p className="mt-2 text-sm text-slate-200">{selected.recovery_status}</p>
                </Card>
              </div>
            </>
          ) : (
            <Card>
              <p className="app-muted-text">Selecione um caso na fila para ver detalhes operacionais.</p>
            </Card>
          )}
        </div>
      </div>

      <Card className="border-dashed border-white/15">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <p className="app-body-text text-sm">{consoleStatus?.demo_note}</p>
          <div className="flex gap-2">
            <Link href="/chatbot-demo">
              <Button variant="ghost" className="h-10">Ver canal simples</Button>
            </Link>
            <Button variant="ghost" className="h-10" onClick={loadCases}>
              Atualizar fila
            </Button>
          </div>
        </div>
      </Card>
    </div>
  )
}
