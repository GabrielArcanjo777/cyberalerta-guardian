export const impactMetrics = {
  dangerous_decisions_paused: 12,
  pix_attempts_interrupted: 8,
  family_alerts_generated: 5,
  recovery_plans_created: 4,
  scenarios_analyzed: 22,
  manipulation_tactics_detected: 6,
  critical_cases_identified: 9,
  trust_locks_activated: 11,
}

export const manipulationPatterns = [
  {label: 'Urgencia', count: 18},
  {label: 'Medo', count: 7},
  {label: 'Falso vinculo familiar', count: 12},
  {label: 'Autoridade falsa', count: 6},
  {label: 'Isolamento', count: 10},
  {label: 'Pedido financeiro', count: 15},
  {label: 'Pedido de senha/codigo', count: 9},
  {label: 'Pedido de documento', count: 5},
]

export const globalThreatPatterns = [
  {label: 'urgency', count: 18},
  {label: 'fear', count: 7},
  {label: 'false authority', count: 11},
  {label: 'fake family identity', count: 12},
  {label: 'isolation', count: 10},
  {label: 'financial pressure', count: 15},
  {label: 'credential request', count: 9},
  {label: 'document request', count: 5},
  {label: 'remote access request', count: 6},
  {label: 'OTP/code request', count: 8},
]

export const globalApplicability = [
  {region: 'Brasil', focus: 'Pix + WhatsApp scams'},
  {region: 'United States', focus: 'gift cards + fake tech support'},
  {region: 'Europe', focus: 'banking phishing + delivery scams'},
  {region: 'India', focus: 'UPI/OTP/KYC scams'},
  {region: 'Africa', focus: 'mobile money scams'},
  {region: 'Global', focus: 'credentials, links, documents, remote access apps'},
]

export const demonstratedScenarios = [
  'Falso filho pedindo Pix',
  'Falso banco com link',
  'Pedido de codigo SMS',
  'Falso suporte pedindo app remoto',
  'Falso emprego pedindo taxa',
]

export const impactNote = 'Dados simulados para demonstracao do MVP.'
