export const mockAnalyzeResult = {
  risk_score: 98,
  risk_level: 'critical',
  dangerous_action: 'pix',
  scam_type: 'falso familiar pedindo Pix',
  scam_stage: 'acao perigosa iminente',
  manipulations: ['vinculo familiar','urgencia','numero novo','pedido financeiro','pedido para nao ligar'],
  trust_evidence: {confidence:94, evidence:['Pedido de Pix','Numero novo ou identidade nao verificada','Urgencia emocional','Pedido para nao ligar','Alegacao de parentesco']},
  agent_decision_trace: [
    {agent:'IntentDetectionAgent',decision:'Acao perigosa detectada: Pix'},
    {agent:'ManipulationAnalysisAgent',decision:'Manipulacoes detectadas: vinculo familiar, urgencia, isolamento'},
    {agent:'RiskScoringAgent',decision:'Risco critico calculado'},
    {agent:'TrustLockAgent',decision:'Trust Lock ativado'},
    {agent:'TrustedCircleAgent',decision:'Alerta familiar recomendado'}
  ],
  trust_lock:{activated:true,title:'TRUST LOCK ATIVADO',reason:'Pedido urgente de Pix vindo de numero nao verificado se passando por familiar.',message:'Essa acao esta em quarentena ate confirmacao por outro canal.'},
  proof_of_trust:['Nao responda o numero novo.','Ligue para o numero antigo da pessoa.','Confirme por chamada de voz.','Nao faca Pix ate confirmar por outro canal.'],
  intervention_playbook:{immediate_action:'Pare agora e nao faca Pix.',verification:'Confirme a identidade por outro canal.',family_escalation:'Gabriel deve ligar para a pessoa imediatamente.',recovery_fallback:'Se o Pix ja foi feito, ativar Recovery Mode.'},
  trusted_circle_alert:{should_alert:true,contact_name:'Gabriel',message:'Gabriel, Dona Lucia recebeu um pedido urgente de Pix de um numero novo...'},
  user_message:'Dona Lucia, pare agora. Nao faca Pix. Ligue para o numero antigo do seu neto.',
  report:{title:'Relatorio CyberAlerta Guardian',summary:'Possivel golpe do falso familiar com pedido de Pix urgente.',agent_decision:'Trust Lock ativado e contato de confianca alertado.',recommended_next_step:'Confirmar por ligacao no numero antigo antes de qualquer pagamento.'}
}

export const mockRecoveryResult = {checklist:['Nenhuma acao de risco confirmada. Monitore e informe familiares.']}
