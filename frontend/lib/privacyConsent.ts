export type PrivacyChecklistItem = {
  id: string
  label: string
  detail: string
}

export const privacyConsentChecklist: PrivacyChecklistItem[] = [
  {
    id: 'voluntary',
    label: 'Voluntário',
    detail: 'A análise só começa quando alguém encaminha conteúdo de forma consciente.',
  },
  {
    id: 'minimized',
    label: 'Minimizado',
    detail: 'Preferimos trechos, aliases e metadados — não conversas inteiras nem dados desnecessários.',
  },
  {
    id: 'explainable',
    label: 'Explicável',
    detail: 'Sinais, risco e próxima ação são mostrados de forma compreensível.',
  },
  {
    id: 'actionable',
    label: 'Acionável',
    detail: 'O fluxo orienta pausa, verificação e decisão — não vigilância passiva.',
  },
  {
    id: 'human_loop',
    label: 'Humano no loop',
    detail: 'O responsável confirma passos críticos; o sistema não decide sozinho.',
  },
]

export const guardianDoesList = [
  'Analisa conteúdo encaminhado voluntariamente (texto, link ou trecho).',
  'Calcula risco e explica sinais de manipulação ou urgência.',
  'Orienta pausa protetiva (Trust Lock) antes de Pix, clique ou credencial.',
  'Cria caso rastreável para o responsável no Guardian Console.',
  'Recomenda verificação segura por canal independente (Proof of Trust).',
  'Pode sugerir escalonamento simulado ao círculo de confiança no MVP.',
]

export const guardianDoesNotList = [
  'Não monitora WhatsApp, SMS ou conversas privadas automaticamente.',
  'Não lê mensagens em segundo plano nem instala “espionagem” no aparelho.',
  'Não pede senha, código SMS, Pix, CPF ou documentos reais na demo.',
  'Não realiza transferências nem bloqueia contas bancárias.',
  'Não substitui banco, polícia, advogado ou canal oficial.',
  'Não envia notificações reais no MVP (tudo é simulado quando indicado).',
  'Não usa dados reais sem consentimento explícito em produção futura.',
]

export const privacyDesignFlow = [
  {title: 'Entrada voluntária', body: 'Pessoa protegida ou responsável escolhe o que compartilhar.'},
  {title: 'Minimização e redaction', body: 'CPF, telefone e chaves podem ser mascarados antes da análise.'},
  {title: 'Análise defensiva', body: 'Sinais de golpe e engenharia social — sem vigilância contínua.'},
  {title: 'Caso para o responsável', body: 'Familiar, cuidador ou instituição age com contexto — não para espionar.'},
  {title: 'Ação humana', body: 'Verificação, Trust Lock, Proof of Trust e decisão registrada.'},
  {title: 'Relatório controlado', body: 'Documentação orientativa; não é denúncia automática.'},
]

export const mvpLimitationsList = [
  'WhatsApp e chatbot são mock — não há conexão real com o aplicativo.',
  'Dados de casos, alertas e métricas são demonstrativos (in-memory na demo).',
  'Provedores externos ficam mock ou desativados por padrão.',
  'Integrações reais exigiriam opt-in, termos claros e configuração institucional.',
  'Não prometemos conformidade legal completa (LGPD) neste MVP — apenas princípios de design.',
]

export const intakePrivacyNotice =
  'Encaminhe apenas o trecho suspeito, com seu consentimento. O MVP não conecta WhatsApp real e não monitora conversas. Não envie senhas, códigos, CPF ou documentos reais — se aparecerem na mensagem, o Guardian orientará a não compartilhar.'

export const familyConsolePrivacyNotice =
  'Este painel é para proteção assistida, não vigilância. Você vê casos que foram compartilhados voluntariamente. Decisões críticas exigem confirmação humana; nenhum envio real ocorre no MVP.'

export const assistedDemoPrivacyNotice =
  'Simulação completa com dados fictícios. Sem monitoramento automático, sem WhatsApp real e sem notificações reais.'

export const reportPrivacyNotice =
  'O relatório serve para documentação e orientação da família ou instituição. Não é denúncia automática, não aciona autoridades e não substitui canais oficiais. O responsável decide os próximos passos.'

export const recoveryPrivacyNotice =
  'Plano educativo e organizado por prioridade. Não substitui banco, polícia, advogado ou suporte oficial. Não envie documentos, senhas ou códigos reais nesta tela.'

export const beforePixPrivacyNotice =
  'Análise apenas do texto que você cola ou simula aqui — sem leitura invisível de conversas. Use mensagens de demonstração; não compartilhe credenciais reais.'
