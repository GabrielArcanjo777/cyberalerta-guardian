import type {ConnectorResult, ConnectorStatus, OCRPreviewResponse} from './types'

export const mockConnectorStatuses: ConnectorStatus[] = [
  {name:'URL Intelligence', provider:'mock_url_intelligence', mode:'mock', enabled:true, privacy:'local/mock analysis'},
  {name:'OCR', provider:'mock_ocr', mode:'mock', enabled:true, privacy:'no real image sent'},
  {name:'Email Opt-in', provider:'mock_email', mode:'mock', enabled:true, privacy:'no real mailbox access'},
  {name:'Browser Extension', provider:'mock_browser_extension', mode:'mock', enabled:true, privacy:'selected URL/text only roadmap'},
  {name:'Messaging Opt-in', provider:'mock_messaging', mode:'mock', enabled:true, privacy:'no private messages read'},
]

export function createMockURLCheck(url:string): ConnectorResult{
  const lower = url.toLowerCase()
  const signals:string[] = []
  if(lower.includes('login')) signals.push('URL contem palavra sensivel: login')
  if(lower.includes('token') || lower.includes('?')) signals.push('URL contem parametros que podem carregar token')
  if(lower.includes('pix') || lower.includes('banco') || lower.includes('bank')) signals.push('dominio potencialmente suspeito')
  if(lower.startsWith('http://')) signals.push('URL usa HTTP sem criptografia')
  if(signals.length === 0) signals.push('nenhum sinal forte no modo mock/local')

  return {
    provider:'mock_url_intelligence',
    status:'mock',
    risk_signals:signals,
    raw_summary:'Analise local/mock de URL para demonstracao. Nenhuma API externa foi chamada.',
    safe_to_display:true,
    privacy_note:'Analise local/mock. Nenhum dado foi enviado a provedor externo.',
    confidence:Math.min(0.95, 0.38 + signals.length * 0.1),
    metadata:{external_lookup:false, input:url},
  }
}

export function createMockOCRPreview(content:string): OCRPreviewResponse{
  return {
    provider:'mock_ocr',
    status:'mock',
    extracted_text:content || 'Texto extraido simulado de um print suspeito: pedido urgente de Pix.',
    risk_signals:['OCR simulado em modo MVP'],
    raw_summary:'OCR simulado para demonstracao. Azure Vision ou provedor equivalente nao foi chamado.',
    safe_to_display:true,
    privacy_note:'OCR real nao ativado. Nenhuma imagem foi enviada a provedor externo.',
    confidence:0.72,
    metadata:{source:'mock', external_lookup:false},
  }
}
