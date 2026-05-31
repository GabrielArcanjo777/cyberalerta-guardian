export const mockAnalyzeResult = {
  risk_score: 98,
  risk_level: 'critical',
  dangerous_action: 'pix',
  scam_type: 'falso familiar pedindo Pix',
  scam_stage: 'acao perigosa iminente',
  manipulations: ['vinculo familiar','urgencia','numero novo','pedido financeiro','pedido para nao ligar'],
  trust_evidence: {confidence:94, evidence:['Pedido de Pix','Numero novo ou identidade nao verificada','Urgencia emocional','Pedido para nao ligar','Alegacao de parentesco']},
  agent_decision_trace: [
    {
      agent:'IntentDetectionAgent',
      input_summary:'Mensagem de WhatsApp com solicitacao de Pix',
      decision:'Acao perigosa detectada: Pix',
      confidence:0.98,
      evidence:['Pix','pagar conta urgente','urgencia'],
      next_action:'Enviar para ManipulationAnalysisAgent'
    },
    {
      agent:'ManipulationAnalysisAgent',
      input_summary:'Mensagem avaliada em busca de pressao emocional e isolamento',
      decision:'Padroes de manipulacao detectados: vinculo familiar, urgencia, numero novo, pedido financeiro, pedido para nao ligar',
      confidence:0.95,
      evidence:['uso de relacao familiar','pressao de tempo','identidade nao confirmada','tentativa de evitar verificacao'],
      next_action:'Enviar para ScamClassificationAgent'
    },
    {
      agent:'ScamClassificationAgent',
      input_summary:'Canal, acao solicitada e sinais de contexto familiar',
      decision:'Classificacao defensiva: falso familiar pedindo Pix',
      confidence:0.92,
      evidence:['Pix','whatsapp','vinculo familiar, urgencia, numero novo'],
      next_action:'Enviar para ScamStageAgent'
    },
    {
      agent:'RiskScoringAgent',
      input_summary:'Acao perigosa, canal e sinais de manipulacao consolidados',
      decision:'Risco critico calculado: 98/100 (critical)',
      confidence:0.96,
      evidence:['score=98','nivel=critical','pedido financeiro sensivel'],
      next_action:'Enviar para TrustEvidenceAgent'
    },
    {
      agent:'TrustEvidenceAgent',
      input_summary:'Evidencias defensivas que sustentam o bloqueio preventivo',
      decision:'Evidencias de risco organizadas para verificacao humana',
      confidence:0.94,
      evidence:['Pedido de Pix','Numero novo ou identidade nao verificada','Urgencia emocional','Pedido para nao ligar'],
      next_action:'Enviar para TrustLockAgent'
    },
    {
      agent:'TrustLockAgent',
      input_summary:'Score final e tipo de golpe analisados antes da acao',
      decision:'Trust Lock ativado',
      confidence:0.99,
      evidence:['nivel=critical','score=98','confirmacao por outro canal exigida'],
      next_action:'Enviar para TrustedCircleAgent'
    },
    {
      agent:'TrustedCircleAgent',
      input_summary:'Contato de confianca informado: Gabriel',
      decision:'Alerta familiar recomendado',
      confidence:0.93,
      evidence:['contato=Gabriel','relacao=neto','nivel=critical'],
      next_action:'Gerar Decision Ledger e relatorio da demo'
    }
  ],
  decision_ledger:{
    final_decision:'Trust Lock ativado',
    decision_reason:'Pedido urgente de Pix vindo de numero novo se passando por familiar',
    safety_level:'critical',
    escalation_required:true,
    audit_summary:'O sistema detectou acao financeira iminente, vinculo familiar, urgencia, numero novo e tentativa de isolamento antes de permitir a decisao do usuario.'
  },
  ai_mode:{
    use_llm:false,
    provider:'mock',
    fallback_enabled:true,
    safety_policy:'enabled',
    llm_enrichment_applied:false
  },
  ml_analysis:{
    classe:'golpe',
    confianca:0.86,
    categoria:'golpe_pix',
    risco:'alto',
    score:100,
    sinais_detectados:['urgencia','pedido_pix','numero_novo','pedido_para_nao_ligar'],
    explicacao:'Resultado demonstrativo do ML Scam Intelligence para texto suspeito.',
    ml_used:true,
    rules_used:true,
    url_analysis_used:false
  },
  url_analysis:null,
  trust_lock:{activated:true,title:'TRUST LOCK ATIVADO',reason:'Pedido urgente de Pix vindo de numero nao verificado se passando por familiar.',message:'Essa acao esta em quarentena ate confirmacao por outro canal.'},
  proof_of_trust:['Nao responda o numero novo.','Ligue para o numero antigo da pessoa.','Confirme por chamada de voz.','Nao faca Pix ate confirmar por outro canal.'],
  intervention_playbook:{immediate_action:'Pare agora e nao faca Pix.',verification:'Confirme a identidade por outro canal.',family_escalation:'Gabriel deve ligar para a pessoa imediatamente.',recovery_fallback:'Se o Pix ja foi feito, ativar Recovery Mode.'},
  trusted_circle_alert:{
    should_alert:true,
    contact_name:'Gabriel',
    relationship:'neto',
    urgency:'critical',
    person_at_risk:'Dona Lucia',
    risk_summary:'Dona Lucia recebeu um pedido urgente de Pix de um numero novo dizendo ser familiar.',
    scam_type:'falso familiar pedindo Pix',
    recommended_action:'Ligue para Dona Lucia agora antes que ela faca qualquer pagamento.',
    suggested_message:'Vo, nao faca o Pix. Sou eu, Gabriel. Vamos confirmar juntos.',
    status:'alert_generated',
    is_simulated:true,
    message:'Gabriel, Dona Lucia recebeu um pedido urgente de Pix de um numero novo dizendo ser familiar. Ligue para ela agora antes de qualquer pagamento.'
  },
  user_message:'Dona Lucia, pare agora. Nao faca Pix. Ligue para o numero antigo do seu neto.',
  report:{title:'Relatorio CyberAlerta Guardian',summary:'Possivel golpe do falso familiar com pedido de Pix urgente.',agent_decision:'Trust Lock ativado e contato de confianca alertado.',recommended_next_step:'Confirmar por ligacao no numero antigo antes de qualquer pagamento.'}
}

