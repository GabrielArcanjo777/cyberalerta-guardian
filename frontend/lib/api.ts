import {
  AdminCase,
  AdminCaseListResponse,
  AdminCaseStatus,
  AnalyzePayload,
  GuardianConsoleStatusResponse,
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

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8001'

export async function analyzeMessage(payload: AnalyzePayload){
  try{
    const res = await fetch(`${API}/analyze`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...mockAnalyzeResult, __mock: true}
  }
}

export async function postRecovery(payload: RecoveryPayload){
  try{
    const res = await fetch(`${API}/recovery`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...mockRecoveryResult, __mock: true}
  }
}

export async function analyzeTextML(texto:string){
  try{
    const res = await fetch(`${API}/analisar`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({texto})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...mockMLTextResult, __mock: true}
  }
}

export async function analyzeURLML(url:string){
  try{
    const res = await fetch(`${API}/analisar-url`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...mockMLUrlResult, url, __mock: true}
  }
}

export async function postRedactPreview(payload: RedactPreviewPayload){
  try{
    const res = await fetch(`${API}/intake/redact-preview`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...createMockRedactPreview(payload.content), __mock: true}
  }
}

export async function postIntakeAnalyze(payload: IntakePayload){
  try{
    const res = await fetch(`${API}/intake/analyze`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify(payload)})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...createMockIntakeAnalyze(payload.content, payload.channel), __mock: true}
  }
}

export async function getConnectorsStatus(){
  try{
    const res = await fetch(`${API}/connectors/status`)
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {connectors: mockConnectorStatuses, __mock: true}
  }
}

export async function postURLCheck(url:string){
  try{
    const res = await fetch(`${API}/connectors/url-check`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({url})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
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

export async function postProtectedResponseGenerate(payload: ProtectedResponseGeneratePayload){
  try{
    const res = await fetch(`${API}/protected-response/generate`, {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify(payload),
    })
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false} as ProtectedResponseGenerateResponse
  }catch{
    return createMockProtectedResponse(payload)
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
    protected_person_short_reply: 'Não faça Pix agora. Essa mensagem tem sinais de golpe e estou avisando Gabriel.',
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

export async function postOCRPreview(source:string, content:string){
  try{
    const res = await fetch(`${API}/connectors/ocr-preview`, {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({source, content})})
    if(!res.ok) throw new Error('api-error')
    const data = await res.json()
    return {...data, __mock: false}
  }catch(e){
    return {...createMockOCRPreview(content), __mock: true}
  }
}
