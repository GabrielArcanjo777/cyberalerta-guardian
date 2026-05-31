import {
  AnalyzePayload,
  IntakePayload,
  RecoveryPayload,
  RedactPreviewPayload,
  ProtectedResponseGeneratePayload,
  ProtectedResponseGenerateResponse,
  SimpleChannelStatusResponse,
  SimpleChannelSubmitPayload,
  SimpleChannelSubmitResponse,
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