export const mockMLTextResult = {
  classe:'golpe',
  confianca:0.86,
  categoria:'golpe_pix',
  risco:'alto',
  score:100,
  sinais_detectados:['urgencia','pedido_pix','numero_novo'],
  explicacao:'Resultado demonstrativo. O backend nao respondeu, entao estes dados sao simulados.',
  ml_used:false,
  rules_used:true,
}

export const mockMLUrlResult = {
  url:'https://nubank-seguranca-verificacao.xyz/login?token=abc',
  risco:'alto',
  score:80,
  categoria:'possivel_phishing',
  sinais_detectados:['dominio_suspeito','palavra_sensivel_login','parametros_sensiveis','imitacao_de_marca'],
  brand_impersonation:{
    brand_impersonation_detected:true,
    brand:'Nubank',
    message:'Possivel tentativa de imitacao da marca Nubank',
    matched_term:'nubank',
  },
  explicacao:'Resultado demonstrativo. A URL apresenta sinais frequentemente associados a phishing.',
  rules_used:true,
  external_api_used:false,
}

export const mockRecoveryResult = {
  severity:'high',
  summary:'Foi identificado possivel dano financeiro por Pix ou transferencia.',
  recovery_plan:[
    {
      priority:'immediate',
      title:'Salve as evidencias',
      description:'Tire prints da conversa, salve comprovante, numero, chave Pix, valor e horario.',
      category:'financial'
    },
    {
      priority:'immediate',
      title:'Avise o banco',
      description:'Entre em contato com seu banco pelos canais oficiais e informe que pode ter ocorrido fraude.',
      category:'financial'
    },
    {
      priority:'high',
      title:'Organize dados para eventual denuncia',
      description:'Anote valor, data, horario, chave Pix ou dados do recebedor e protocolo do banco.',
      category:'financial'
    }
  ],
  evidence_to_save:['prints da conversa','comprovante do Pix ou transferencia','chave Pix ou dados do recebedor','data, horario e valor'],
  accounts_to_secure:['conta bancaria','e-mail','WhatsApp'],
  what_not_to_do:['nao continue conversando com o contato suspeito','nao envie novos dados','nao faca outro pagamento'],
  disclaimer:'Esta e uma orientacao preventiva e educativa. Em caso de prejuizo real, procure seu banco, canais oficiais e autoridades competentes.'
}

export function createMockRedactPreview(content:string){
  let redacted = content
  const items:string[] = []
  const apply = (pattern:RegExp,replacement:string,label:string) => {
    if(pattern.test(redacted) && !items.includes(label)){
      items.push(label)
    }
    redacted = redacted.replace(pattern,replacement)
  }

  apply(/(https?:\/\/[^\s?)]+)\?[^)\s]+/g,'$1?[PARAMS_MASCARADOS]','link_params')
  apply(/\b\d{3}\.?\d{3}\.?\d{3}-?\d{2}\b/g,'[CPF_MASCARADO]','cpf')
  apply(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}\b/g,'[EMAIL_MASCARADO]','email')
  apply(/(?<!\d)(?:\(?\d{2}\)?\s?)?\d{4,5}-?\d{4}(?!\d)/g,'[TELEFONE_MASCARADO]','phone')
  apply(/\b\d{8,}\b/g,'[NUMERO_MASCARADO]','long_number')

  return {
    original_length: content.length,
    redacted_content: redacted,
    items_masked: items,
  }
}

export function createMockIntakeAnalyze(content:string, channel='manual_text'){
  const preview = createMockRedactPreview(content)
  return {
    analysis: mockAnalyzeResult,
    privacy_report: {
      consent_verified: true,
      redaction_applied: true,
      channel,
      data_minimization: true,
      sensitive_items_masked: preview.items_masked,
      monitoring: false,
      message: 'A analise foi feita apenas com o conteudo enviado voluntariamente pelo usuario.',
    },
    redacted_content: preview.redacted_content,
  }
}
