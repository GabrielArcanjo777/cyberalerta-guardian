import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'

const trustPrinciples = [
  {
    title: 'O que o Guardian analisa',
    body: 'Mensagens, links, prints ou conteúdos enviados voluntariamente para identificar risco, manipulação, pedidos financeiros e sinais de golpe.',
  },
  {
    title: 'O que o Guardian não analisa',
    body: 'Conversas privadas sem consentimento, contas pessoais, aplicativos reais, histórico bancário, contatos do telefone ou dados que o usuário não decidiu compartilhar.',
  },
  {
    title: 'Como protegemos sua privacidade',
    body: 'Aplicamos minimização de dados, redaction quando possível e audit log apenas com metadados técnicos sem conteúdo bruto da mensagem.',
  },
  {
    title: 'Consentimento e opt-in',
    body: 'O Guardian não monitora suas conversas automaticamente. Você decide o que compartilhar para análise.',
  },
  {
    title: 'Dados simulados no MVP',
    body: 'O MVP pode usar dados simulados para demonstrar funcionalidades, integrações, alertas e métricas de impacto.',
  },
  {
    title: 'Limitações',
    body: 'O CyberAlerta Guardian não substitui banco, polícia, advogado ou canais oficiais. Ele é uma camada preventiva de orientação e pausa.',
  },
]

const requiredStatements = [
  'O Guardian não monitora suas conversas automaticamente.',
  'Você decide o que compartilhar para análise.',
  'O sistema analisa apenas mensagens, links, prints ou conteúdos enviados voluntariamente.',
  'O MVP pode usar dados simulados para demonstrar funcionalidades.',
  'O CyberAlerta Guardian não substitui banco, polícia, advogado ou canais oficiais.',
  'Nunca envie senhas, códigos de autenticação ou documentos reais para teste.',
]

const aiPolicies = [
  'A análise pode ser heurística ou assistida por IA.',
  'SafetyPolicy valida saídas antes de exibir conteúdo sensível.',
  'IA não deve reduzir risco crítico calculado sem justificativa e revisão segura.',
  'O sistema funciona sem chave externa usando heurísticas determinísticas.',
  'IA não substitui confirmação por bancos, autoridades ou canais oficiais.',
]

const channelCards = [
  {
    name: 'Colar mensagem manualmente',
    status: 'MVP',
    consent: 'Consentimento explícito na tela.',
    analyzes: 'Trecho colado pelo usuário.',
    excludes: 'Não acessa conversas completas nem outros apps.',
  },
  {
    name: 'Print enviado voluntariamente',
    status: 'Visão futura',
    consent: 'Upload iniciado pelo usuário.',
    analyzes: 'Imagem ou texto extraído do print.',
    excludes: 'Não abre galeria automaticamente.',
  },
  {
    name: 'URL check',
    status: 'MVP mock',
    consent: 'URL enviada manualmente.',
    analyzes: 'Metadados de risco e sinais defensivos.',
    excludes: 'Não navega em contas privadas.',
  },
  {
    name: 'OCR futuro',
    status: 'Mock',
    consent: 'Opt-in antes do processamento.',
    analyzes: 'Texto detectado em imagem enviada.',
    excludes: 'Não armazena documento real no MVP.',
  },
  {
    name: 'E-mail opt-in',
    status: 'Visão futura',
    consent: 'Permissão granular e reversível.',
    analyzes: 'Mensagem suspeita escolhida pelo usuário.',
    excludes: 'Não monitora caixa de entrada inteira.',
  },
  {
    name: 'WhatsApp Business opt-in futuro',
    status: 'Visão futura',
    consent: 'Somente com opt-in claro.',
    analyzes: 'Conteúdo compartilhado voluntariamente.',
    excludes: 'Não acessa WhatsApp pessoal real.',
  },
  {
    name: 'Browser extension futura',
    status: 'Visão futura',
    consent: 'Ação manual do usuário.',
    analyzes: 'Página ou link selecionado.',
    excludes: 'Não registra navegação contínua.',
  },
]

