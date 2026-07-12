"use client"

import React, {useCallback, useEffect, useState} from 'react'
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
  needs_review: 'Revisar',
  mark_resolved: 'Resolvido',
}

const actionNotes: Record<GuardianFeedbackAction, string> = {
  confirm_scam: 'Responsável confirmou o risco por canal independente.',
  false_alarm: 'Responsável marcou este caso como falso positivo.',
  needs_review: 'Responsável pediu revisão antes de concluir.',
  mark_resolved: 'Responsável encerrou o caso no console.',
}

// Segmented control: neutro por padrão; só o texto carrega a semântica.
const actionAccents: Record<GuardianFeedbackAction, string> = {
  confirm_scam: 'text-red-300',
  false_alarm: 'text-slate-300',
  needs_review: 'text-amber-200',
  mark_resolved: 'text-emerald-300',
}

type RiskTheme = {
  label: string
  dot: string
  banner: string
  score: string
}

// 3 cores semânticas, dessaturadas para dark mode. Vermelho forte só no detalhe.
const RISK_THEMES: Record<string, RiskTheme> = {
  critical: {label:'Crítico', dot:'bg-red-400', banner:'border-red-400/35 bg-red-950/30', score:'text-red-300'},
  high: {label:'Alto', dot:'bg-red-400', banner:'border-red-400/30 bg-red-950/25', score:'text-red-300'},
  medium: {label:'Médio', dot:'bg-amber-300', banner:'border-amber-300/30 bg-amber-950/20', score:'text-amber-200'},
  low: {label:'Baixo', dot:'bg-emerald-400', banner:'border-emerald-400/30 bg-emerald-950/20', score:'text-emerald-300'},
}

function riskTheme(level?: string | null): RiskTheme {
  const key = (level || '').toLowerCase()
  if (key === 'critical') return RISK_THEMES.critical
  if (key === 'high' || key === 'alto') return RISK_THEMES.high
  if (key === 'low' || key === 'baixo') return RISK_THEMES.low
  return RISK_THEMES.medium
}

function formatTime(iso:string){
  try{
    return new Date(iso).toLocaleString('pt-BR', {dateStyle: 'short', timeStyle: 'short'})
  }catch{
    return iso
  }
}

