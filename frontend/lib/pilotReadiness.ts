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
    audience:'Familias com idosos, cuidadores e contatos de confianca',
    objective:'Testar se a pausa protetiva reduz decisoes por impulso antes de Pix, links e pedidos de codigo.',
    duration:'7 dias',
    flow:[
      'Orientar a familia em uma chamada curta de 20 minutos.',
      'Simular 3 cenarios comuns com mensagens de demonstracao.',
      'Usar Before Pix, Family Console, Help Network e Recovery Mode em casos simulados.',
      'Coletar feedback anonimo sobre clareza, medo reduzido e facilidade de uso.',
    ],
    metrics:[
      'Numero de analises simuladas.',
      'Trust Locks ativados em cenarios de alto risco.',
      'Planos de recuperacao criados sem conteudo privado.',
      'Tempo medio ate a familia entender a acao recomendada.',
    ],
    requirements:[
      'Consentimento verbal ou escrito dos participantes.',
      'Nenhum telefone real inserido no sistema.',
      'Uso apenas de mensagens ficticias ou anonimizadas.',
    ],
    risks:[
      'Participantes podem confundir MVP com envio real de alerta.',
      'O piloto precisa reforcar que a ferramenta orienta, mas nao substitui canais oficiais.',
    ],
  },
  {
    id:'school-workshop',
    title:'school workshop pilot',
    audience:'Escolas, coordenadores, professores, alunos e responsaveis',
    objective:'Validar o Guardian como material de educacao digital para phishing, falso suporte e pedido de codigo.',
    duration:'1 oficina de 60 a 90 minutos',
    flow:[
      'Apresentar golpes comuns em linguagem simples.',
      'Rodar cenarios de phishing e pedido de codigo no modo demo.',
      'Mostrar como preservar evidencias sem expor o aluno.',
      'Encerrar com checklist de seguranca para alunos e familiares.',
    ],
    metrics:[
      'Cenarios analisados durante a oficina.',
      'Tipos de risco identificados pela turma.',
      'Perguntas frequentes registradas sem nomes.',
      'Nivel de compreensao antes/depois por formulario anonimo.',
    ],
    requirements:[
      'Autorizacao da escola para atividade educativa.',
      'Sem coleta de nome, telefone ou conta real de aluno.',
      'Responsavel adulto presente quando houver menores.',
    ],
    risks:[
      'Nao transformar vitimas em exemplo publico.',
      'Evitar que links suspeitos reais sejam abertos durante a oficina.',
    ],
  },
  {
    id:'city-cras',
    title:'city/CRAS digital safety pilot',
    audience:'CRAS, centros de idosos, prefeituras e equipes sociais',
    objective:'Testar playbooks comunitarios para orientar populacoes vulneraveis sem coletar dados sensiveis.',
    duration:'2 semanas',
    flow:[
      'Treinar equipe social com 5 casos simulados.',
      'Usar a Rede de Ajuda para escolher playbooks por contexto.',
      'Criar comunicados preventivos sem expor casos reais.',
      'Revisar metricas agregadas ao fim do piloto.',
    ],
    metrics:[
      'Numero de orientacoes realizadas.',
      'Categorias de risco mais frequentes.',
      'Alertas educativos gerados.',
      'Tempo medio de resposta da equipe.',
    ],
    requirements:[
      'Consentimento e aviso de que nao ha atendimento emergencial automatico.',
      'Uso de registros agregados, sem mensagem bruta.',
      'Encaminhamento de perdas reais para canais oficiais.',
    ],
    risks:[
      'Equipe pode receber casos graves que exigem protocolo humano.',
      'O MVP nao substitui policia, banco, saude mental ou assistencia juridica.',
    ],
  },
  {
    id:'condo-community',
    title:'condo/community pilot',
    audience:'Condominios, associacoes de moradores e administradoras',
    objective:'Organizar resposta rapida a golpes de entrega, falso prestador e campanhas recorrentes em grupos locais.',
    duration:'10 dias',
    flow:[
      'Selecionar sindico, portaria ou lider comunitario como facilitador.',
      'Simular alertas de entrega falsa e taxa indevida.',
      'Gerar mensagens educativas para canais oficiais.',
      'Medir clareza da orientacao e reducao de encaminhamentos confusos.',
    ],
    metrics:[
      'Comunicados preventivos gerados.',
      'Cenarios analisados por tipo de risco.',
      'Trust Locks acionados em simulacoes de pagamento.',
      'Feedback anonimo dos moradores.',
    ],
    requirements:[
      'Canal oficial ja existente para comunicados.',
      'Sem coleta de telefones individuais.',
      'Sem exposicao de moradores vitimas ou suspeitas.',
    ],
    risks:[
      'Grupos podem espalhar prints com dados pessoais.',
      'Necessario moderar comunicacao para nao gerar panico.',
    ],
  },
  {
    id:'small-business-training',
    title:'small business anti-fraud training pilot',
    audience:'Pequenas empresas, ONGs, cooperativas e equipes financeiras',
    objective:'Testar treinamento contra boleto falso, fornecedor falso, pedido de senha e falso suporte.',
    duration:'1 semana',
    flow:[
      'Mapear os 3 fluxos financeiros mais sensiveis da instituicao.',
      'Rodar simulacoes de boleto, link e suporte remoto.',
      'Criar protocolo simples de dupla checagem.',
      'Avaliar se a equipe sabe pausar e escalar antes de pagar.',
    ],
    metrics:[
      'Tentativas simuladas classificadas corretamente.',
      'Tempo para acionar gestor ou financeiro.',
      'Planos de recuperacao criados para cenarios pos-dano.',
      'Acoes de Trust Lock compreendidas pela equipe.',
    ],
    requirements:[
      'Apoio de gestor responsavel pelo piloto.',
      'Uso de documentos ficticios ou anonimizados.',
      'Sem integracao real com sistemas financeiros.',
    ],
    risks:[
      'Nao usar boletos reais em demonstracao.',
      'O MVP nao executa bloqueio bancario nem investigacao formal.',
    ],
  },
]

