export type PilotPackage = {
  id:string
  title:string
  audience:string
  objective:string
  duration:string
  flow:string[]
  metrics:string[]
  requirements:string[]
  risks:string[]
}

export type PrivacySafeMetric = {
  label:string
  value:string
  description:string
}

export type AccessibilityChecklistItem = {
  label:string
  detail:string
}

export const pilotPackages:PilotPackage[] = [
  {
    id:'family-7-day',
    title:'7-day family pilot',
    audience:'Famílias com idosos, cuidadores e contatos de confiança',
    objective:'Testar se a pausa protetiva reduz decisões por impulso antes de Pix, links e pedidos de código.',
    duration:'7 dias',
    flow:[
      'Orientar a família em uma chamada curta de 20 minutos.',
      'Simular 3 cenários comuns com mensagens de demonstração.',
      'Usar Before Pix, Family Console, Help Network e Recovery Mode em casos simulados.',
      'Coletar feedback anônimo sobre clareza, medo reduzido e facilidade de uso.',
    ],
    metrics:[
      'Número de análises simuladas.',
      'Trust Locks ativados em cenários de alto risco.',
      'Planos de recuperação criados sem conteúdo privado.',
      'Tempo médio até a família entender a ação recomendada.',
    ],
    requirements:[
      'Consentimento verbal ou escrito dos participantes.',
      'Nenhum telefone real inserido no sistema.',
      'Uso apenas de mensagens fictícias ou anonimizadas.',
    ],
    risks:[
      'Participantes podem confundir MVP com envio real de alerta.',
      'O piloto precisa reforçar que a ferramenta orienta, mas não substitui canais oficiais.',
    ],
  },
  {
    id:'school-workshop',
    title:'school workshop pilot',
    audience:'Escolas, coordenadores, professores, alunos e responsáveis',
    objective:'Validar o Guardian como material de educação digital para phishing, falso suporte e pedido de código.',
    duration:'1 oficina de 60 a 90 minutos',
    flow:[
      'Apresentar golpes comuns em linguagem simples.',
      'Rodar cenários de phishing e pedido de código no modo demo.',
      'Mostrar como preservar evidências sem expor o aluno.',
      'Encerrar com checklist de segurança para alunos e familiares.',
    ],
    metrics:[
      'Cenários analisados durante a oficina.',
      'Tipos de risco identificados pela turma.',
      'Perguntas frequentes registradas sem nomes.',
      'Nível de compreensão antes/depois por formulário anônimo.',
    ],
    requirements:[
      'Autorização da escola para atividade educativa.',
      'Sem coleta de nome, telefone ou conta real de aluno.',
      'Responsável adulto presente quando houver menores.',
    ],
    risks:[
      'Não transformar vítimas em exemplo público.',
      'Evitar que links suspeitos reais sejam abertos durante a oficina.',
    ],
  },
  {
    id:'city-cras',
    title:'city/CRAS digital safety pilot',
    audience:'CRAS, centros de idosos, prefeituras e equipes sociais',
    objective:'Testar playbooks comunitários para orientar populações vulneráveis sem coletar dados sensíveis.',
    duration:'2 semanas',
    flow:[
      'Treinar equipe social com 5 casos simulados.',
      'Usar a Rede de Ajuda para escolher playbooks por contexto.',
      'Criar comunicados preventivos sem expor casos reais.',
      'Revisar métricas agregadas ao fim do piloto.',
    ],
    metrics:[
      'Número de orientações realizadas.',
      'Categorias de risco mais frequentes.',
      'Alertas educativos gerados.',
      'Tempo médio de resposta da equipe.',
    ],
    requirements:[
      'Consentimento e aviso de que não há atendimento emergencial automático.',
      'Uso de registros agregados, sem mensagem bruta.',
      'Encaminhamento de perdas reais para canais oficiais.',
    ],
    risks:[
      'Equipe pode receber casos graves que exigem protocolo humano.',
      'O MVP não substitui polícia, banco, saúde mental ou assistência jurídica.',
    ],
  },
  {
    id:'condo-community',
    title:'condo/community pilot',
    audience:'Condomínios, associações de moradores e administradoras',
    objective:'Organizar resposta rápida a golpes de entrega, falso prestador e campanhas recorrentes em grupos locais.',
    duration:'10 dias',
    flow:[
      'Selecionar síndico, portaria ou líder comunitário como facilitador.',
      'Simular alertas de entrega falsa e taxa indevida.',
      'Gerar mensagens educativas para canais oficiais.',
      'Medir clareza da orientação e redução de encaminhamentos confusos.',
    ],
    metrics:[
      'Comunicados preventivos gerados.',
      'Cenários analisados por tipo de risco.',
      'Trust Locks acionados em simulações de pagamento.',
      'Feedback anônimo dos moradores.',
    ],
    requirements:[
      'Canal oficial já existente para comunicados.',
      'Sem coleta de telefones individuais.',
      'Sem exposição de moradores vítimas ou suspeitas.',
    ],
    risks:[
      'Grupos podem espalhar prints com dados pessoais.',
      'Necessário moderar comunicação para não gerar pânico.',
    ],
  },
  {
    id:'small-business-training',
    title:'small business anti-fraud training pilot',
    audience:'Pequenas empresas, ONGs, cooperativas e equipes financeiras',
    objective:'Testar treinamento contra boleto falso, fornecedor falso, pedido de senha e falso suporte.',
    duration:'1 semana',
    flow:[
      'Mapear os 3 fluxos financeiros mais sensíveis da instituição.',
      'Rodar simulações de boleto, link e suporte remoto.',
      'Criar protocolo simples de dupla checagem.',
      'Avaliar se a equipe sabe pausar e escalar antes de pagar.',
    ],
    metrics:[
      'Tentativas simuladas classificadas corretamente.',
      'Tempo para acionar gestor ou financeiro.',
      'Planos de recuperação criados para cenários pós-dano.',
      'Ações de Trust Lock compreendidas pela equipe.',
    ],
    requirements:[
      'Apoio de gestor responsável pelo piloto.',
      'Uso de documentos fictícios ou anonimizados.',
      'Sem integração real com sistemas financeiros.',
    ],
    risks:[
      'Não usar boletos reais em demonstração.',
      'O MVP não executa bloqueio bancário nem investigação formal.',
    ],
  },
]

