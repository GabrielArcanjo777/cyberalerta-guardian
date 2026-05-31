import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import {
  ActionPanel,
  CommandPanel,
  DecisionPanel,
  EvidencePanel,
  OperationalTimeline,
  PageHeader,
  PageShell,
  SectionHeader,
  StatusRail,
} from '@/components/CommandCenter'

const commitments = [
  {
    title: 'Sem monitoramento automático',
    body: 'O Guardian não lê conversas privadas nem observa aplicativos em segundo plano.',
    status: 'core',
  },
  {
    title: 'Compartilhamento voluntário',
    body: 'A análise começa apenas quando a pessoa decide enviar uma mensagem, link ou print.',
    status: 'consent',
  },
  {
    title: 'Dados minimizados',
    body: 'O MVP usa o mínimo necessário para demonstrar risco, redaction e ação segura.',
    status: 'privacy',
  },
  {
    title: 'Sem substituição de canais oficiais',
    body: 'Bancos, autoridades, advogados e suporte oficial continuam sendo a referência em casos reais.',
    status: 'limit',
  },
  {
    title: 'Demonstração com dados simulados',
    body: 'Fluxos de alerta, métricas e conectores usam dados de demo quando não há backend real disponível.',
    status: 'demo',
  },
]

const designFlow = [
  {title:'Entrada voluntária', body:'A pessoa escolhe o trecho ou link que deseja revisar.'},
  {title:'Redaction e minimização', body:'Dados pessoais podem ser mascarados antes da análise.'},
  {title:'Análise defensiva', body:'Sinais de risco, manipulação e ação perigosa são avaliados.'},
  {title:'Evidência rastreável', body:'O resultado mostra por que a pausa protetiva foi recomendada.'},
  {title:'Ação segura', body:'O fluxo orienta confirmação por canal confiável e contato salvo.'},
  {title:'Sem bruto por padrão', body:'O MVP não cria banco de dados nem armazenamento persistente de mensagens.'},
]

const neverDo = [
  'Não monitoramos conversas privadas.',
  'Não pedimos senhas, códigos de autenticação ou acesso remoto.',
  'Não substituímos banco, polícia, advogado ou suporte oficial.',
  'Não coletamos dados reais para a demo.',
  'Não vendemos dados.',
]

const policyBlocks = [
  {
    eyebrow: 'O que analisamos',
    title: 'Conteúdo compartilhado para revisão',
    body: 'Mensagens, links, prints ou textos enviados voluntariamente para identificar risco, manipulação, pedido financeiro e próxima ação segura.',
  },
  {
    eyebrow: 'O que não analisamos',
    title: 'Vida privada fora do escopo',
    body: 'Conversas completas, contas pessoais, histórico bancário, contatos do telefone e aplicativos reais sem consentimento ficam fora do MVP.',
  },
  {
    eyebrow: 'IA responsável',
    title: 'IA defensiva, limitada e auditável',
    body: 'A IA pode enriquecer explicações, mas a segurança do produto permanece baseada em evidências, heurísticas e Trust Lock.',
  },
]

const channelPolicies = [
  ['Texto manual', 'Trecho colado pelo usuário', 'Disponível no MVP'],
  ['Verificação de URL', 'Link enviado manualmente', 'Mock/local'],
  ['Print/OCR', 'Conteúdo voluntário com redação futura', 'Simulado'],
  ['WhatsApp opt-in', 'Somente visão futura com opt-in claro', 'Não real'],
  ['E-mail opt-in', 'Escopos granulares e reversíveis', 'Futuro'],
  ['Extensão do navegador', 'Texto ou página selecionada manualmente', 'Futuro'],
]

function CommitmentList(){
  return (
    <div className="guardian-policy-ledger">
      {commitments.map((item,index)=> (
        <div key={item.title} className="guardian-commitment-row">
          <span className="guardian-timeline-index">{String(index + 1).padStart(2,'0')}</span>
          <div>
            <div className="flex flex-col gap-2 sm:flex-row sm:items-center sm:justify-between">
              <h3 className="text-base font-semibold text-white">{item.title}</h3>
              <span className="guardian-technical-badge">{item.status}</span>
            </div>
            <p className="mt-2 text-sm leading-6 text-slate-400">{item.body}</p>
          </div>
        </div>
      ))}
    </div>
  )
}

