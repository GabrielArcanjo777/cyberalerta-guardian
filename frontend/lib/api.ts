import {
  AdminCase,
  AdminAuditLogsResponse,
  AdminUsersResponse,
  AdminCaseListResponse,
  AdminCaseStatus,
  LoginPayload,
  LoginResponse,
  GoogleAuthStatusResponse,
  MFASetupResponse,
  MFAStatusResponse,
  MeResponse,
  RecoveryCodesResponse,
  RegisterPayload,
  AnalyzePayload,
  GuardianConsoleStatusResponse,
  GuardianConsoleRealCaseDetail,
  GuardianConsoleRealCaseListResponse,
  GuardianConsoleRealStatusResponse,
  GuardianFeedbackPayload,
  GuardianFeedbackResponse,
  DualBotFlowResponse,
  DualBotInboundPayload,
  ConsentAcceptPayload,
  ConsentActionPayload,
  ConsentScope,
  ConsentStatusResponse,
  IntakePayload,
  RecoveryPayload,
  RedactPreviewPayload,
  ProtectedResponseGeneratePayload,
  ProtectedResponseGenerateResponse,
  SimpleChannelStatusResponse,
  SimpleChannelSubmitPayload,
  SimpleChannelSubmitResponse,
  TrustedCircleEscalatePayload,
  TrustedCircleEscalateResponse,
  TrustedCircleEscalationRecord,
  TrustedCircleStatusResponse,
  AssistedProofSessionCreatePayload,
  AssistedProofSessionResponse,
  AssistedProofStepUpdatePayload,
  ProofTrustStepItem,
  AnalyzeResponse,
  EvolutionConnectionState,
} from './types'
import { createMockOCRPreview, createMockURLCheck, mockConnectorStatuses } from './connectorMockData'
import {
  createMockIntakeAnalyze,
  createMockRedactPreview,
  mockAnalyzeResult,
  mockMLTextResult,
  mockMLUrlResult,
  mockRecoveryResult,
} from './mockData'

export const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

const API = API_URL

async function authFetch(path:string, init:RequestInit = {}){
  const headers = new Headers(init.headers)
  if(init.body && !headers.has('Content-Type')){
    headers.set('Content-Type', 'application/json')
  }
  const res = await fetch(`${API}${path}`, {
    ...init,
    headers,
    credentials: 'include',
  })
  if(!res.ok){
    const body = await res.json().catch(()=>({detail:'Erro de autenticação'}))
    throw new Error(typeof body.detail === 'string' ? body.detail : 'Erro de autenticação')
  }
  return res
}

export function getGoogleLoginUrl(){
  return `${API}/auth/google/login`
}

