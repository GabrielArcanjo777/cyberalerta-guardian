"use client"

import React, {useCallback, useEffect, useState} from 'react'
import Card from '@/components/Card'
import {
  getGuardianConsoleRealCase,
  getGuardianConsoleRealCases,
  getGuardianConsoleRealStatus,
  getHybridDecision,
  postConsentAccept,
  postConsentBotActivate,
  postConsentBotDeactivate,
  postConsentRevoke,
  postDualBotMockProtectedMessage,
  postGuardianConsoleRealFeedback,
  type HybridDecisionView,
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
  under_review: 'Em revisão',
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
  confirm_scam: 'Responsável confirmou o risco por canal independente.',
  false_alarm: 'Responsável marcou este caso como falso positivo.',
  needs_review: 'Responsável pediu revisão antes de concluir.',
  mark_resolved: 'Responsável encerrou o caso no console.',
}

// Cor de ação por semântica (confirmar = perigo, resolver = ok).
const actionClasses: Record<GuardianFeedbackAction, string> = {
  confirm_scam: 'border-red-500/50 bg-red-500/10 text-red-100 hover:bg-red-500/20',
  false_alarm: 'border-slate-500/40 bg-slate-500/10 text-slate-200 hover:bg-slate-500/20',
  needs_review: 'border-amber-400/45 bg-amber-400/10 text-amber-100 hover:bg-amber-400/20',
  mark_resolved: 'border-emerald-500/50 bg-emerald-500/10 text-emerald-100 hover:bg-emerald-500/20',
}

type RiskTheme = {
  label: string
  chip: string
  dot: string
  bar: string
  banner: string
  score: string
}

// Semáforo de risco: vermelho (alto/crítico), âmbar (médio), verde (baixo).
const RISK_THEMES: Record<string, RiskTheme> = {
  critical: {
    label: 'Crítico',
    chip: 'border-red-500/50 bg-red-500/15 text-red-200',
    dot: 'bg-red-500',
    bar: 'border-l-4 border-l-red-500',
    banner: 'border-red-500/40 bg-red-950/40',
    score: 'text-red-300',
  },
  high: {
    label: 'Alto',
    chip: 'border-red-500/45 bg-red-500/12 text-red-200',
    dot: 'bg-red-500',
    bar: 'border-l-4 border-l-red-500',
    banner: 'border-red-500/35 bg-red-950/35',
    score: 'text-red-300',
  },
  medium: {
    label: 'Médio',
    chip: 'border-amber-400/45 bg-amber-400/12 text-amber-100',
    dot: 'bg-amber-400',
    bar: 'border-l-4 border-l-amber-400',
    banner: 'border-amber-400/35 bg-amber-950/30',
    score: 'text-amber-300',
  },
  low: {
    label: 'Baixo',
    chip: 'border-emerald-400/45 bg-emerald-400/12 text-emerald-100',
    dot: 'bg-emerald-400',
    bar: 'border-l-4 border-l-emerald-400',
    banner: 'border-emerald-400/35 bg-emerald-950/30',
    score: 'text-emerald-300',
  },
}

function riskTheme(level?: string | null): RiskTheme {
  const key = (level || '').toLowerCase()
  if (key === 'critical') return RISK_THEMES.critical
  if (key === 'high' || key === 'alto') return RISK_THEMES.high
  if (key === 'medium' || key === 'média' || key === 'media' || key === 'médio') return RISK_THEMES.medium
  if (key === 'low' || key === 'baixo') return RISK_THEMES.low
  return RISK_THEMES.medium
}

