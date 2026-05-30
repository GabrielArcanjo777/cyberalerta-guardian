import { AnalyzePayload, RecoveryPayload } from './types'
import { mockAnalyzeResult, mockRecoveryResult } from './mockData'

const API = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000'

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