export default function TrustCenterPage(){
  return (
    <section className="mx-auto max-w-7xl space-y-7 pb-14">
      <div className="guardian-panel-dark overflow-hidden rounded-lg text-white">
        <div className="grid lg:grid-cols-[1.08fr_0.92fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="guardian-kicker">
              Security and privacy
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight text-white sm:text-5xl">Trust Center</h1>
            <p className="mt-4 max-w-3xl text-base font-semibold leading-7 text-slate-300">
              Privacidade, segurança e uso responsável no CyberAlerta Guardian.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Link href="/intake"><Button className="h-12 w-full !border-white !bg-white !text-slate-950 hover:!bg-cyan-50 sm:w-auto">Enviar mensagem suspeita</Button></Link>
              <Link href="/before-pix"><Button variant="ghost" className="h-12 w-full sm:w-auto">Voltar para análise</Button></Link>
            </div>
          </div>
          <div className="border-t border-white/10 bg-white/[0.04] p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">Compromissos do MVP</div>
            <div className="mt-5 space-y-3">
              {requiredStatements.slice(0, 4).map((statement)=> (
                <div key={statement} className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
                  <p className="text-sm font-semibold leading-6 text-slate-200">{statement}</p>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-3">
        {trustPrinciples.map((item)=> (
          <Card key={item.title}>
            <div className="flex h-9 w-9 items-center justify-center rounded-lg bg-slate-950 text-sm font-black text-white">
              {item.title.slice(0, 1)}
            </div>
            <h2 className="mt-4 text-lg font-black tracking-tight text-slate-950">{item.title}</h2>
            <p className="mt-2 text-sm leading-6 text-slate-600">{item.body}</p>
          </Card>
        ))}
      </div>

      <Card className="border-red-200 bg-red-50">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-start lg:justify-between">
          <div>
            <div className="text-xs font-bold uppercase tracking-[0.2em] text-red-600">Em caso real de golpe</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Pare, preserve evidências e procure canais oficiais.</h2>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-700">
              O CyberAlerta Guardian ajuda a organizar sinais de risco e próximos passos, mas não substitui atendimento do banco, polícia, advogado, suporte oficial ou autoridades competentes.
            </p>
          </div>
          <div className="rounded-lg border border-red-200 bg-white px-4 py-3 text-sm font-black text-red-700">
            Não envie dados reais para teste
          </div>
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1fr)_minmax(320px,0.8fr)]">
        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Responsible AI</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Como usamos IA</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            A IA é opcional e limitada a enriquecer explicações defensivas. A base de segurança continua sendo a decisão por heurísticas, evidências e Trust Lock.
          </p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            {aiPolicies.map((policy)=> (
              <div key={policy} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-semibold leading-6 text-slate-700">{policy}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Famílias e instituições</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Segurança prática para decisão rápida</h2>
          <p className="mt-3 text-sm leading-6 text-slate-600">
            O produto cria uma pausa antes do dano e mostra por que um alerta foi gerado. Isso ajuda famílias, escolas, prefeituras e instituições a orientar pessoas vulneráveis sem vigilância permanente.
          </p>
          <div className="mt-5 space-y-3">
            {requiredStatements.slice(4).map((statement)=> (
              <div key={statement} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <p className="text-sm font-bold leading-6 text-slate-800">{statement}</p>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-end sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Privacy by channel</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Privacidade por canal</h2>
          </div>
          <span className="rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
            Consentimento antes da análise
          </span>
        </div>
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {channelCards.map((channel)=> (
            <div key={channel.name} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-start justify-between gap-3">
                <h3 className="text-sm font-black text-slate-950">{channel.name}</h3>
                <span className="rounded border border-slate-200 bg-white px-2 py-1 text-[10px] font-bold uppercase tracking-wide text-slate-600">
                  {channel.status}
                </span>
              </div>
              <div className="mt-4 space-y-3 text-sm leading-5 text-slate-600">
                <p><span className="font-bold text-slate-900">Consentimento:</span> {channel.consent}</p>
                <p><span className="font-bold text-slate-900">Analisa:</span> {channel.analyzes}</p>
                <p><span className="font-bold text-slate-900">Não analisa:</span> {channel.excludes}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Uso global e limitações</div>
        <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Produto global exige adaptação local</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-2">
          {[
            'Golpes variam por país, idioma, meio de pagamento e canal de comunicação.',
            'Regras legais, privacidade, retenção e auditoria variam por região.',
            'O MVP é uma demonstração defensiva e usa dados simulados em algumas áreas.',
            'Usuários devem seguir bancos, autoridades, suporte oficial e canais locais.',
          ].map((item)=> (
            <div key={item} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm font-semibold leading-6 text-slate-700">{item}</p>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Políticas técnicas</div>
        <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Transparência do MVP</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-3">
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-black text-slate-950">Audit log seguro</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">Registra apenas metadados mínimos, como canal, nível de risco, ação e modo de IA.</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-black text-slate-950">Sem persistência real</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">O MVP não cria banco de dados nem coleta persistente de mensagens reais por padrão.</p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-black text-slate-950">Opt-in futuro</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">Integrações futuras devem exigir permissão explícita, granular e reversível.</p>
          </div>
        </div>
      </Card>
    </section>
  )
}
