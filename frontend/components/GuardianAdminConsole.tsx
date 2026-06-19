"use client"

import React, {useCallback, useEffect, useState} from 'react'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppBadge, AppCardTitle, AppSectionTitle} from '@/components/AppPrimitives'
import {riskStatusClass} from '@/lib/appStatus'
import {
  getGuardianConsoleRealCase,
  getGuardianConsoleRealCases,
  getGuardianConsoleRealStatus,
  postConsentAccept,
  postConsentBotActivate,
  postConsentBotDeactivate,
  postConsentRevoke,
  postDualBotMockProtectedMessage,
  postGuardianConsoleRealFeedback,
} from '@/lib/api'
import type {
  GuardianConsoleAuditLogView,
  GuardianConsoleRealCaseDetail,
  GuardianConsoleRealCaseSummary,
  GuardianConsoleRealStatusResponse,
  GuardianFeedbackAction,
} from '@/lib/types'

const statusLabels: Record<string, string> = {
  new: 'Novo',
  under_review: 'Em revisao',
  paused: 'Pausado',
  confirmed_scam: 'Golpe confirmado',
  false_alarm: 'Falso positivo',
  resolved: 'Resolvido',
}

const actionLabels: Record<GuardianFeedbackAction, string> = {
  confirm_scam: 'Confirmar golpe',
  false_alarm: 'Falso positivo',
  needs_review: 'Precisa revisar',
  mark_resolved: 'Marcar resolvido',
}

const actionNotes: Record<GuardianFeedbackAction, string> = {
  confirm_scam: 'Responsavel confirmou o risco por canal independente.',
  false_alarm: 'Responsavel marcou este caso como falso positivo.',
  needs_review: 'Responsavel pediu revisao antes de concluir.',
  mark_resolved: 'Responsavel encerrou o caso no console.',
}

function formatTime(iso:string){
  try{
    return new Date(iso).toLocaleString('pt-BR', {dateStyle: 'short', timeStyle: 'short'})
  }catch{
    return iso
  }
}

function deliveryLabel(status?:string | null){
  if(!status) return 'sem status'
  if(status === 'delivered') return 'entregue'
  if(status === 'pending') return 'pendente'
  if(status === 'sent') return 'enviado'
  if(status === 'failed') return 'falhou'
  return status
}

function caseStateLabel(item:GuardianConsoleRealCaseSummary){
  if(item.guardian_confirmed) return 'confirmado'
  if(item.false_positive) return 'falso positivo'
  if(item.resolved) return 'resolvido'
  if(item.alert_delivered) return 'alerta entregue'
  return statusLabels[item.status] || item.status
}

function recurrenceText(recurrence:Record<string, number>){
  const entries = Object.entries(recurrence).filter(([,value])=>value > 0)
  if(entries.length === 0) return 'sem recorrencia registrada'
  return entries
    .map(([key,value])=>`${key.replace(/_/g, ' ')}: ${value}`)
    .join(' · ')
}

function yesNo(value?:boolean | null){
  return value ? 'sim' : 'nao'
}

function auditTarget(entry:GuardianConsoleAuditLogView){
  return `${entry.target_type}:${entry.target_id.slice(0, 18)}`
}

function isFeedbackAction(action:string): action is GuardianFeedbackAction {
  return action in actionLabels
}

