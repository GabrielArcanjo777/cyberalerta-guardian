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
  whatsappUserMessage:
    'Pare agora. Não faça Pix, não clique em links e não envie códigos. Esta mensagem tem sinais fortes de risco: urgência, número novo e pedido de Pix. Confirme por ligação usando um número que você já tinha salvo.',
  whatsappTrustedContactMessage:
    'Alerta CyberAlerta Guardian: Dona Lucia recebeu uma mensagem com sinais de risco. Risco: alto. Sinais: urgência, número novo e pedido de Pix. Ligue para ela usando um número conhecido antes de qualquer pagamento ou clique.',
  shortExplanation:
    'O sistema identificou pressa, número novo, pedido de dinheiro e orientação para não ligar. Esses sinais justificam pausar a ação e confirmar por canal confiável.',
  nextBestAction: 'Não pagar agora. Confirmar por ligação usando o contato antigo salvo.',
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
  {
    id: 'do_not_reply',
    title: 'Não responder ao contato suspeito',
    guidance: 'Não use o contato suspeito — o responsável conduz a verificação.',
    status: 'completed' as const,
  },
  {
    id: 'confirm_independent_channel',
    title: 'Confirmar pelo contato salvo',
    guidance: 'Confirme por canal independente (telefone salvo ou presencial).',
    status: 'pending' as const,
  },
  {
    id: 'identity_challenge',
    title: 'Pergunta combinada',
    guidance: 'Pergunta que só a pessoa real saberia responder.',
    status: 'pending' as const,
  },
  {
    id: 'confirm_request_real',
    title: 'Confirmar se o pedido financeiro é real',
    guidance: 'Validar o pedido de Pix sem usar o número suspeito.',
    status: 'pending' as const,
  },
  {
    id: 'record_decision',
    title: 'Registrar decisão',
    guidance: 'O responsável registra o resultado no Guardian Console.',
    status: 'pending' as const,
  },
  {
    id: 'release_or_block',
    title: 'Liberar somente após confirmação',
    guidance: 'Manter pausa protetiva se não houver confirmação segura.',
    status: 'pending' as const,
  },
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