export const privacySafeMetrics:PrivacySafeMetric[] = [
  {
    label:'Analises',
    value:'48',
    description:'Quantidade agregada de casos simulados, sem armazenar mensagens brutas.',
  },
  {
    label:'Tipos de risco',
    value:'8',
    description:'Categorias como Pix, link, senha, codigo, documento e app remoto.',
  },
  {
    label:'Trust Locks',
    value:'19',
    description:'Intervencoes preventivas em cenarios de alto risco.',
  },
  {
    label:'Recovery Plans',
    value:'11',
    description:'Planos educativos gerados para casos simulados de pos-dano.',
  },
  {
    label:'Tempo de resposta',
    value:'< 30s',
    description:'Tempo demonstrativo ate uma orientacao clara aparecer na tela.',
  },
  {
    label:'Mensagens brutas',
    value:'0',
    description:'Meta do piloto: medir agregados, nao guardar conteudo privado.',
  },
]

export const accessibilityChecklist:AccessibilityChecklistItem[] = [
  {
    label:'Texto grande',
    detail:'Controle no topo aumenta a escala visual para pessoas idosas ou com baixa visao.',
  },
  {
    label:'Alto contraste',
    detail:'Modo opcional reforca contraste de bordas, textos e fundos neutros.',
  },
  {
    label:'Botoes maiores',
    detail:'Acoes principais usam area de toque mais confortavel e foco visivel.',
  },
  {
    label:'Linguagem simples',
    detail:'As telas explicam o que fazer agora, sem depender de termos tecnicos.',
  },
  {
    label:'Navegacao por teclado',
    detail:'Skip link e estados de foco ajudam quem navega sem mouse.',
  },
  {
    label:'Dados simulados',
    detail:'O MVP deixa claro quando esta em modo demonstracao e nao coleta dados reais.',
  },
]