function RiskChip({level}: {level?: string | null}){
  const theme = riskTheme(level)
  return (
    <span className={`inline-flex items-center gap-1.5 whitespace-nowrap rounded-full border px-2.5 py-1 text-xs font-semibold ${theme.chip}`}>
      <span className={`h-1.5 w-1.5 rounded-full ${theme.dot}`} aria-hidden />
      Risco {theme.label}
    </span>
  )
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
  if(entries.length === 0) return 'sem recorrência registrada'
  return entries
    .map(([key,value])=>`${key.replace(/_/g, ' ')}: ${value}`)
    .join(' · ')
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
  const [hybrid,setHybrid]=useState<HybridDecisionView | null>(null)
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
      setError('Não foi possível carregar o console. Verifique se o backend local está ativo.')
      setSelected(null)
    }finally{
      setLoading(false)
    }
  },[])

  useEffect(()=>{
    let active = true
    if(!selectedId){ setHybrid(null); return }
    getHybridDecision(selectedId)
      .then(r => { if(active) setHybrid(r.available ? (r.decision ?? null) : null) })
      .catch(()=>{ if(active) setHybrid(null) })
    return ()=>{ active = false }
  },[selectedId])

  const selectCase = useCallback(async (caseId:string)=>{
    setSelectedId(caseId)
    setDetailLoading(true)
    setError('')
    try{
      setSelected(await getGuardianConsoleRealCase(caseId))
    }catch{
      setError('Não foi possível carregar o detalhe do caso.')
    }finally{
      setDetailLoading(false)
    }
  },[])

  useEffect(()=>{
    loadConsole()
  },[loadConsole])

  // Atualização silenciosa da fila: casos novos aparecem sem spinner e sem
  // interromper o caso que o responsável está lendo.
  useEffect(()=>{
    const id = setInterval(async ()=>{
      try{
        const [status, list] = await Promise.all([
          getGuardianConsoleRealStatus(),
          getGuardianConsoleRealCases(),
        ])
        setConsoleStatus(status)
        setCases(list.cases)
      }catch{
        // silencioso
      }
    }, 10000)
    return ()=>clearInterval(id)
  },[])

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
      setError('Não foi possível simular o fluxo local do Dual Bot.')
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
        guardian_alias: selected.guardian_alias || 'Responsável',
        note: actionNotes[action],
      })
      await loadConsole(selected.case_id)
    }catch{
      setError('Não foi possível registrar a ação do responsável.')
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
      setError('Não foi possível atualizar consentimento/opt-in.')
    }finally{
      setConsentUpdating(false)
    }
  }

  const consent = selected?.consent || consoleStatus?.consent
  const selectedTimeline = selected?.bot_events?.length ? selected.bot_events : selected?.timeline ?? []
  const selectedActions = selected?.feedback?.available_actions?.filter(isFeedbackAction)
  const openCount = consoleStatus?.open_case_count ?? cases.filter(c=>!c.resolved && !c.false_positive).length
  const level = selected ? (selected.risk_assessment?.risk_level ?? selected.risk_level) : undefined
  const theme = riskTheme(level)

  return (
    <div className="space-y-5">
      {/* Resumo compacto */}
      <div className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-slate-950/50 px-5 py-4">
        <div className="flex flex-wrap items-center gap-x-6 gap-y-2">
          <div>
            <div className="text-2xl font-bold text-white">{consoleStatus?.case_count ?? cases.length}</div>
            <div className="app-muted-text text-xs">casos no total</div>
          </div>
          <div>
            <div className="flex items-center gap-2 text-2xl font-bold text-white">
              <span className={`h-2.5 w-2.5 rounded-full ${openCount > 0 ? 'bg-amber-400' : 'bg-emerald-400'}`} aria-hidden />
              {openCount}
            </div>
            <div className="app-muted-text text-xs">precisam de atenção</div>
          </div>
          <div>
            <div className="text-sm font-semibold capitalize text-white">{consoleStatus?.channel_provider || 'mock'}</div>
            <div className="app-muted-text text-xs">canal ativo</div>
          </div>
        </div>
        <div className="flex flex-col gap-2 sm:flex-row">
          <button
            onClick={()=>loadConsole(selectedId)}
            disabled={loading || simulating}
            className="h-10 rounded-md border border-white/12 bg-slate-950/60 px-4 text-sm font-semibold text-slate-100 transition hover:border-white/25 disabled:opacity-50"
          >
            Atualizar
          </button>
          <button
            onClick={createDemoFlow}
            disabled={simulating}
            className="h-10 rounded-md border border-teal-300/45 bg-teal-500/90 px-4 text-sm font-bold text-slate-950 transition hover:bg-teal-400 disabled:opacity-50"
          >
            {simulating ? 'Simulando…' : 'Simular caso'}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-md border border-amber-300/25 bg-amber-950/25 px-4 py-3 text-sm font-medium text-amber-100">
          {error}
        </div>
      )}

      <div className="grid gap-5 xl:grid-cols-[minmax(280px,0.8fr)_minmax(0,1.5fr)]">
        {/* Fila de alertas — cor por risco na borda esquerda */}
        <Card className="card-secondary overflow-hidden p-0">
          <div className="border-b border-white/10 px-5 py-3">
            <h2 className="text-base font-bold text-white">Alertas</h2>
            <p className="app-muted-text mt-0.5 text-xs">Mensagens suspeitas monitoradas</p>
          </div>
          <div className="max-h-[640px] overflow-y-auto p-3">
            {loading && <p className="app-muted-text p-2 text-sm">Carregando…</p>}
            {!loading && cases.length === 0 && (
              <div className="p-2">
                <p className="text-sm font-semibold text-white">Nenhum alerta ainda.</p>
                <p className="app-muted-text mt-2 text-sm">
                  Simule um caso para ver o fluxo completo funcionando.
                </p>
                <button
                  onClick={createDemoFlow}
                  disabled={simulating}
                  className="mt-4 h-10 w-full rounded-md border border-teal-300/45 bg-teal-500/90 px-4 text-sm font-bold text-slate-950 transition hover:bg-teal-400 disabled:opacity-50"
                >
                  {simulating ? 'Simulando…' : 'Simular caso'}
                </button>
              </div>
            )}
            {cases.map(item=> {
              const itemTheme = riskTheme(item.risk_level)
              const active = selectedId === item.case_id
              return (
                <button
                  key={item.case_id}
                  type="button"
                  onClick={()=>selectCase(item.case_id)}
                  className={`mb-2 w-full rounded-md border bg-slate-950/40 p-3 text-left transition ${itemTheme.bar} ${
                    active ? 'border-white/30 ring-1 ring-white/20' : 'border-white/10 hover:border-white/20'
                  }`}
                >
                  <div className="flex items-start justify-between gap-2">
                    <div className="min-w-0">
                      <div className="truncate text-sm font-semibold text-white">{item.protected_person_alias}</div>
                      <div className="app-muted-text mt-0.5 truncate text-xs">
                        {item.guardian_alias ? `resp. ${item.guardian_alias}` : 'sem responsável'}
                      </div>
                    </div>
                    <RiskChip level={item.risk_level} />
                  </div>
                  <p className="mt-2 line-clamp-2 text-sm leading-5 text-slate-300">{item.message_summary}</p>
                  <div className="app-muted-text mt-2 flex flex-wrap items-center gap-1.5 text-xs">
                    <span>{caseStateLabel(item)}</span>
                    <span>·</span>
                    <span>{formatTime(item.updated_at)}</span>
                  </div>
                </button>
              )
            })}
          </div>
        </Card>

        {/* Caso selecionado — visão enxuta */}
        <div className="space-y-4">
          {detailLoading && (
            <Card className="card-muted"><p className="app-muted-text text-sm">Carregando caso…</p></Card>
          )}

          {!detailLoading && selected ? (
            <>
              {/* Banner de risco */}
              <div className={`rounded-xl border p-5 ${theme.banner}`}>
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div className="flex items-center gap-4">
                    <div className={`text-5xl font-black leading-none ${theme.score}`}>
                      {selected.risk_assessment?.score ?? selected.risk_score}
                    </div>
                    <div>
                      <RiskChip level={level} />
                      <p className="mt-2 text-sm font-semibold text-white">
                        {selected.protected_person?.alias ?? selected.protected_person_alias}
                        <span className="app-muted-text font-normal"> · {statusLabels[selected.case?.status ?? selected.status] || selected.status}</span>
                      </p>
                    </div>
                  </div>
                </div>
                <div className="mt-4 rounded-lg border border-white/10 bg-slate-950/40 p-4">
                  <div className="app-label">O que fazer</div>
                  <p className="mt-1 text-base font-semibold leading-6 text-white">
                    {selected.next_step || selected.recommended_action}
                  </p>
                </div>
              </div>

              {/* Mensagem suspeita + sinais */}
              <Card className="card-muted">
                <div className="app-label">Mensagem suspeita</div>
                <p className="mt-2 rounded-md border border-white/10 bg-slate-950/40 p-3 text-sm leading-6 text-slate-200">
                  “{selected.message?.body ?? selected.source_message}”
                </p>
                <div className="app-muted-text mt-2 text-xs">
                  Canal {selected.message?.channel ?? selected.source_channel} · {formatTime(selected.message?.created_at ?? selected.created_at)}
                </div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {(selected.risk_assessment?.signals ?? selected.risk_signals).map(signal=> (
                    <span key={signal} className={`rounded-full border px-2.5 py-1 text-xs font-medium ${theme.chip}`}>
                      {signal.replace(/_/g, ' ')}
                    </span>
                  ))}
                </div>
              </Card>

              {/* Único envio: alerta ao contato de confiança. Nada é enviado ao remetente. */}
              <Card className="card-muted">
                <div className="app-label">Alerta ao contato de confiança</div>
                <p className="app-body-text mt-2 text-sm leading-6">{selected.guardian_alert.body}</p>
                <p className="app-muted-text mt-2 text-xs">
                  {selected.responsible_contact?.alias || selected.guardian_alias || 'não vinculado'} · {deliveryLabel(selected.channel_status?.guardian_alert_status ?? selected.guardian_alert.status)}
                </p>
                <p className="app-muted-text mt-2 text-xs">
                  O bot nunca responde ao remetente. A análise fica registrada aqui no console para sua revisão.
                </p>
              </Card>

              {/* Ações do responsável */}
              <Card className="card-action">
                <div className="app-label">Suas ações</div>
                <p className="app-muted-text mt-1 text-sm">
                  Último feedback: {selected.feedback?.latest_action ? `${selected.feedback.latest_action} por ${selected.feedback.latest_actor || 'responsável'}` : 'nenhum ainda'}
                </p>
                <div className="mt-4 grid gap-2 sm:grid-cols-2 xl:grid-cols-4">
                  {(selectedActions?.length ? selectedActions : Object.keys(actionLabels) as GuardianFeedbackAction[]).map(action=> (
                    <button
                      key={action}
                      type="button"
                      disabled={updating}
                      onClick={()=>submitFeedback(action)}
                      className={`h-11 rounded-md border px-3 text-sm font-semibold transition disabled:opacity-50 ${actionClasses[action]}`}
                    >
                      {actionLabels[action]}
                    </button>
                  ))}
                </div>
              </Card>

              {/* Detalhes técnicos — recolhido por padrão para não poluir */}
              <details className="group rounded-xl border border-white/10 bg-slate-950/40">
                <summary className="cursor-pointer list-none px-5 py-3 text-sm font-semibold text-slate-200 transition hover:text-white">
                  <span className="inline-flex items-center gap-2">
                    <span className="text-slate-500 transition group-open:rotate-90">▶</span>
                    Detalhes técnicos (linha do tempo, padrões, auditoria e consentimento)
                  </span>
                </summary>
                <div className="space-y-4 border-t border-white/10 p-5">
                  {/* Linha do tempo */}
                  <section>
                    <div className="app-label">Linha do tempo · {selectedTimeline.length} eventos</div>
                    <ol className="guardian-operational-timeline mt-3">
                      {selectedTimeline.map((event,index)=> (
                        <li key={event.event_id} className="guardian-timeline-item">
                          <span className="guardian-timeline-index">{String(index + 1).padStart(2,'0')}</span>
                          <div>
                            <div className="flex flex-wrap items-center gap-2">
                              <span className="text-sm font-semibold text-white">{event.label}</span>
                              {event.status && <AppBadgeText>{deliveryLabel(event.status)}</AppBadgeText>}
                            </div>
                            <p className="mt-1 text-sm leading-6 text-slate-400">{event.description}</p>
                            <p className="mt-1 text-xs text-slate-500">{formatTime(event.occurred_at)} · {event.event_type}</p>
                          </div>
                        </li>
                      ))}
                    </ol>
                  </section>

                  {/* Pattern Intelligence */}
                  {selected.pattern && (
                    <section className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="app-label">Pattern Intelligence · {selected.pattern.threat_type_label || 'padrões'}</div>
                        <RiskChip level={selected.pattern.level} />
                      </div>
                      <p className="app-body-text mt-2 text-sm">{selected.pattern.explanation}</p>
                      <p className="app-muted-text mt-1 text-sm">{selected.pattern.recommendation}</p>
                      <div className="mt-3 grid gap-3 sm:grid-cols-2">
                        <div>
                          <div className="app-muted-text text-xs">Sinais de padrão</div>
                          <div className="mt-1 flex flex-wrap gap-1.5">
                            {selected.pattern.signals.map(signal=> (
                              <AppBadgeText key={signal}>{signal.replace(/_/g, ' ')}</AppBadgeText>
                            ))}
                          </div>
                        </div>
                        <div>
                          <div className="app-muted-text text-xs">Recorrência</div>
                          <p className="app-body-text mt-1 text-sm">{recurrenceText(selected.pattern.recurrence)}</p>
                        </div>
                      </div>
                    </section>
                  )}

                  {/* Decisão híbrida (regras + LLM + Policy Engine) */}
                  {hybrid ? (
                    <section>
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="app-label">Decisão híbrida · policy {hybrid.policy_version ?? 'v1'}</div>
                        <div className="flex items-center gap-2">
                          {hybrid.shadow_decision ? <AppBadgeText>shadow</AppBadgeText> : null}
                          <span className={`rounded-md border px-2 py-1 text-xs font-bold ${
                            hybrid.action === 'AUTO_ALERT' ? 'border-red-400/40 text-red-200'
                            : hybrid.action === 'REVIEW' ? 'border-amber-300/40 text-amber-100'
                            : 'border-slate-400/30 text-slate-300'
                          }`}>{hybrid.action ?? '—'}</span>
                        </div>
                      </div>
                      <div className="mt-3 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="app-muted-text text-xs">Score final</div>
                          <p className="mt-1 text-lg font-bold text-white">{hybrid.final_score ?? '—'}</p>
                          <p className="app-muted-text mt-1 text-xs">
                            det {hybrid.deterministic_score ?? '—'} · LLM {hybrid.llm_score ?? '—'}
                          </p>
                        </div>
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="app-muted-text text-xs">LLM</div>
                          <p className="mt-1 text-sm font-semibold text-white">{hybrid.classification ?? 'indisponível'}</p>
                          <p className="app-muted-text mt-1 text-xs">
                            conf {hybrid.confidence != null ? hybrid.confidence.toFixed(2) : '—'} · {hybrid.llm_model ?? hybrid.llm_status ?? '—'}
                          </p>
                        </div>
                        <div className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                          <div className="app-muted-text text-xs">Estado</div>
                          <p className="mt-1 text-sm font-semibold text-white">
                            {hybrid.conflict ? 'conflito regras×LLM' : 'sem conflito'}
                          </p>
                          <p className="app-muted-text mt-1 text-xs">
                            {hybrid.requires_human_review ? 'requer revisão humana' : 'automatizável'}
                          </p>
                        </div>
                      </div>
                      {hybrid.rule_codes?.length ? (
                        <div className="mt-3">
                          <div className="app-muted-text text-xs">Regras acionadas</div>
                          <div className="mt-1 flex flex-wrap gap-1.5">
                            {hybrid.rule_codes.map(code => (
                              <span key={code} className="rounded border border-white/10 bg-slate-900/50 px-2 py-0.5 text-xs text-slate-300">{code}</span>
                            ))}
                          </div>
                        </div>
                      ) : null}
                      {hybrid.reasons?.length ? (
                        <ul className="mt-3 grid gap-1">
                          {hybrid.reasons.map((reason,i) => (
                            <li key={i} className="text-xs text-slate-400">· {reason}</li>
                          ))}
                        </ul>
                      ) : null}
                    </section>
                  ) : null}

                  {/* Decisões dos agentes */}
                  {selected.agent_decisions?.length ? (
                    <section>
                      <div className="app-label">Decisões dos agentes · {selected.agent_decisions.length}</div>
                      <div className="mt-3 grid gap-3 lg:grid-cols-2">
                        {selected.agent_decisions.map(decision=> (
                          <div key={decision.event_id} className="rounded-md border border-white/10 bg-slate-950/30 p-3">
                            <div className="flex flex-wrap items-center justify-between gap-2">
                              <span className="text-sm font-semibold text-white">{decision.agent}</span>
                              <AppBadgeText>{decision.fallback_used ? 'fallback seguro' : 'guardrails ok'}</AppBadgeText>
                            </div>
                            <p className="mt-2 text-sm leading-6 text-slate-300">{decision.summary}</p>
                            <p className="mt-2 text-xs text-slate-500">{formatTime(decision.occurred_at)}</p>
                          </div>
                        ))}
                      </div>
                    </section>
                  ) : null}

                  {/* Audit log */}
                  <section>
                    <div className="app-label">Registro auditável · {selected.audit_log?.length ?? 0}</div>
                    <div className="mt-3 grid gap-2">
                      {(selected.audit_log ?? []).slice(-6).map(entry=> (
                        <div key={entry.audit_log_id} className="flex flex-col gap-1 rounded-md border border-white/10 bg-slate-950/30 p-3 sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <p className="text-sm font-semibold text-white">{entry.action}</p>
                            <p className="app-muted-text mt-1 text-xs">{auditTarget(entry)}</p>
                          </div>
                          <p className="text-xs text-slate-500">{formatTime(entry.created_at)}</p>
                        </div>
                      ))}
                      {!(selected.audit_log?.length) && (
                        <p className="app-muted-text text-sm">Nenhum registro para este caso.</p>
                      )}
                    </div>
                  </section>

                  {/* Consentimento / opt-in */}
                  {consent && (
                    <section className="rounded-lg border border-white/10 bg-slate-950/30 p-4">
                      <div className="flex flex-col gap-3 lg:flex-row lg:items-start lg:justify-between">
                        <div>
                          <div className="app-label">Consentimento · opt-in {consent.status}</div>
                          <p className="app-muted-text mt-2 text-sm">{consent.limitation_notice}</p>
                          <div className="mt-2 flex flex-wrap gap-1.5">
                            {(consent.scopes.length ? consent.scopes : ['sem escopo ativo']).map(scope=> (
                              <AppBadgeText key={scope}>{scope.replace(/_/g, ' ')}</AppBadgeText>
                            ))}
                          </div>
                        </div>
                        <div className="grid gap-2 sm:grid-cols-3 lg:min-w-[360px]">
                          <button className="h-10 rounded-md border border-teal-300/45 bg-teal-500/90 px-3 text-sm font-bold text-slate-950 transition hover:bg-teal-400 disabled:opacity-50" disabled={consentUpdating} onClick={()=>updateConsent(['active', 'bot_disabled'].includes(consent.status) ? 'activate' : 'accept')}>
                            {['active', 'bot_disabled'].includes(consent.status) ? 'Reativar bot' : 'Aceitar opt-in'}
                          </button>
                          <button className="h-10 rounded-md border border-white/12 bg-slate-950/60 px-3 text-sm font-semibold text-slate-100 transition hover:border-white/25 disabled:opacity-50" disabled={consentUpdating || !consent.bot_active} onClick={()=>updateConsent('deactivate')}>
                            Desativar bot
                          </button>
                          <button className="h-10 rounded-md border border-red-500/40 bg-red-500/10 px-3 text-sm font-semibold text-red-100 transition hover:bg-red-500/20 disabled:opacity-50" disabled={consentUpdating || consent.status === 'revoked'} onClick={()=>updateConsent('revoke')}>
                            Revogar
                          </button>
                        </div>
                      </div>
                      <div className="app-muted-text mt-3 grid gap-2 text-xs sm:grid-cols-3">
                        <span>Mensagens: {consent.retention_message_body_days} dias</span>
                        <span>Auditoria: {consent.retention_event_audit_days} dias</span>
                        <span>Revogação: {consent.delete_after_revocation_days} dias</span>
                      </div>
                    </section>
                  )}
                </div>
              </details>
            </>
          ) : null}

          {!loading && !detailLoading && !selected && cases.length > 0 && (
            <Card><p className="app-muted-text">Selecione um alerta na fila para ver os detalhes.</p></Card>
          )}
        </div>
      </div>
    </div>
  )
}

function AppBadgeText({children}: {children: React.ReactNode}){
  return (
    <span className="inline-flex items-center rounded-full border border-white/12 bg-white/5 px-2 py-0.5 text-xs text-slate-300">
      {children}
    </span>
  )
}