export default function TrustCenterPage(){
  return (
    <PageShell>
      <PageHeader
        eyebrow="Security and privacy"
        title="Trust Center"
        description="Privacidade, segurança, consentimento e uso responsável no CyberAlerta Guardian."
        detail="Uma página institucional para famílias, escolas, ONGs, prefeituras, empresas e avaliadores entenderem o que o MVP faz, o que não faz e quais limites são preservados."
        actions={
          <>
            <Link href="/intake">
              <Button className="h-12 w-full !border-cyan-300/40 !bg-cyan-300/10 !text-cyan-100 hover:!bg-cyan-300/15 sm:w-auto">Enviar mensagem suspeita</Button>
            </Link>
            <Link href="/before-pix">
              <Button variant="ghost" className="h-12 w-full sm:w-auto">Voltar para análise</Button>
            </Link>
          </>
        }
        aside={
          <div className="space-y-5">
            <div className="text-xs font-bold uppercase tracking-[0.08em] text-cyan-300">Compromissos principais</div>
            <StatusRail
              items={[
                {label:'Consentimento', value:'obrigatório', tone:'ready'},
                {label:'Dados', value:'minimizados', tone:'neutral'},
                {label:'Canais oficiais', value:'preservados', tone:'warn'},
              ]}
            />
            <p className="text-sm leading-6 text-slate-300">
              O produto cria uma pausa antes do dano, mas não promete recuperação, não substitui instituições oficiais e não exige dados reais para demo.
            </p>
          </div>
        }
      />

      <div className="grid items-start gap-6 xl:grid-cols-[1.08fr_0.92fr]">
        <EvidencePanel
          eyebrow="Compromissos do MVP"
          title="Contrato visual de confiança"
          description="A lista abaixo resume o comportamento esperado do produto em uma demo segura e em pilotos pequenos."
        >
          <CommitmentList />
        </EvidencePanel>

        <ActionPanel
          eyebrow="Em caso real"
          title="Pare, preserve evidências e procure canais oficiais."
          description="O Guardian organiza sinais e próximos passos, mas não substitui banco, polícia, advogado, suporte oficial ou autoridades competentes."
        >
          <div className="rounded-md border border-red-400/35 bg-red-500/12 p-4">
            <div className="text-sm font-semibold text-red-100">Não envie dados reais para teste.</div>
            <p className="mt-2 text-sm leading-6 text-slate-300">
              Use mensagens simuladas ou anonimizadas. Senhas, códigos, documentos e chaves reais devem ficar fora da demo.
            </p>
          </div>
        </ActionPanel>
      </div>

      <CommandPanel>
        <SectionHeader
          eyebrow="Como o Guardian protege por design"
          title="Fluxo defensivo de ponta a ponta"
          description="A experiência prioriza pausa, explicabilidade e ação segura sem vigilância permanente."
        />
        <OperationalTimeline items={designFlow} />
      </CommandPanel>

      <div className="grid items-start gap-6 lg:grid-cols-[1.15fr_0.85fr]">
        <DecisionPanel
          eyebrow="Policy panels"
          title="Escopo claro para clientes e instituições"
          description="Os painéis abaixo substituem documentos soltos por política operacional objetiva."
        >
          <div className="grid gap-4">
            {policyBlocks.map((block,index)=> (
              <div key={block.title} className={`guardian-policy-card ${index === 0 ? 'guardian-policy-primary' : ''}`}>
                <div className="guardian-panel-eyebrow">{block.eyebrow}</div>
                <h3 className="mt-2 text-lg font-semibold text-white">{block.title}</h3>
                <p className="mt-2 text-sm leading-6 text-slate-400">{block.body}</p>
              </div>
            ))}
          </div>
        </DecisionPanel>

        <EvidencePanel
          eyebrow="O que nunca fazemos"
          title="Limites de segurança"
          description="Limites simples para evitar confusão no momento de risco."
        >
          <ul className="grid gap-3">
            {neverDo.map((item)=> (
              <li key={item} className="guardian-never-row">
                <span className="guardian-status-dot guardian-status-risk" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </EvidencePanel>
      </div>

      <div className="grid items-start gap-6 lg:grid-cols-[0.9fr_1.1fr]">
        <ActionPanel
          eyebrow="Dados simulados"
          title="Transparência do MVP"
          description="Alertas, métricas, conectores e alguns resultados podem usar simulação para demonstrar a tese sem expor dados reais."
        >
          <div className="grid gap-3">
            {[
              ['Sem persistência real', 'Não cria banco de dados para mensagens brutas no MVP.'],
              ['Audit log seguro', 'Demonstra metadados técnicos como canal, risco e modo de IA.'],
              ['Opt-in futuro', 'Integrações reais exigiriam permissão granular e reversível.'],
            ].map(([title,body])=> (
              <div key={title} className="guardian-console-mini-card">
                <div className="text-sm font-semibold text-white">{title}</div>
                <p className="mt-1 text-sm leading-6 text-slate-400">{body}</p>
              </div>
            ))}
          </div>
        </ActionPanel>

        <CommandPanel
          eyebrow="Privacidade por canal"
          title="Matriz de consentimento"
          description="Cada canal tem escopo, permissão e limite explícitos."
        >
          <div className="guardian-channel-matrix">
            {channelPolicies.map(([name,scope,status])=> (
              <div key={name} className="guardian-channel-row">
                <div>
                  <div className="text-sm font-semibold text-white">{name}</div>
                  <p className="mt-1 text-sm leading-5 text-slate-400">{scope}</p>
                </div>
                <span className="guardian-technical-badge">{status}</span>
              </div>
            ))}
          </div>
        </CommandPanel>
      </div>
    </PageShell>
  )
}