// "há 2h" em vez de data completa — a fila é sobre recência, não sobre datas.
function timeAgo(iso:string){
  try{
    const diff = Date.now() - new Date(iso).getTime()
    const min = Math.floor(diff / 60000)
    if(min < 1) return 'agora'
    if(min < 60) return `há ${min}min`
    const hours = Math.floor(min / 60)
    if(hours < 24) return `há ${hours}h`
    const days = Math.floor(hours / 24)
    if(days < 7) return `há ${days}d`
    return new Date(iso).toLocaleDateString('pt-BR', {day:'2-digit', month:'2-digit'})
  }catch{
    return ''
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

const GHOST_BTN = 'inline-flex h-9 items-center rounded-lg border border-white/10 px-3 text-sm font-medium text-slate-300 transition hover:bg-white/5 hover:text-white disabled:opacity-50'
const PRIMARY_BTN = 'inline-flex h-9 items-center rounded-lg bg-teal-400 px-4 text-sm font-semibold text-slate-950 transition hover:brightness-110 disabled:opacity-50'

export default function GuardianAdminConsole({operatorName}:{operatorName?:string}){
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
  const caseCount = consoleStatus?.case_count ?? cases.length
  const channel = consoleStatus?.channel_provider || 'mock'
  const level = selected ? (selected.risk_assessment?.risk_level ?? selected.risk_level) : undefined
  const theme = riskTheme(level)
  const feedbackActions = (selectedActions?.length ? selectedActions : Object.keys(actionLabels) as GuardianFeedbackAction[])

  return (
    <div className="space-y-4">
      {/* Header único do console: título + métricas inline + ações */}
      <div className="flex flex-wrap items-center justify-between gap-x-6 gap-y-3 rounded-lg border border-white/10 bg-slate-950/50 px-5 py-4">
        <div className="min-w-0">
          <div className="flex flex-wrap items-baseline gap-x-3 gap-y-1">
            <h1 className="text-lg font-bold leading-tight text-white">Guardian Console</h1>
            <span className="text-sm text-slate-400">{caseCount} casos</span>
            <span className="text-slate-600" aria-hidden>·</span>
            <span className={`text-sm font-medium ${openCount > 0 ? 'text-amber-200' : 'text-slate-400'}`}>
              {openCount} {openCount === 1 ? 'precisa' : 'precisam'} de atenção
            </span>
            <span className="text-slate-600" aria-hidden>·</span>
            <span className="inline-flex items-center gap-1.5 text-sm text-slate-400">
              <span className="h-1.5 w-1.5 rounded-full bg-emerald-400" aria-hidden />
              {channel}
            </span>
          </div>
          <p className="mt-1 text-xs text-slate-500">
            Casos compartilhados voluntariamente — decisões críticas exigem confirmação humana.{' '}
            <a href="/trust-center" className="text-teal-300/80 transition hover:text-teal-200">Saiba mais</a>
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <a href="/whatsapp-setup" className={PRIMARY_BTN}>Conectar WhatsApp</a>
          <button onClick={()=>loadConsole(selectedId)} disabled={loading || simulating} className={GHOST_BTN}>
            Atualizar
          </button>
          <button onClick={createDemoFlow} disabled={simulating} className={GHOST_BTN}>
            {simulating ? 'Simulando…' : 'Simular caso'}
          </button>
        </div>
      </div>

      {error && (
        <div className="rounded-lg border border-amber-300/25 bg-amber-950/25 px-4 py-3 text-sm font-medium text-amber-100">
          {error}
        </div>
      )}

      <div className="grid gap-4 lg:grid-cols-[340px_minmax(0,1fr)]">
        {/* Fila de alertas — mínima: nome, dot de risco, 1ª linha, tempo relativo */}
        <div className="self-start overflow-hidden rounded-lg border border-white/10 bg-slate-950/40">
          <div className="border-b border-white/10 px-4 py-3">
            <h2 className="text-sm font-semibold text-white">Alertas</h2>
          </div>
          <div className="max-h-[620px] overflow-y-auto" style={{scrollbarWidth:'thin'}}>
            {loading && <p className="p-4 text-sm text-slate-500">Carregando…</p>}
            {!loading && cases.length === 0 && (
              <div className="p-4">
                <p className="text-sm font-semibold text-white">Nenhum alerta ainda.</p>
                <p className="mt-1 text-sm text-slate-500">Simule um caso para ver o fluxo completo.</p>
                <button onClick={createDemoFlow} disabled={simulating} className={`${PRIMARY_BTN} mt-3 w-full justify-center`}>
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
                  className={`block w-full border-b border-white/5 px-4 py-3 text-left transition ${
                    active ? 'border-l-2 border-l-teal-300 bg-white/[0.06]' : 'border-l-2 border-l-transparent hover:bg-white/[0.03]'
                  }`}
                >
                  <div className="flex items-center justify-between gap-2">
                    <span className="truncate text-sm font-semibold text-white">{item.protected_person_alias}</span>
                    <span className="flex flex-none items-center gap-1.5 text-[11px] text-slate-500">
                      <span className={`h-1.5 w-1.5 rounded-full ${itemTheme.dot}`} aria-hidden />
                      {itemTheme.label}
                    </span>
                  </div>
                  <p className="mt-1 truncate text-sm text-slate-400">{item.message_summary}</p>
                  <p className="mt-1 text-[11px] text-slate-600">{timeAgo(item.updated_at)}</p>
                </button>
              )
            })}
          </div>
        </div>

        {/* Detalhe do caso — hierarquia: ação recomendada > mensagem > resto */}
        <div className="min-w-0 space-y-4">
          {detailLoading && (
            <div className="rounded-lg border border-white/10 bg-slate-950/40 p-5">
              <p className="text-sm text-slate-500">Carregando caso…</p>
            </div>
          )}

          {!detailLoading && selected ? (
            <>
              {/* 1. O que fazer — a informação mais importante */}
              <div className={`rounded-lg border p-5 ${theme.banner}`}>
                <div className="flex flex-wrap items-center gap-x-3 gap-y-1 text-sm">
                  <span className="font-semibold text-white">
                    {selected.protected_person?.alias ?? selected.protected_person_alias}
                  </span>
                  <span className="text-slate-500" aria-hidden>·</span>
                  <span className={`font-semibold ${theme.score}`}>
                    Risco {theme.label} ({selected.risk_assessment?.score ?? selected.risk_score})
                  </span>
                  <span className="text-slate-500" aria-hidden>·</span>
                  <span className="text-slate-400">{statusLabels[selected.case?.status ?? selected.status] || selected.status}</span>
                </div>
                <p className="mt-3 text-lg font-semibold leading-snug text-white">
                  {selected.next_step || selected.recommended_action}
                </p>
                <p className="mt-1 text-xs text-slate-500">O que fazer agora</p>
              </div>

              {/* 2. Mensagem + 3. alerta/ações — um único contêiner, separadores de 1px */}
              <div className="rounded-lg border border-white/10 bg-slate-950/40">
                <div className="p-5">
                  <blockquote className="border-l-2 border-white/20 pl-4 text-sm leading-6 text-slate-200">
                    “{selected.message?.body ?? selected.source_message}”
                  </blockquote>
                  <p className="mt-2 text-xs text-slate-500">
                    {selected.message?.channel ?? selected.source_channel} · {formatTime(selected.message?.created_at ?? selected.created_at)}
                  </p>
                  <div className="mt-3 flex flex-wrap gap-1.5">
                    {(selected.risk_assessment?.signals ?? selected.risk_signals).map(signal=> (
                      <span key={signal} className="rounded border border-white/10 px-2 py-0.5 text-[11px] text-slate-400">
                        {signal.replace(/_/g, ' ')}
                      </span>
                    ))}
                  </div>
                </div>

                <details className="group border-t border-white/10">
                  <summary className="flex cursor-pointer list-none items-center gap-2 px-5 py-3 text-sm font-medium text-slate-300 transition hover:text-white">
                    <span className="text-xs text-slate-500 transition group-open:rotate-90" aria-hidden>▸</span>
                    Ver alerta enviado
                    <span className="text-xs font-normal text-slate-500">
                      {selected.responsible_contact?.alias || selected.guardian_alias || 'não vinculado'} · {deliveryLabel(selected.channel_status?.guardian_alert_status ?? selected.guardian_alert.status)}
                    </span>
                  </summary>
                  <div className="px-5 pb-4">
                    <p className="text-sm leading-6 text-slate-300">{selected.guardian_alert.body}</p>
                    <p className="mt-2 text-xs text-slate-500">
                      O bot nunca responde ao remetente — o alerta vai só para o contato de confiança.
                    </p>
                  </div>
                </details>

                <div className="flex flex-wrap items-center justify-between gap-3 border-t border-white/10 px-5 py-3">
                  <div className="inline-flex overflow-hidden rounded-lg border border-white/10">
                    {feedbackActions.map((action, index)=> (
                      <button
                        key={action}
                        type="button"
                        disabled={updating}
                        onClick={()=>submitFeedback(action)}
                        className={`h-9 px-3 text-xs font-medium transition hover:bg-white/5 disabled:opacity-50 ${
                          index > 0 ? 'border-l border-white/10' : ''
                        } ${actionAccents[action]}`}
                      >
                        {actionLabels[action]}
                      </button>
                    ))}
                  </div>
                  <p className="text-xs text-slate-500">
                    {selected.feedback?.latest_action
                      ? `Último: ${selected.feedback.latest_action} por ${selected.feedback.latest_actor || 'responsável'}`
                      : 'Nenhum feedback ainda'}
                  </p>
                </div>
              </div>

              {/* Detalhes técnicos — recolhido; inclui infraestrutura e canais */}
              <details className="group rounded-lg border border-white/10 bg-slate-950/40">
                <summary className="flex cursor-pointer list-none items-center gap-2 px-5 py-3 text-sm font-medium text-slate-300 transition hover:text-white">
                  <span className="text-xs text-slate-500 transition group-open:rotate-90" aria-hidden>▸</span>
                  Detalhes técnicos
                  <span className="text-xs font-normal text-slate-500">linha do tempo, padrões, auditoria, consentimento, infra</span>
                </summary>
                <div className="space-y-5 border-t border-white/10 p-5">
                  {/* Infraestrutura */}
                  <section>
                    <div className="app-label">Infraestrutura</div>
                    <div className="mt-2 grid gap-x-6 gap-y-1 text-sm text-slate-300 sm:grid-cols-3">
                      <span><span className="text-slate-500">Operador:</span> {operatorName || 'local'}</span>
                      <span><span className="text-slate-500">Armazenamento:</span> SQLite (persistente)</span>
                      <span><span className="text-slate-500">Canal:</span> {channel} · não-oficial</span>
                    </div>
                    <a href="/chatbot-demo" className="mt-2 inline-block text-xs text-teal-300/80 transition hover:text-teal-200">
                      Ver canal da pessoa protegida →
                    </a>
                  </section>

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
                    <section className="border-t border-white/10 pt-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="app-label">Pattern Intelligence · {selected.pattern.threat_type_label || 'padrões'}</div>
                        <span className="flex items-center gap-1.5 text-xs text-slate-400">
                          <span className={`h-1.5 w-1.5 rounded-full ${riskTheme(selected.pattern.level).dot}`} aria-hidden />
                          {riskTheme(selected.pattern.level).label}
                        </span>
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
                    <section className="border-t border-white/10 pt-4">
                      <div className="flex flex-wrap items-center justify-between gap-2">
                        <div className="app-label">Decisão híbrida · policy {hybrid.policy_version ?? 'v1'}</div>
                        <div className="flex items-center gap-2">
                          {hybrid.shadow_decision ? <AppBadgeText>shadow</AppBadgeText> : null}
                          <span className={`rounded-lg border px-2 py-1 text-xs font-bold ${
                            hybrid.action === 'AUTO_ALERT' ? 'border-red-400/40 text-red-200'
                            : hybrid.action === 'REVIEW' ? 'border-amber-300/40 text-amber-100'
                            : 'border-slate-400/30 text-slate-300'
                          }`}>{hybrid.action ?? '—'}</span>
                        </div>
                      </div>
                      <div className="mt-3 grid gap-x-6 gap-y-2 text-sm sm:grid-cols-3">
                        <div>
                          <div className="app-muted-text text-xs">Score final</div>
                          <p className="mt-0.5 font-semibold text-white">{hybrid.final_score ?? '—'}
                            <span className="ml-2 text-xs font-normal text-slate-500">det {hybrid.deterministic_score ?? '—'} · LLM {hybrid.llm_score ?? '—'}</span>
                          </p>
                        </div>
                        <div>
                          <div className="app-muted-text text-xs">LLM</div>
                          <p className="mt-0.5 font-semibold text-white">{hybrid.classification ?? 'indisponível'}
                            <span className="ml-2 text-xs font-normal text-slate-500">conf {hybrid.confidence != null ? hybrid.confidence.toFixed(2) : '—'}</span>
                          </p>
                        </div>
                        <div>
                          <div className="app-muted-text text-xs">Estado</div>
                          <p className="mt-0.5 font-semibold text-white">{hybrid.conflict ? 'conflito regras×LLM' : 'sem conflito'}
                            <span className="ml-2 text-xs font-normal text-slate-500">{hybrid.requires_human_review ? 'requer revisão' : 'automatizável'}</span>
                          </p>
                        </div>
                      </div>
                      {hybrid.rule_codes?.length ? (
                        <div className="mt-3 flex flex-wrap gap-1.5">
                          {hybrid.rule_codes.map(code => (
                            <span key={code} className="rounded border border-white/10 px-2 py-0.5 text-[11px] text-slate-400">{code}</span>
                          ))}
                        </div>
                      ) : null}
                      {hybrid.reasons?.length ? (
                        <ul className="mt-2 grid gap-1">
                          {hybrid.reasons.map((reason,i) => (
                            <li key={i} className="text-xs text-slate-500">· {reason}</li>
                          ))}
                        </ul>
                      ) : null}
                    </section>
                  ) : null}

                  {/* Decisões dos agentes */}
                  {selected.agent_decisions?.length ? (
                    <section className="border-t border-white/10 pt-4">
                      <div className="app-label">Decisões dos agentes · {selected.agent_decisions.length}</div>
                      <div className="mt-3 grid gap-3 lg:grid-cols-2">
                        {selected.agent_decisions.map(decision=> (
                          <div key={decision.event_id} className="rounded-lg border border-white/10 p-3">
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
                  <section className="border-t border-white/10 pt-4">
                    <div className="app-label">Registro auditável · {selected.audit_log?.length ?? 0}</div>
                    <div className="mt-3 grid gap-1.5">
                      {(selected.audit_log ?? []).slice(-6).map(entry=> (
                        <div key={entry.audit_log_id} className="flex flex-col gap-0.5 py-1.5 sm:flex-row sm:items-center sm:justify-between">
                          <div>
                            <p className="text-sm font-medium text-slate-200">{entry.action}</p>
                            <p className="text-xs text-slate-500">{auditTarget(entry)}</p>
                          </div>
                          <p className="text-xs text-slate-500">{formatTime(entry.created_at)}</p>
                        </div>
                      ))}
                      {!(selected.audit_log?.length) && (
                        <p className="text-sm text-slate-500">Nenhum registro para este caso.</p>
                      )}
                    </div>
                  </section>

                  {/* Consentimento / opt-in */}
                  {consent && (
                    <section className="border-t border-white/10 pt-4">
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
                          <button className={`${PRIMARY_BTN} justify-center`} disabled={consentUpdating} onClick={()=>updateConsent(['active', 'bot_disabled'].includes(consent.status) ? 'activate' : 'accept')}>
                            {['active', 'bot_disabled'].includes(consent.status) ? 'Reativar bot' : 'Aceitar opt-in'}
                          </button>
                          <button className={`${GHOST_BTN} justify-center`} disabled={consentUpdating || !consent.bot_active} onClick={()=>updateConsent('deactivate')}>
                            Desativar bot
                          </button>
                          <button className={`${GHOST_BTN} justify-center text-red-300 hover:text-red-200`} disabled={consentUpdating || consent.status === 'revoked'} onClick={()=>updateConsent('revoke')}>
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
            <div className="rounded-lg border border-white/10 bg-slate-950/40 p-5">
              <p className="text-sm text-slate-500">Selecione um alerta na fila para ver os detalhes.</p>
            </div>
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
