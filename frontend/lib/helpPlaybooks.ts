export type HelpPlaybook = {
  id:string
  title:string
  audience:string
  signals:string[]
  immediate_action:string
  who_to_notify:string[]
  suggested_message:string
  what_not_to_do:string[]
  next_steps:string[]
}

export type AlertTemplate = {
  id:string
  audience:string
  title:string
  message:string
}

export const helpAudiences = [
  {
    title:'Para famílias',
    description:'Orientação rápida para filhos, netos, cuidadores e contatos de confiança ajudarem sem invadir privacidade.',
  },
  {
    title:'Para escolas',
    description:'Playbooks para coordenadores e professores apoiarem alunos e responsáveis em incidentes digitais.',
  },
  {
    title:'Para ONGs',
    description:'Material de apoio para inclusão digital, idosos, comunidades vulneráveis e mutirões educativos.',
  },
  {
    title:'Para condomínios',
    description:'Resposta organizada para golpes de entrega, falsos prestadores e avisos recorrentes a moradores.',
  },
  {
    title:'Para prefeituras',
    description:'Base para programas sociais, CRAS, centros de idosos e campanhas municipais de prevenção.',
  },
  {
    title:'Para bancos/fintechs',
    description:'Camada educativa de intervenção pré-dano integrada a canais oficiais e suporte humano.',
  },
]

export const helpPlaybooks:HelpPlaybook[] = [
  {
    id:'elderly-pix-request',
    title:'Idoso recebeu pedido de Pix',
    audience:'Família e contato de confiança',
    signals:['pedido de Pix urgente','número novo','pedido para não ligar','vínculo familiar não verificado'],
    immediate_action:'Pausar qualquer pagamento e falar com a pessoa por um canal antigo ou presencial.',
    who_to_notify:['familiar de confiança','cuidador','gerente ou canal oficial do banco, se houve pagamento'],
    suggested_message:'Vó, não faça o Pix agora. Sou eu. Vamos confirmar juntos por ligação no número antigo antes de qualquer pagamento.',
    what_not_to_do:['não enviar dinheiro','não responder ao número novo','não compartilhar comprovantes','não discutir com o suspeito'],
    next_steps:['salvar prints','confirmar identidade por voz','acionar Recovery Mode se o pagamento já aconteceu'],
  },
  {
    id:'student-phishing',
    title:'Aluno caiu em phishing',
    audience:'Escola e responsáveis',
    signals:['link de login','pedido de senha','conta escolar ou jogo','urgência para validar acesso'],
    immediate_action:'Orientar o aluno a parar, trocar senha pelo canal oficial e avisar um adulto responsável.',
    who_to_notify:['coordenação escolar','responsável legal','suporte oficial da plataforma'],
    suggested_message:'Olá, recebemos um alerta de possível link falso. Não use o link. Vamos orientar a troca de senha pelo site oficial e acompanhar com a família.',
    what_not_to_do:['não expor o aluno','não compartilhar prints publicamente','não culpar a vítima','não clicar novamente no link'],
    next_steps:['registrar orientação mínima','reforçar educação digital','avaliar se outras pessoas receberam a mesma mensagem'],
  },
  {
    id:'employee-fake-invoice',
    title:'Funcionário recebeu falso boleto',
    audience:'Empresa, cooperativa ou instituição',
    signals:['boleto inesperado','cobrança urgente','fornecedor não confirmado','link ou anexo suspeito'],
    immediate_action:'Bloquear o pagamento até validação com financeiro e fornecedor por canal conhecido.',
    who_to_notify:['financeiro interno','gestor direto','segurança da informação ou suporte interno'],
    suggested_message:'Recebemos uma cobrança suspeita. Não pague ainda. Confirme com o financeiro e valide o fornecedor por canal oficial.',
    what_not_to_do:['não pagar por pressão','não encaminhar anexo suspeito','não alterar dados bancários sem validação'],
    next_steps:['registrar tentativa','avisar equipe impactada','criar regra de dupla checagem para pagamentos'],
  },
  {
    id:'resident-fake-delivery',
    title:'Morador recebeu falso entregador',
    audience:'Condomínio e portaria',
    signals:['taxa de entrega','link externo','entregador não confirmado','pedido de documento'],
    immediate_action:'Orientar o morador a não pagar taxa nem enviar documento sem confirmar com a transportadora oficial.',
    who_to_notify:['síndico ou administradora','portaria','grupo oficial de avisos do condomínio'],
    suggested_message:'Atenção: há alerta de possível golpe de entrega. Não pague taxas por links recebidos e confirme encomendas pelos canais oficiais.',
    what_not_to_do:['não divulgar telefone de morador','não expor vítima no grupo','não abrir link suspeito'],
    next_steps:['avisar moradores','padronizar canal de comunicados','preservar evidências se houver prejuízo'],
  },
  {
    id:'family-fake-support',
    title:'Família recebeu golpe de falso suporte',
    audience:'Família e cuidador',
    signals:['suporte técnico inesperado','instalar aplicativo','acesso remoto','pedido de senha ou código'],
    immediate_action:'Desconectar a chamada, não instalar app e procurar suporte oficial por conta própria.',
    who_to_notify:['familiar de confiança','suporte oficial do serviço','banco, se dados financeiros foram expostos'],
    suggested_message:'Não instale nenhum aplicativo nem compartilhe tela. Vamos encerrar a conversa e procurar o suporte oficial pelo site ou app conhecido.',
    what_not_to_do:['não compartilhar tela','não informar senha','não instalar app remoto','não seguir instruções do contato suspeito'],
    next_steps:['verificar apps instalados','trocar senhas se necessário','ativar Recovery Mode se houve acesso ou pagamento'],
  },
  {
    id:'community-recurring-campaign',
    title:'Comunidade recebeu campanha de golpe recorrente',
    audience:'ONG, prefeitura, escola ou liderança comunitária',
    signals:['várias pessoas receberam mensagem parecida','mesma marca imitada','mesmo link ou cobrança','pressão emocional coletiva'],
    immediate_action:'Criar alerta educativo curto, reforçar canais oficiais e orientar preservação de evidências.',
    who_to_notify:['equipe social','lideranças comunitárias','comunicação institucional','canais oficiais locais'],
    suggested_message:'Alerta preventivo: circula uma mensagem suspeita na comunidade. Não clique, não pague e confirme informações nos canais oficiais antes de agir.',
    what_not_to_do:['não publicar dados pessoais','não prometer investigação oficial','não compartilhar link suspeito ativo'],
    next_steps:['mapear sinais sem coletar dados sensíveis','publicar orientação preventiva','encaminhar casos reais para canais oficiais'],
  },
]

