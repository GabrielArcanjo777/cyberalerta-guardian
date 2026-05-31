import { AnalyzePayload, IntakePayload, RecoveryPayload, RedactPreviewPayload } from './types'
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
