import {
  AnalyzePayload,
  IntakePayload,
  RecoveryPayload,
  RedactPreviewPayload,
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

function createMockSimpleChannelSubmit(payload: SimpleChannelSubmitPayload): SimpleChannelSubmitResponse {
  const highRisk = /pix|urgente|troquei de numero/i.test(payload.content)
  return {
    channel_case_id: `ch-mock-${Date.now().toString(36)}`,
    risk_level: highRisk ? 'alto' : 'medio',
    simple_reply: highRisk
      ? 'Nao faca Pix agora. Essa mensagem tem sinais de golpe. Estou avisando seu contato de confianca.'
      : `${payload.protected_person_alias}, espere e confirme por outro canal antes de agir.`,
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