export const alertTemplates:AlertTemplate[] = [
  {
    id:'family-contact',
    audience:'Familiar',
    title:'Mensagem para familiar',
    message:'Recebi um alerta do Guardian. Não faça pagamento nem clique em links por enquanto. Vamos confirmar juntos por um canal conhecido.',
  },
  {
    id:'school-coordinator',
    audience:'Coordenador escolar',
    title:'Mensagem para coordenação escolar',
    message:'Há suspeita de golpe digital envolvendo aluno ou responsável. A orientação é pausar, preservar evidências e conduzir a verificação por canais oficiais da escola.',
  },
  {
    id:'condo-manager',
    audience:'Condomínio',
    title:'Mensagem para síndico/portaria',
    message:'Possível golpe circulando entre moradores. Favor orientar que ninguém pague taxas ou envie documentos por links recebidos fora dos canais oficiais.',
  },
  {
    id:'city-social-team',
    audience:'Equipe social/prefeitura',
    title:'Mensagem para equipe social',
    message:'Foi identificado padrão de golpe digital em contexto comunitário. Recomendamos alerta educativo, preservação de privacidade e encaminhamento de casos reais aos canais oficiais.',
  },
  {
    id:'internal-support',
    audience:'Suporte interno',
    title:'Mensagem para suporte de empresa',
    message:'Possível tentativa de golpe contra colaborador. Não execute pagamento, não abra anexo e valide a solicitação com financeiro ou segurança por canal interno conhecido.',
  },
]
