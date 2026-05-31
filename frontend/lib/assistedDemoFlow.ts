export type AssistedDemoStepId =
  | 'suspicious-message'
  | 'forward'
  | 'short-reply'
  | 'console-case'
  | 'trust-lock'
  | 'trusted-circle'
  | 'proof-of-trust'
  | 'decision-trace'
  | 'report'

export const assistedDemoMeta = {
  title: 'Demo de proteção assistida',
  subtitle:
    'Veja como uma mensagem suspeita encaminhada por uma pessoa protegida vira um caso rastreável para o responsável.',
  protectedPerson: 'Dona Lucia',
  guardian: 'Gabriel',
  channel: 'WhatsApp mock',
  scamType: 'Mensagem de falso familiar',
  suspiciousMessage: 'Oi mãe, troquei de número. Preciso fazer um Pix urgente. Não liga agora.',
  forwardNote: 'Conteúdo recebido de forma voluntária pelo canal simples.',
  shortReply:
    'Não faça Pix agora. Essa mensagem tem sinais de golpe. Estou avisando seu contato de confiança.',
  caseId: 'case-demo-001',
  riskScore: 87,
  riskLevel: 'alto',
  scamCategory: 'golpe_pix',
  signals: [
    'urgência',
    'número novo',
    'pedido de Pix',
    'isolamento',
    'identidade não verificada',
  ],
  trustLockTitle: 'Pausa protetiva ativada',
  trustLockBody:
    'O sistema não decide pela pessoa; ele pausa e orienta verificação segura antes de qualquer transferência.',
  trustedCircleNote: 'Gabriel seria avisado para verificar o caso.',
  trustedCircleDisclaimer: 'Simulado no MVP — nenhum envio real.',
}

export const proofOfTrustChecklist = [
  'Não responder ao número suspeito',
  'Confirmar pelo contato salvo',
  'Verificar identidade por pergunta combinada',
  'Confirmar se o pedido financeiro é real',
  'Registrar decisão no console',
]

export const decisionTraceTimeline = [
  {step: 'Entrada voluntária recebida', detail: 'Dona Lucia encaminhou o trecho pelo canal simples com consentimento.'},
  {step: 'Sinais de engenharia social detectados', detail: 'Urgência, número novo, pedido de Pix e isolamento ("não liga").'},
  {step: 'Risco calculado', detail: 'Score 87/100 — categoria golpe_pix, nível alto.'},
  {step: 'Trust Lock recomendado', detail: 'Pausa protetiva antes de qualquer transferência.'},
  {step: 'Responsável acionado', detail: 'Caso aberto para Gabriel no Guardian Console (simulado).'},
  {step: 'Relatório disponível', detail: 'Resumo auditável para família, instituição ou piloto.'},
]

export const reportPreview = {
  title: 'Relatório de intervenção — caso demo',
  summary:
    'Mensagem simulada de falso familiar pedindo Pix urgente. Guardian recomendou pausa, resposta curta à pessoa protegida e encaminhamento ao responsável.',
  risk: 'Alto (87/100)',
  signals: assistedDemoMeta.signals.join(', '),
  actionTaken: 'Trust Lock recomendado · Trusted Circle simulado · Proof of Trust sugerido',
  recommendation: 'Confirmar identidade por telefone salvo antes de qualquer Pix.',
  finalStatus: 'Em análise pelo responsável (demo)',
}

export const assistedDemoSteps: Array<{id: AssistedDemoStepId, label: string, order: number}> = [
  {id: 'suspicious-message', label: 'Mensagem suspeita', order: 1},
  {id: 'forward', label: 'Encaminhamento', order: 2},
  {id: 'short-reply', label: 'Resposta curta', order: 3},
  {id: 'console-case', label: 'Caso no console', order: 4},
  {id: 'trust-lock', label: 'Trust Lock', order: 5},
  {id: 'trusted-circle', label: 'Trusted Circle', order: 6},
  {id: 'proof-of-trust', label: 'Proof of Trust', order: 7},
  {id: 'decision-trace', label: 'Trilha da decisão', order: 8},
  {id: 'report', label: 'Relatório', order: 9},
]