export async function postLogin(payload:LoginPayload){
  const res = await authFetch('/auth/login', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return await res.json() as LoginResponse
}

export async function postRegister(payload:RegisterPayload){
  const res = await authFetch('/auth/register', {
    method: 'POST',
    body: JSON.stringify(payload),
  })
  return await res.json() as LoginResponse
}

export async function getGoogleAuthStatus(){
  const res = await fetch(`${API}/auth/google/status`, {credentials: 'include'})
  if(!res.ok) throw new Error('google-auth-status-error')
  return await res.json() as GoogleAuthStatusResponse
}

export async function postLogout(){
  const res = await authFetch('/auth/logout', {method: 'POST'})
  return await res.json() as {status:string}
}

export async function getAuthMe(){
  const res = await authFetch('/auth/me')
  return await res.json() as MeResponse
}

export async function postMfaSetup(){
  const res = await authFetch('/auth/mfa/setup', {method: 'POST'})
  return await res.json() as MFASetupResponse
}

export async function postMfaEnable(code:string){
  const res = await authFetch('/auth/mfa/enable', {
    method: 'POST',
    body: JSON.stringify({code}),
  })
  return await res.json() as RecoveryCodesResponse
}

export async function postMfaVerify(temporaryToken:string, code:string){
  const res = await authFetch('/auth/mfa/verify', {
    method: 'POST',
    body: JSON.stringify({temporary_token: temporaryToken, code}),
  })
  return await res.json() as LoginResponse
}

export async function postMfaDisable(password:string, code?:string){
  const res = await authFetch('/auth/mfa/disable', {
    method: 'POST',
    body: JSON.stringify({password, code}),
  })
  return await res.json() as MFAStatusResponse
}

export async function postMfaRegenerateRecoveryCodes(){
  const res = await authFetch('/auth/mfa/recovery-codes/regenerate', {method: 'POST'})
  return await res.json() as RecoveryCodesResponse
}

export async function getAdminUsers(){
  const res = await authFetch('/admin/users')
  return await res.json() as AdminUsersResponse
}

export async function getAdminAuditLogs(){
  const res = await authFetch('/admin/audit-logs')
  return await res.json() as AdminAuditLogsResponse
}

export async function getBackendHealth(){
  const res = await fetch(`${API}/health`, {credentials: 'include'})
  if(!res.ok) throw new Error('backend-health-error')
  return await res.json() as {status:string; service:string}
}

export async function getN8nHealth(){
  const res = await fetch(`${API}/integrations/n8n/health`, {credentials: 'include'})
  if(!res.ok) throw new Error('n8n-health-error')
  return await res.json() as Record<string, unknown>
}

export async function analyzeMessage(payload: AnalyzePayload): Promise<AnalyzeResponse>{
  try{
    const res = await fetch(`${API}/analyze`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...mockAnalyzeResult, __mock: true}
  }
}

export async function postRecovery(payload: RecoveryPayload){
  try{
    const res = await fetch(`${API}/recovery`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...mockRecoveryResult, __mock: true}
  }
}

export async function analyzeTextML(texto:string){
  try{
    const res = await fetch(`${API}/analisar`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({texto})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...mockMLTextResult, __mock: true}
  }
}

export async function analyzeURLML(url:string){
  try{
    const res = await fetch(`${API}/analisar-url`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...mockMLUrlResult, url, __mock: true}
  }
}

export async function postRedactPreview(payload: RedactPreviewPayload){
  try{
    const res = await fetch(`${API}/intake/redact-preview`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...createMockRedactPreview(payload.content), __mock: true}
  }
}

export async function postIntakeAnalyze(payload: IntakePayload){
  try{
    const res = await fetch(`${API}/intake/analyze`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...createMockIntakeAnalyze(payload.content, payload.channel), __mock: true}
  }
}

export async function getConnectorsStatus(){
  try{
    const res = await fetch(`${API}/connectors/status`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {connectors: mockConnectorStatuses, __mock: true}
  }
}

export async function postURLCheck(url:string){
  try{
    const res = await fetch(`${API}/connectors/url-check`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...createMockURLCheck(url), __mock: true}
  }
}

function createMockProtectedResponse(payload: ProtectedResponseGeneratePayload): ProtectedResponseGenerateResponse {
  const contact = payload.trusted_contact_alias
  const high = ['alto', 'critico'].includes(payload.risk_level)
  if (payload.category === 'golpe_pix' || /pedido_pix/i.test(payload.signals.join(' '))) {
    return {
      short_reply: high
        ? `Não faça Pix agora. Essa mensagem tem sinais de golpe${contact ? ` e estou avisando ${contact}` : ' e seu contato de confiança será avisado'}.`
        : 'Recebi sua mensagem. Não faça nenhuma transferência urgente agora.',
      tone: 'calm_clear',
      do_not_do: ['não fazer Pix', 'não clicar', 'não enviar código'],
      next_step: high ? 'aguardar contato de confiança' : 'aguardar verificação',
      __mock: true,
    }
  }
  if (payload.category === 'link_suspeito') {
    return {
      short_reply: 'Não clique nesse link. Ele pode ser perigoso e o caso será verificado pelo responsável.',
      tone: 'calm_clear',
      do_not_do: ['não clicar'],
      next_step: 'aguardar contato de confiança',
      __mock: true,
    }
  }
  if (payload.category === 'codigo_senha') {
    return {
      short_reply: contact
        ? `Não envie código nem senha. Aguarde até ${contact} confirmar.`
        : 'Não envie código nem senha. Aguarde seu contato de confiança confirmar.',
      tone: 'calm_clear',
      do_not_do: ['não enviar código', 'não enviar senha'],
      next_step: 'aguardar contato de confiança',
      __mock: true,
    }
  }
  return {
    short_reply: 'Recebi sua mensagem. Vou registrar para verificação, mas não faça nenhuma ação urgente agora.',
    tone: 'calm_clear',
    do_not_do: ['não agir com pressa'],
    next_step: 'aguardar verificação',
    __mock: true,
  }
}

function createMockSimpleChannelSubmit(payload: SimpleChannelSubmitPayload): SimpleChannelSubmitResponse {
  const highRisk = /pix|urgente|troquei de numero/i.test(payload.content)
  const mockResponse = createMockProtectedResponse({
    risk_level: highRisk ? 'alto' : 'baixo',
    category: highRisk ? 'golpe_pix' : 'risco_baixo',
    signals: highRisk ? ['urgencia', 'numero_novo', 'pedido_pix'] : [],
    trusted_contact_alias: payload.trusted_contact_alias,
  })
  return {
    channel_case_id: `ch-mock-${Date.now().toString(36)}`,
    risk_level: highRisk ? 'alto' : 'medio',
    simple_reply: mockResponse.short_reply,
    admin_case_created: payload.consent && highRisk,
    trust_lock_recommended: highRisk,
    __mock: true,
  }
}

const mockSimpleChannelStatus: SimpleChannelStatusResponse = {
  service: 'simple-channel-intake',
  mode: 'whatsapp_mock',
  channels: ['whatsapp_mock'],
  whatsapp_real_enabled: false,
  monitoring_enabled: false,
  privacy_note: 'Entrada voluntaria com consentimento. Nenhuma conversa privada e monitorada.',
  demo_note: 'WhatsApp real e integracao futura. MVP com conversa simulada.',
  __mock: true,
}

export async function getSimpleChannelStatus(){
  try{
    const res = await fetch(`${API}/simple-channel/status`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as SimpleChannelStatusResponse
  }catch{
    return {...mockSimpleChannelStatus}
  }
}

export async function postSimpleChannelSubmit(payload: SimpleChannelSubmitPayload){
  try{
    const res = await fetch(`${API}/simple-channel/submit`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    })
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as SimpleChannelSubmitResponse
  }catch{
    return createMockSimpleChannelSubmit(payload)
  }
}

const mockGuardianCases: AdminCase[] = [
  {
    case_id: 'case-demo-001',
    protected_person_alias: 'Dona Lucia',
    guardian_alias: 'Gabriel',
    source_channel: 'whatsapp_mock',
    received_content_summary: 'Mensagem simulando falso filho pedindo Pix urgente.',
    risk_score: 87,
    risk_level: 'alto',
    scam_category: 'golpe_pix',
    detected_signals: ['urgencia', 'numero_novo', 'pedido_pix', 'isolamento'],
    agent_decision: 'Trust Lock recomendado antes de qualquer transferência.',
    agent_decision_trace: [
      {step: 'Entrada recebida', detail: 'Conteúdo encaminhado por canal simples.'},
      {step: 'Sinais detectados', detail: 'Urgência, pedido financeiro e identidade não verificada.'},
      {step: 'Decisão', detail: 'Pausar ação e acionar responsável.'},
    ],
    trust_lock_status: 'recommended',
    trusted_circle_status: 'pending',
    proof_of_trust_status: 'not_started',
    recovery_status: 'not_needed',
    recommended_action: 'Confirmar com contato salvo antes de qualquer Pix.',
    status: 'open',
    created_at: '2026-01-01T10:00:00Z',
    updated_at: '2026-01-01T10:00:00Z',
  },
  {
    case_id: 'case-demo-002',
    protected_person_alias: 'Seu Joao',
    guardian_alias: 'Gabriel',
    source_channel: 'whatsapp_mock',
    received_content_summary: 'Link suspeito fingindo ser banco.',
    risk_score: 62,
    risk_level: 'medio',
    scam_category: 'link_suspeito',
    detected_signals: ['urgencia', 'link_externo'],
    agent_decision: 'Orientar pausa antes de clicar.',
    agent_decision_trace: [
      {step: 'Entrada recebida', detail: 'Canal simples.'},
      {step: 'Decisão', detail: 'Aguardar confirmação do responsável.'},
    ],
    trust_lock_status: 'not_needed',
    trusted_circle_status: 'notified',
    proof_of_trust_status: 'not_started',
    recovery_status: 'not_needed',
    recommended_action: 'Não clicar no link.',
    status: 'reviewing',
    created_at: '2026-01-02T14:20:00Z',
    updated_at: '2026-01-02T15:05:00Z',
  },
]

export async function getGuardianConsoleStatus(){
  try{
    const res = await fetch(`${API}/guardian-console/status`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as GuardianConsoleStatusResponse
  }catch{
    return {
      service: 'guardian-admin-case-console',
      mode: 'in_memory_demo',
      storage: 'mock_store',
      case_count: mockGuardianCases.length,
      auth_enabled: false,
      notifications_enabled: false,
      demo_note: 'Modo demonstração local.',
      __mock: true,
    }
  }
}

export async function getGuardianConsoleCases(){
  try{
    const res = await fetch(`${API}/guardian-console/cases`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as AdminCaseListResponse
  }catch{
    return {cases: mockGuardianCases, total: mockGuardianCases.length, __mock: true}
  }
}

export async function getGuardianConsoleCase(caseId:string){
  try{
    const res = await fetch(`${API}/guardian-console/cases/${caseId}`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as AdminCase
  }catch{
    const found = mockGuardianCases.find(item=>item.case_id === caseId)
    if(!found) throw new Error('not-found')
    return {...found, __mock: true}
  }
}

export async function patchGuardianCaseStatus(caseId:string, status:AdminCaseStatus){
  try{
    const res = await fetch(`${API}/guardian-console/cases/${caseId}/status`, {
      method: 'PATCH',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({status}),
    })
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as AdminCase
  }catch{
    const found = mockGuardianCases.find(item=>item.case_id === caseId)
    if(!found) throw new Error('not-found')
    return {...found, status, __mock: true}
  }
}

export async function getGuardianConsoleRealStatus(){
  const res = await fetch(`${API}/guardian-console/real/status`)
  if(!res.ok) throw new Error('guardian-console-real-status-error')
  return await res.json() as GuardianConsoleRealStatusResponse
}

export async function getGuardianConsoleRealCases(){
  const res = await fetch(`${API}/guardian-console/real/cases`)
  if(!res.ok) throw new Error('guardian-console-real-cases-error')
  return await res.json() as GuardianConsoleRealCaseListResponse
}

export async function getGuardianConsoleRealCase(caseId:string){
  const res = await fetch(`${API}/guardian-console/real/cases/${caseId}`)
  if(!res.ok) throw new Error('guardian-console-real-case-error')
  return await res.json() as GuardianConsoleRealCaseDetail
}

export async function postGuardianConsoleRealFeedback(caseId:string, payload:GuardianFeedbackPayload){
  const res = await fetch(`${API}/guardian-console/real/cases/${caseId}/feedback`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  })
  if(!res.ok) throw new Error('guardian-console-real-feedback-error')
  return await res.json() as GuardianFeedbackResponse
}

export async function postDualBotMockProtectedMessage(payload:DualBotInboundPayload){
  const res = await fetch(`${API}/dual-bot/mock/protected-message`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  })
  if(!res.ok) throw new Error('dual-bot-mock-protected-message-error')
  return await res.json() as DualBotFlowResponse
}

export async function getConsentStatus(protectedPersonId = 'demo-protected-person'){
  const res = await fetch(`${API}/consent/status?protected_person_id=${encodeURIComponent(protectedPersonId)}`)
  if(!res.ok) throw new Error('consent-status-error')
  return await res.json() as ConsentStatusResponse
}

export async function postConsentAccept(payload:ConsentAcceptPayload){
  const res = await fetch(`${API}/consent/accept`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  })
  if(!res.ok) throw new Error('consent-accept-error')
  return await res.json() as ConsentStatusResponse
}

export async function postConsentRevoke(payload:ConsentActionPayload){
  const res = await fetch(`${API}/consent/revoke`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  })
  if(!res.ok) throw new Error('consent-revoke-error')
  return await res.json() as ConsentStatusResponse
}

export async function postConsentBotActivate(payload:ConsentActionPayload){
  const res = await fetch(`${API}/consent/bot/activate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  })
  if(!res.ok) throw new Error('consent-bot-activate-error')
  return await res.json() as ConsentStatusResponse
}

export async function postConsentBotDeactivate(payload:ConsentActionPayload){
  const res = await fetch(`${API}/consent/bot/deactivate`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify(payload),
  })
  if(!res.ok) throw new Error('consent-bot-deactivate-error')
  return await res.json() as ConsentStatusResponse
}

export async function postConsentScopes(protectedPersonId:string, scopes:ConsentScope[]){
  const res = await fetch(`${API}/consent/scopes`, {
    method: 'POST',
    headers: {'Content-Type': 'application/json'},
    body: JSON.stringify({protected_person_id: protectedPersonId, scopes}),
  })
  if(!res.ok) throw new Error('consent-scopes-error')
  return await res.json() as ConsentStatusResponse
}

function normalizeRiskLevel(riskLevel:string){
  return (riskLevel || '').trim().toLowerCase()
}

export function escalationRecommendedForRisk(riskLevel:string){
  const key = normalizeRiskLevel(riskLevel)
  return key === 'alto' || key === 'critico' || key === 'crítico' || key.includes('crit')
}

function mockTrustedCircleEscalate(
  payload: TrustedCircleEscalatePayload,
): TrustedCircleEscalateResponse {
  const key = normalizeRiskLevel(payload.risk_level)
  const escalationId = `esc-mock-${Date.now().toString(36)}`
  const contacts = payload.trusted_contacts.length ? payload.trusted_contacts : ['Gabriel']
  const message = `${payload.protected_person_alias} recebeu uma mensagem com sinais de risco (${payload.reason}). Verifique antes de qualquer transferência.`

  if(key === 'baixo'){
    return {
      escalation_id: escalationId,
      status: 'not_escalated',
      message_to_guardian:
        'Risco baixo: escalonamento do círculo de confiança não é recomendado. Monitore o caso.',
      trusted_contacts: contacts,
      proof_of_trust_recommended: false,
      sent_real_notification: false,
      demo_note: 'Mock local — nenhum envio real.',
      case_id: payload.case_id,
      risk_level: payload.risk_level,
      escalation_recommended: false,
      __mock: true,
    }
  }

  if(key === 'medio' || key === 'médio'){
    return {
      escalation_id: escalationId,
      status: 'review_suggested',
      message_to_guardian: `Revisão sugerida para o responsável: ${message}`,
      trusted_contacts: contacts,
      proof_of_trust_recommended: true,
      sent_real_notification: false,
      demo_note: 'Risco médio — revisão do responsável sugerida (mock).',
      case_id: payload.case_id,
      risk_level: payload.risk_level,
      escalation_recommended: false,
      __mock: true,
    }
  }

  return {
    escalation_id: escalationId,
    status: 'simulated_notified',
    message_to_guardian: message,
    trusted_contacts: contacts,
    proof_of_trust_recommended: true,
    sent_real_notification: false,
    demo_note: 'Escalonamento simulado no MVP (mock local).',
    case_id: payload.case_id,
    risk_level: payload.risk_level,
    escalation_recommended: true,
    __mock: true,
  }
}

export async function getTrustedCircleStatus(){
  try{
    const res = await fetch(`${API}/trusted-circle/status`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as TrustedCircleStatusResponse
  }catch{
    return {
      service: 'trusted-circle-escalation',
      mode: 'in_memory_demo',
      real_notifications_enabled: false,
      escalation_count: 0,
      demo_note: 'Modo demonstração local — nenhum envio real.',
      __mock: true,
    }
  }
}

export async function postTrustedCircleEscalate(payload: TrustedCircleEscalatePayload){
  try{
    const res = await fetch(`${API}/trusted-circle/escalate`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    })
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as TrustedCircleEscalateResponse
  }catch{
    return mockTrustedCircleEscalate(payload)
  }
}

export async function getTrustedCircleEscalation(escalationId:string){
  try{
    const res = await fetch(`${API}/trusted-circle/escalations/${escalationId}`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as TrustedCircleEscalationRecord
  }catch{
    throw new Error('not-found')
  }
}

export function proofTrustRecommendedForRisk(riskLevel:string){
  return escalationRecommendedForRisk(riskLevel)
}

const mockProofSessions: Record<string, AssistedProofSessionResponse> = {}

function buildMockProofSteps(): ProofTrustStepItem[] {
  return [
    {
      id: 'do_not_reply',
      title: 'Não responder ao contato suspeito',
      status: 'completed',
      guidance: 'Não use o contato suspeito como fonte de verificação.',
    },
    {
      id: 'confirm_independent_channel',
      title: 'Confirmar pelo contato salvo',
      status: 'pending',
      guidance: 'Confirme por canal independente.',
    },
    {
      id: 'identity_challenge',
      title: 'Pergunta combinada',
      status: 'pending',
      guidance: 'Pergunta que só a pessoa real saberia.',
    },
    {
      id: 'confirm_request_real',
      title: 'Confirmar se o pedido é real',
      status: 'pending',
      guidance: 'Validar pedido financeiro sem usar o contato suspeito.',
    },
    {
      id: 'record_decision',
      title: 'Registrar decisão',
      status: 'pending',
      guidance: 'Registre o resultado (demo).',
    },
    {
      id: 'release_or_block',
      title: 'Liberar somente após confirmação',
      status: 'pending',
      guidance: 'Manter pausa se não houver confirmação segura.',
    },
  ]
}

function mockNextStepId(steps: ProofTrustStepItem[]){
  const pending = steps.find(s=>s.status === 'pending')
  return pending?.id || 'release_or_block'
}

function mockCreateProofSession(payload: AssistedProofSessionCreatePayload): AssistedProofSessionResponse {
  if(!proofTrustRecommendedForRisk(payload.risk_level)){
    throw new Error('risk-not-allowed')
  }
  const sessionId = `proof-mock-${Date.now().toString(36)}`
  const session: AssistedProofSessionResponse = {
    session_id: sessionId,
    case_id: payload.case_id,
    status: 'in_progress',
    current_step: 'confirm_independent_channel',
    steps: buildMockProofSteps(),
    final_decision: null,
    guardian_note: null,
    protected_person_alias: payload.protected_person_alias,
    guardian_alias: payload.guardian_alias,
    trusted_contact_alias: payload.trusted_contact_alias,
    suspected_request: payload.suspected_request,
    demo_note: 'Verificação segura simulada (mock local).',
    __mock: true,
  }
  mockProofSessions[sessionId] = session
  return session
}

function mockUpdateProofStep(
  sessionId: string,
  payload: AssistedProofStepUpdatePayload,
): AssistedProofSessionResponse {
  const session = mockProofSessions[sessionId]
  if(!session) throw new Error('not-found')

  const step = session.steps.find(s=>s.id === payload.step_id)
  if(!step || step.id !== session.current_step) throw new Error('step-order')

  step.status = payload.status || 'completed'
  if(payload.note) {
    step.note = payload.note
    session.guardian_note = session.guardian_note
      ? `${session.guardian_note}\n${payload.note}`
      : payload.note
  }

  if(payload.step_id === 'record_decision') {
    if(!payload.final_decision) throw new Error('decision-required')
    session.final_decision = payload.final_decision
  }

  session.current_step = mockNextStepId(session.steps)

  if(payload.step_id === 'release_or_block' && session.final_decision) {
    session.status = session.final_decision
  }

  mockProofSessions[sessionId] = session
  return {...session}
}

export async function postAssistedProofSession(payload: AssistedProofSessionCreatePayload){
  try{
    const res = await fetch(`${API}/proof-trust/assisted-session`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    })
    if(!res.ok){
      if(res.status === 400) throw new Error('proof-risk-not-allowed')
      throw new Error('api-error')
    }
    const data = await res.json()
    return {...data, __mock: false} as AssistedProofSessionResponse
  }catch(error){
    if(error instanceof Error && error.message === 'proof-risk-not-allowed') throw error
    try{
      return mockCreateProofSession(payload)
    }catch{
      throw error
    }
  }
}

export async function getAssistedProofSession(sessionId: string){
  try{
    const res = await fetch(`${API}/proof-trust/assisted-session/${sessionId}`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as AssistedProofSessionResponse
  }catch{
    const session = mockProofSessions[sessionId]
    if(!session) throw new Error('not-found')
    return session
  }
}

export async function postAssistedProofSessionStep(
  sessionId: string,
  payload: AssistedProofStepUpdatePayload,
){
  try{
    const res = await fetch(`${API}/proof-trust/assisted-session/${sessionId}/step`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    })
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as AssistedProofSessionResponse
  }catch{
    return mockUpdateProofStep(sessionId, payload)
  }
}

export async function getEvolutionStatus(autoReconnect = false){
  const res = await authFetch(`/api/channels/evolution/status${autoReconnect ? '?auto_reconnect=true' : ''}`)
  return await res.json() as EvolutionConnectionState
}

export async function getEvolutionQr(){
  const res = await authFetch('/api/channels/evolution/qr')
  return await res.json() as EvolutionConnectionState
}

export async function postEvolutionReconnect(){
  const res = await authFetch('/api/channels/evolution/reconnect', { method: 'POST' })
  return await res.json() as EvolutionConnectionState
}

export interface TrustedContactSettings {
  protected_number: string
  trusted_contact: string
  dry_run: boolean
  beta_real_send_enabled: boolean
}

export async function getTrustedContactSettings(): Promise<TrustedContactSettings> {
  const res = await authFetch('/settings/trusted-contact')
  return await res.json() as TrustedContactSettings
}

export async function putTrustedContactSettings(
  update: {protected_number?: string, trusted_contact?: string},
): Promise<TrustedContactSettings> {
  const res = await authFetch('/settings/trusted-contact', {
    method: 'PUT',
    body: JSON.stringify(update),
  })
  return await res.json() as TrustedContactSettings
}

export async function postOCRPreview(source:string, content:string){
  try{
    const res = await fetch(`${API}/connectors/ocr-preview`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({source, content})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch{
    return {...createMockOCRPreview(content), __mock: true}
  }
}