export default function GuardianAdminConsole(){
  const [consoleStatus,setConsoleStatus]=useState<GuardianConsoleRealStatusResponse | null>(null)
  const [cases,setCases]=useState<GuardianConsoleRealCaseSummary[]>([])
  const [selectedId,setSelectedId]=useState<string | null>(null)
  const [selected,setSelected]=useState<GuardianConsoleRealCaseDetail | null>(null)
  const [loading,setLoading]=useState(true)
  const [detailLoading,setDetailLoading]=useState(false)
  const [updating,setUpdating]=useState(false)
  const [consentUpdating,setConsentUpdating]=useState(false)
  const [simulating,setSimulating]=useState(false)
  const [error,setError]=useState('')

  const loadConsole = useCallback(async (preferredId?:string | null)=>{
    setLoading(true)
    setError('')
    try{
      const [status, list] = await Promise.all([
        getGuardianConsoleRealStatus(),
        getGuardianConsoleRealCases(),
      ])
      setConsoleStatus(status)
      setCases(list.cases)
      const nextId = preferredId ?? list.cases[0]?.case_id ?? null
      setSelectedId(nextId)
      if(nextId){
        setSelected(await getGuardianConsoleRealCase(nextId))
      }else{
        setSelected(null)
      }
    }catch{
      setError('Nao foi possivel carregar o Guardian Console real. Verifique se o backend local esta ativo.')
      setSelected(null)
    }finally{
      setLoading(false)
    }
  },[])

  const selectCase = useCallback(async (caseId:string)=>{
    setSelectedId(caseId)
    setDetailLoading(true)
    setError('')
    try{
      setSelected(await getGuardianConsoleRealCase(caseId))
    }catch{
      setError('Nao foi possivel carregar o detalhe do caso.')
    }finally{
      setDetailLoading(false)
    }
  },[])

  useEffect(()=>{
    loadConsole()
  },[loadConsole])

  async function createDemoFlow(){
    setSimulating(true)
    setError('')
    try{
      const flow = await postDualBotMockProtectedMessage({
        providerMessageId: `console-ui-${Date.now().toString(36)}`,
        body: 'Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.',
        protected_person_alias: 'Dona Lucia',
        guardian_alias: 'Gabriel',
        guardian_address: '+5511888880001',
      })
      await loadConsole(flow.case_id ?? null)
    }catch{
      setError('Nao foi possivel simular o fluxo local do Dual Bot.')
    }finally{
      setSimulating(false)
    }
  }

  async function submitFeedback(action:GuardianFeedbackAction){
    if(!selected) return
    setUpdating(true)
    setError('')
    try{
      await postGuardianConsoleRealFeedback(selected.case_id, {
        action,
        guardian_alias: selected.guardian_alias || 'Responsavel',
        note: actionNotes[action],
      })
      await loadConsole(selected.case_id)
    }catch{
      setError('Nao foi possivel registrar a acao do responsavel.')
    }finally{
      setUpdating(false)
    }
  }

  async function updateConsent(action:'accept' | 'activate' | 'deactivate' | 'revoke'){
    const protectedPersonId = selected?.protected_person?.protected_person_id || 'demo-protected-person'
    setConsentUpdating(true)
    setError('')
    try{
      if(action === 'accept'){
        await postConsentAccept({
          protected_person_id: protectedPersonId,
          protected_person_alias: selected?.protected_person?.alias || selected?.protected_person_alias || 'Dona Lucia',
          guardian_alias: selected?.responsible_contact?.alias || selected?.guardian_alias || 'Gabriel',
          channel_provider: selected?.channel_status?.provider || consoleStatus?.channel_provider || 'mock',
        })
      }
      if(action === 'activate'){
        await postConsentBotActivate({
          protected_person_id: protectedPersonId,
          reason: 'Bot reativado pelo Console apos verificacao de opt-in.',
        })
      }
      if(action === 'deactivate'){
        await postConsentBotDeactivate({
          protected_person_id: protectedPersonId,
          reason: 'Bot desativado pelo Console sem revogar consentimento.',
        })
      }
      if(action === 'revoke'){
        await postConsentRevoke({
          protected_person_id: protectedPersonId,
          reason: 'Consentimento revogado pelo Console.',
        })
      }
      await loadConsole(selectedId)
    }catch{
      setError('Nao foi possivel atualizar consentimento/opt-in.')
    }finally{
      setConsentUpdating(false)
    }
  }

  const activation = selected?.activation || consoleStatus?.activation
  const consent = selected?.consent || consoleStatus?.consent
  const selectedTimeline = selected?.bot_events?.length ? selected.bot_events : selected?.timeline ?? []
  const selectedActions = selected?.feedback?.available_actions?.filter(isFeedbackAction)

  return (
    <div className="space-y-6">
      <div className="grid gap-4 md:grid-cols-4">
        <Card className="card-muted !p-4">
          <div className="app-label">Canal</div>
          <p className="mt-2 text-lg font-semibold text-white">
            {consoleStatus?.channel_provider || 'mock'}
          </p>
          <p className="app-muted-text mt-1 text-xs">
            {selected?.environment_label || (activation?.simulated ? 'mock local / in-memory' : 'demo controlado')}
          </p>
        </Card>
        <Card className="card-primary !p-4">
          <div className="app-label">Casos</div>
          <p className="mt-2 text-lg font-semibold text-white">{consoleStatus?.case_count ?? cases.length}</p>
          <p className="app-muted-text mt-1 text-xs">{consoleStatus?.open_case_count ?? 0} abertos</p>
        </Card>
        <Card className="card-muted !p-4">
          <div className="app-label">Bot Protegido</div>
          <p className="mt-2 text-sm font-semibold text-white">
            {activation?.protected_bot.active ? 'Ativo' : 'Inativo'}
          </p>
          <p className="app-muted-text mt-1 text-xs">{activation?.protected_bot.last_event || 'aguardando evento'}</p>
        </Card>
        <Card className="card-muted !p-4">
          <div className="app-label">Bot Responsavel</div>
          <p className="mt-2 text-sm font-semibold text-white">
            {activation?.responsible_bot.active ? 'Ativo' : 'Inativo'}
          </p>
          <p className="app-muted-text mt-1 text-xs">
            delivery {consoleStatus?.delivery_status_available ? 'rastreavel' : 'indisponivel'}
          </p>
        </Card>
      </div>

      <div className="flex flex-col gap-3 rounded-md border border-white/10 bg-slate-950/45 p-4 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-sm font-semibold text-slate-100">Console real local</p>
          <p className="app-muted-text mt-1 text-sm">
            {consoleStatus?.demo_note || 'Dados consumidos do Event Model/Dual Bot local. Nao e painel estatico.'}
          </p>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <Button variant="ghost" className="h-10" onClick={()=>loadConsole(selectedId)} disabled={loading || simulating}>
            Atualizar
          </Button>
          <Button className="h-10" onClick={createDemoFlow} disabled={simulating}>
            {simulating ? 'Simulando...' : 'Simular fluxo local'}
          </Button>
        </div>
      </div>

      {consent && (
        <Card className="card-muted">
          <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
            <div>
              <div className="app-label">Consentimento e opt-in</div>
              <AppCardTitle className="mt-2 text-xl">
                Bot {consent.bot_active ? 'ativo' : 'inativo'} - opt-in {consent.status}
              </AppCardTitle>
              <p className="app-muted-text mt-2 text-sm">{consent.limitation_notice}</p>
              <div className="mt-3 flex flex-wrap gap-2">
                {(consent.scopes.length ? consent.scopes : ['sem escopo ativo']).map(scope=> (
                  <AppBadge key={scope}>{scope.replace(/_/g, ' ')}</AppBadge>
                ))}
              </div>
            </div>
            <div className="grid gap-2 sm:grid-cols-3 lg:min-w-[420px]">
              <Button className="h-10" disabled={consentUpdating} onClick={()=>updateConsent(['active', 'bot_disabled'].includes(consent.status) ? 'activate' : 'accept')}>
                {['active', 'bot_disabled'].includes(consent.status) ? 'Reativar bot' : 'Aceitar opt-in'}
              </Button>
              <Button variant="ghost" className="h-10" disabled={consentUpdating || !consent.bot_active} onClick={()=>updateConsent('deactivate')}>
                Desativar bot
              </Button>
              <Button variant="ghost" className="h-10" disabled={consentUpdating || consent.status === 'revoked'} onClick={()=>updateConsent('revoke')}>
                Revogar
              </Button>
            </div>
          </div>
          <div className="mt-4 grid gap-3 text-xs text-slate-400 md:grid-cols-3">
            <span>Mensagens: {consent.retention_message_body_days} dias</span>
            <span>Auditoria: {consent.retention_event_audit_days} dias</span>
            <span>Revogacao: {consent.delete_after_revocation_days} dias</span>
          </div>
        </Card>
      )}

      {error && (
        <div className="rounded-md border border-amber-300/25 bg-amber-950/25 px-4 py-3 text-sm font-medium text-amber-100">
          {error}
        </div>
      )}

      <div className="grid gap-6 xl:grid-cols-[minmax(300px,0.92fr)_minmax(0,1.42fr)]">
        <Card className="card-secondary overflow-hidden p-0">
          <div className="border-b border-white/10 px-4 py-3 sm:px-5">
            <AppSectionTitle className="text-lg">Inbox de casos</AppSectionTitle>
            <p className="app-muted-text mt-1 text-sm">Casos criados pelo Dual Bot Flow</p>
          </div>
          <div className="max-h-[620px] overflow-y-auto p-2">
            {loading && <p className="app-muted-text p-3 text-sm">Carregando casos...</p>}
            {!loading && cases.length === 0 && (
              <div className="p-3">
                <p className="text-sm font-semibold text-white">Nenhum caso aberto ainda.</p>
                <p className="app-muted-text mt-2 text-sm">
                  Crie um fluxo local para popular o Event Model e demonstrar o Console ponta a ponta.
                </p>
                <Button className="mt-4 h-10 w-full" onClick={createDemoFlow} disabled={simulating}>
                  {simulating ? 'Simulando...' : 'Criar caso mock real'}
                </Button>
              </div>
            )}
            {cases.map(item=> (
              <button
                key={item.case_id}
                type="button"
                onClick={()=>selectCase(item.case_id)}
                className={`mb-2 w-full rounded-md border p-3 text-left transition ${
                  selectedId === item.case_id
                    ? 'border-cyan-400/45 bg-cyan-950/25'
                    : 'border-white/10 bg-slate-950/30 hover:border-white/20'
                }`}
              >
                <div className="flex items-start justify-between gap-3">
                  <div>
                    <div className="text-sm font-semibold text-white">{item.protected_person_alias}</div>
                    <div className="app-muted-text mt-0.5 text-xs">
                      Responsavel: {item.guardian_alias || 'nao vinculado'}
                    </div>
                  </div>
                  <span className={riskStatusClass(item.risk_level)}>Risco {item.risk_level}</span>
                </div>
                <p className="mt-3 line-clamp-2 text-sm leading-5 text-slate-300">{item.message_summary}</p>
                <div className="mt-3 flex flex-wrap gap-2 text-xs text-slate-400">
                  <span>{caseStateLabel(item)}</span>
                  <span>·</span>
                  <span>{item.source_channel}</span>
                  {item.pattern_level && (
                    <>
                      <span>·</span>
                      <span>padrao {item.pattern_level}</span>
                    </>
                  )}
                  <span>·</span>
                  <span>{formatTime(item.updated_at)}</span>
                </div>
              </button>
            ))}
          </div>
        </Card>

        <div className="space-y-4">
          {detailLoading && (
            <Card className="card-muted">
              <p className="app-muted-text text-sm">Carregando detalhe operacional...</p>
            </Card>
          )}

          {!detailLoading && selected ? (
            <>
              <div className="grid gap-4 lg:grid-cols-[0.85fr_1.15fr]">
                <section className="guardian-case-risk-card">
                  <div className="app-label text-red-200/90">Risco atual</div>
                  <div className="mt-3 flex flex-wrap items-end gap-3">
                    <span className="guardian-case-risk-score">{selected.risk_assessment?.score ?? selected.risk_score}</span>
                    <span className={riskStatusClass(selected.risk_assessment?.risk_level ?? selected.risk_level)}>
                      Risco {selected.risk_assessment?.risk_level ?? selected.risk_level}
                    </span>
                  </div>
                  <p className="mt-3 text-sm font-semibold leading-6 text-red-100/90">
                    Status: {statusLabels[selected.case?.status ?? selected.status] || selected.case?.status || selected.status}
                  </p>
                </section>

                <section className="guardian-case-action-card">
                  <div className="app-label text-emerald-200/90">Acao recomendada</div>
                  <p className="mt-3 text-lg font-semibold leading-7 text-emerald-50">
                    {selected.next_step || selected.recommended_action}
                  </p>
                  <p className="mt-3 text-sm leading-6 text-slate-400">
                    Baseado no score, sinais detectados e feedback do responsavel registrado no Event Model.
                  </p>
                </section>
              </div>

              <Card className="guardian-secondary-card">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="app-label">Caso ativo · {selected.case?.case_id ?? selected.case_id}</div>
                    <AppCardTitle className="mt-2 text-xl">
                      {selected.protected_person?.alias ?? selected.protected_person_alias} com responsavel {selected.responsible_contact?.alias || selected.guardian_alias || 'nao vinculado'}
                    </AppCardTitle>
                    <p className="app-muted-text mt-2 text-sm">
                      Canal {selected.message?.channel ?? selected.source_channel} · alerta {deliveryLabel(selected.channel_status?.guardian_alert_status ?? selected.delivery.guardian_alert_status)}
                    </p>
                  </div>
                  <div className="flex flex-wrap gap-2">
                    <AppBadge>{selected.channel_status?.provider ?? selected.activation.channel_provider}</AppBadge>
                    <AppBadge>{selected.channel_status?.environment_label ?? (selected.activation.simulated ? 'mock local' : 'demo')}</AppBadge>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 lg:grid-cols-3">
                  <div className="app-action-panel">
                    <div className="app-label">Pessoa protegida</div>
                    <p className="app-body-text mt-2">{selected.protected_person?.alias ?? selected.protected_person_alias}</p>
                    <p className="app-muted-text mt-2 text-xs">
                      Status: {selected.protected_person?.status ?? 'active'} · ID {selected.protected_person?.protected_person_id?.slice(0, 18) ?? 'local'}
                    </p>
                  </div>
                  <div className="app-action-panel">
                    <div className="app-label">Responsavel vinculado</div>
                    <p className="app-body-text mt-2">{selected.responsible_contact?.alias || selected.guardian_alias || 'nao vinculado'}</p>
                    <p className="app-muted-text mt-2 text-xs">
                      Notificado: {yesNo(selected.responsible_contact?.notified ?? selected.delivery.guardian_notified)} · entrega {deliveryLabel(selected.responsible_contact?.last_delivery_status ?? selected.delivery.guardian_alert_status)}
                    </p>
                  </div>
                  <div className="app-action-panel">
                    <div className="app-label">Canal e bots</div>
                    <p className="app-body-text mt-2">{selected.channel_status?.provider ?? selected.activation.channel_provider}</p>
                    <p className="app-muted-text mt-2 text-xs">
                      Protegido {yesNo(selected.channel_status?.protected_bot_active ?? selected.activation.protected_bot.active)} · Responsavel {yesNo(selected.channel_status?.responsible_bot_active ?? selected.activation.responsible_bot.active)}
                    </p>
                  </div>
                </div>

                <div className="mt-5 grid gap-4 lg:grid-cols-2">
                  <div className="app-action-panel">
                    <div className="app-label">Mensagem que disparou o alerta</div>
                    <p className="app-body-text mt-2">{selected.message?.body ?? selected.source_message}</p>
                    <p className="app-muted-text mt-2 text-xs">
                      Entrada {selected.message?.status ?? 'received'} · {formatTime(selected.message?.created_at ?? selected.created_at)}
                    </p>
                  </div>
                  <div className="app-action-panel">
                    <div className="app-label">Sinais detectados</div>
                    <div className="mt-3 flex flex-wrap gap-2">
                      {(selected.risk_assessment?.signals ?? selected.risk_signals).map(signal=> (
                        <AppBadge key={signal}>{signal.replace(/_/g, ' ')}</AppBadge>
                      ))}
                    </div>
                    {selected.risk_assessment?.explanation?.length ? (
                      <p className="app-muted-text mt-3 text-xs">
                        {selected.risk_assessment.explanation.join(' · ')}
                      </p>
                    ) : null}
                  </div>
                </div>

                <div className="mt-4 grid gap-4 lg:grid-cols-2">
                  <div className="app-action-panel border-cyan-400/20">
                    <div className="app-label">Bot Protegido enviou</div>
                    <p className="app-body-text mt-2">{selected.protected_reply.body}</p>
                    <p className="app-muted-text mt-3 text-xs">
                      Status: {deliveryLabel(selected.channel_status?.protected_reply_status ?? selected.protected_reply.status)} · {selected.protected_reply.simulated ? 'simulado' : 'provider controlado'}
                    </p>
                  </div>
                  <div className="app-action-panel border-emerald-400/20">
                    <div className="app-label">Bot Responsavel enviou</div>
                    <p className="app-body-text mt-2">{selected.guardian_alert.body}</p>
                    <p className="app-muted-text mt-3 text-xs">
                      Status: {deliveryLabel(selected.channel_status?.guardian_alert_status ?? selected.guardian_alert.status)} · notificado: {yesNo(selected.channel_status?.guardian_notified ?? selected.delivery.guardian_notified)}
                    </p>
                  </div>
                </div>
              </Card>

              {selected.pattern && (
                <Card className="card-evidence">
                  <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <div className="app-label">Pattern Intelligence</div>
                      <AppCardTitle className="mt-2 text-xl">{selected.pattern.threat_type_label || 'Padroes explicaveis'}</AppCardTitle>
                      <p className="app-body-text mt-2">{selected.pattern.explanation}</p>
                      <p className="app-muted-text mt-2 text-sm">{selected.pattern.recommendation}</p>
                    </div>
                    <span className={riskStatusClass(selected.pattern.level)}>
                      Padrao {selected.pattern.level} · {selected.pattern.score}/100
                    </span>
                  </div>
                  <div className="mt-4 grid gap-4 lg:grid-cols-[1fr_0.85fr_0.85fr]">
                    <div className="app-action-panel">
                      <div className="app-label">Sinais de padrao</div>
                      <div className="mt-3 flex flex-wrap gap-2">
                        {selected.pattern.signals.map(signal=> (
                          <AppBadge key={signal}>{signal.replace(/_/g, ' ')}</AppBadge>
                        ))}
                      </div>
                    </div>
                    <div className="app-action-panel">
                      <div className="app-label">Recorrencia</div>
                      <p className="app-body-text mt-2">{recurrenceText(selected.pattern.recurrence)}</p>
                      <p className="app-muted-text mt-2 text-xs">
                        Clusters: {selected.pattern.cluster_ids.length || 0} · feedback: {selected.pattern.feedback_label || 'pendente'}
                      </p>
                    </div>
                    <div className="app-action-panel">
                      <div className="app-label">Evidencias</div>
                      <div className="mt-2 space-y-2">
                        {selected.pattern.reasons.slice(0, 3).map(reason=> (
                          <p key={reason} className="text-sm leading-5 text-slate-300">{reason}</p>
                        ))}
                      </div>
                    </div>
                  </div>
                </Card>
              )}

              {selected.agent_decisions?.length ? (
                <Card className="card-evidence">
                  <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                    <div>
                      <div className="app-label">Agentes controlados</div>
                      <AppCardTitle className="mt-2 text-xl">Decisoes auditaveis</AppCardTitle>
                      <p className="app-muted-text mt-2 text-sm">
                        Saidas tipadas, com guardrails e revisao humana preservada.
                      </p>
                    </div>
                    <AppBadge>{selected.agent_decisions.length} decisoes</AppBadge>
                  </div>
                  <div className="mt-4 grid gap-3 lg:grid-cols-2">
                    {selected.agent_decisions.map(decision=> (
                      <div key={decision.event_id} className="app-action-panel">
                        <div className="flex flex-wrap items-center justify-between gap-2">
                          <span className="text-sm font-semibold text-white">{decision.agent}</span>
                          {decision.fallback_used ? <AppBadge>fallback seguro</AppBadge> : <AppBadge>guardrails ok</AppBadge>}
                        </div>
                        <p className="mt-2 text-sm leading-6 text-slate-300">{decision.summary}</p>
                        {decision.recommended_action ? (
                          <p className="app-muted-text mt-2 text-xs">{decision.recommended_action}</p>
                        ) : null}
                        {decision.guardrails.length ? (
                          <p className="mt-2 text-xs text-cyan-100/75">
                            {decision.guardrails.slice(0, 2).join(' - ')}
                          </p>
                        ) : null}
                        <p className="mt-2 text-xs text-slate-500">{formatTime(decision.occurred_at)}</p>
                      </div>
                    ))}
                  </div>
                </Card>
              ) : null}

              <Card className="card-action">
                <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="app-label">Acoes do responsavel</div>
                    <p className="app-muted-text mt-2 text-sm">
                      Ultimo feedback: {selected.feedback?.latest_action ? `${selected.feedback.latest_action} por ${selected.feedback.latest_actor || 'responsavel'}` : 'pendente'}
                    </p>
                  </div>
                  <span className={riskStatusClass(selected.risk_level)}>Risco {selected.risk_level}</span>
                </div>
                <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                  {(selectedActions?.length ? selectedActions : Object.keys(actionLabels) as GuardianFeedbackAction[]).map(action=> (
                    <Button
                      key={action}
                      variant={action === 'confirm_scam' ? 'primary' : 'ghost'}
                      className="h-11"
                      disabled={updating}
                      onClick={()=>submitFeedback(action)}
                    >
                      {actionLabels[action]}
                    </Button>
                  ))}
                </div>
              </Card>

              <Card className="card-evidence">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="app-label">Timeline auditavel</div>
                    <AppCardTitle className="mt-2 text-xl">Eventos do caso</AppCardTitle>
                  </div>
                  <AppBadge>{selectedTimeline.length} eventos</AppBadge>
                </div>
                <ol className="guardian-operational-timeline mt-5">
                  {selectedTimeline.map((event,index)=> (
                    <li key={event.event_id} className="guardian-timeline-item">
                      <span className="guardian-timeline-index">{String(index + 1).padStart(2,'0')}</span>
                      <div>
                        <div className="flex flex-wrap items-center gap-2">
                          <span className="text-sm font-semibold text-white">{event.label}</span>
                          {event.status && <AppBadge>{deliveryLabel(event.status)}</AppBadge>}
                        </div>
                        <p className="mt-1 text-sm leading-6 text-slate-400">{event.description}</p>
                        <p className="mt-1 text-xs text-slate-500">{formatTime(event.occurred_at)} · {event.event_type}</p>
                      </div>
                    </li>
                  ))}
                </ol>
              </Card>

              <Card className="card-muted">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="app-label">Audit log</div>
                    <AppCardTitle className="mt-2 text-xl">Registro auditavel</AppCardTitle>
                  </div>
                  <AppBadge>{selected.audit_log?.length ?? 0} registros</AppBadge>
                </div>
                <div className="mt-4 grid gap-2">
                  {(selected.audit_log ?? []).slice(-6).map(entry=> (
                    <div key={entry.audit_log_id} className="flex flex-col gap-1 rounded-md border border-white/10 bg-slate-950/35 p-3 sm:flex-row sm:items-center sm:justify-between">
                      <div>
                        <p className="text-sm font-semibold text-white">{entry.action}</p>
                        <p className="app-muted-text mt-1 text-xs">{auditTarget(entry)}</p>
                      </div>
                      <p className="text-xs text-slate-500">{formatTime(entry.created_at)}</p>
                    </div>
                  ))}
                  {!(selected.audit_log?.length) && (
                    <p className="app-muted-text text-sm">Nenhum registro de auditoria para este caso.</p>
                  )}
                </div>
              </Card>

              <div className="grid gap-3 sm:grid-cols-3">
                <Card className="card-muted !p-4">
                  <div className="app-label">Responsavel confirmou</div>
                  <p className="mt-2 text-sm font-semibold text-white">{yesNo(selected.feedback?.guardian_confirmed ?? selected.guardian_confirmed)}</p>
                </Card>
                <Card className="card-muted !p-4">
                  <div className="app-label">Falso positivo</div>
                  <p className="mt-2 text-sm font-semibold text-white">{yesNo(selected.feedback?.false_positive ?? selected.false_positive)}</p>
                </Card>
                <Card className="card-muted !p-4">
                  <div className="app-label">Resolucao</div>
                  <p className="mt-2 text-sm font-semibold text-white">{(selected.feedback?.resolved ?? selected.resolved) ? 'resolvido' : 'pendente'}</p>
                </Card>
              </div>
            </>
          ) : null}

          {!loading && !detailLoading && !selected && cases.length > 0 && (
            <Card>
              <p className="app-muted-text">Selecione um caso na fila para ver detalhes operacionais.</p>
            </Card>
          )}
        </div>
      </div>
    </div>
  )
}