export const privacySafeMetrics:PrivacySafeMetric[] = [
  {
    label:'Análises',
    value:'48',
    description:'Quantidade agregada de casos simulados, sem armazenar mensagens brutas.',
  },
  {
    label:'Tipos de risco',
    value:'8',
    description:'Categorias como Pix, link, senha, código, documento e app remoto.',
  },
  {
    label:'Trust Locks',
    value:'19',
    description:'Intervenções preventivas em cenários de alto risco.',
  },
  {
    label:'Recovery Plans',
    value:'11',
    description:'Planos educativos gerados para casos simulados de pós-dano.',
  },
  {
    label:'Tempo de resposta',
    value:'< 30s',
    description:'Tempo demonstrativo até uma orientação clara aparecer na tela.',
  },
  {
    label:'Mensagens brutas',
    value:'0',
    description:'Meta do piloto: medir agregados, não guardar conteúdo privado.',
  },
]

export const accessibilityChecklist:AccessibilityChecklistItem[] = [
  {
    label:'Texto grande',
    detail:'Controle no topo aumenta a escala visual para pessoas idosas ou com baixa visão.',
  },
  {
    label:'Alto contraste',
    detail:'Modo opcional reforça contraste de bordas, textos e fundos neutros.',
  },
  {
    label:'Botões maiores',
    detail:'Ações principais usam área de toque mais confortável e foco visível.',
  },
  {
    label:'Linguagem simples',
    detail:'As telas explicam o que fazer agora, sem depender de termos técnicos.',
  },
  {
    label:'Navegação por teclado',
    detail:'Skip link e estados de foco ajudam quem navega sem mouse.',
  },
  {
    label:'Dados simulados',
    detail:'O MVP deixa claro quando está em modo demonstração e não coleta dados reais.',
  },
]
