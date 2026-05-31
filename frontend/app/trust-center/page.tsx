import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import PrivacyConsentChecklist from '@/components/PrivacyConsentChecklist'
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
import {
  guardianDoesList,
  guardianDoesNotList,
  mvpLimitationsList,
  privacyDesignFlow,
} from '@/lib/privacyConsent'

const channelPolicies = [
  ['Canal simples / chatbot', 'Trecho encaminhado voluntariamente', 'Mock no MVP'],
  ['Texto manual (intake)', 'Colagem consciente com consentimento', 'Disponível'],
  ['WhatsApp real', 'Somente com opt-in explícito futuro', 'Não conectado'],
  ['Verificação de URL', 'Link enviado manualmente', 'Mock/local'],
  ['Print / OCR', 'Conteúdo voluntário com redaction', 'Simulado'],
  ['Notificações', 'Alertas ao responsável', 'Simuladas no MVP'],
]

export default function TrustCenterPage(){
  return (
    <PageShell>
      <PageHeader
        eyebrow="Privacidade e consentimento"
        title="Trust Center"
        description="Como o CyberAlerta Guardian protege por consentimento, minimização de dados e humano no loop — sem monitoramento automático de conversas."
        detail="Proteção assistida para famílias, cuidadores e instituições. Prevenção pré-dano, não vigilância. MVP com dados simulados e canais mock."
        actions={
          <>
            <Link href="/chatbot-demo">
              <Button className="h-12 w-full !border-cyan-300/40 !bg-cyan-300/10 !text-cyan-100 hover:!bg-cyan-300/15 sm:w-auto">
                Canal simples (mock)
              </Button>
            </Link>
            <Link href="/assisted-demo">
              <Button variant="ghost" className="h-12 w-full sm:w-auto">Demo guiada</Button>
            </Link>
          </>
        }
        aside={
          <div className="space-y-5">
            <StatusRail
              items={[
                {label:'Monitoramento', value:'não automático', tone:'ready'},
                {label:'Entrada', value:'voluntária', tone:'ready'},
                {label:'MVP', value:'dados simulados', tone:'warn'},
              ]}
            />
            <p className="text-sm leading-6 text-slate-300">
              O Guardian não lê WhatsApp em silêncio. A análise começa quando alguém escolhe encaminhar um conteúdo suspeito.
            </p>
          </div>
        }
      />

      <EvidencePanel
        eyebrow="Princípios"
        title="Checklist de privacidade"
        description="Cinco pilares que orientam o fluxo assistido em todas as telas do produto."
      >
        <PrivacyConsentChecklist />
      </EvidencePanel>

      <div className="grid items-start gap-6 xl:grid-cols-2">
        <DecisionPanel
          eyebrow="Seção A"
          title="O que o Guardian faz"
          description="Capacidades defensivas quando há conteúdo compartilhado com consentimento."
        >
          <ul className="grid gap-3">
            {guardianDoesList.map(item=> (
              <li key={item} className="guardian-never-row">
                <span className="guardian-status-dot guardian-status-ready" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </DecisionPanel>

        <EvidencePanel
          eyebrow="Seção B"
          title="O que o Guardian não faz"
          description="Limites explícitos para evitar narrativa de espionagem ou coleta invasiva."
        >
          <ul className="grid gap-3">
            {guardianDoesNotList.map(item=> (
              <li key={item} className="guardian-never-row">
                <span className="guardian-status-dot guardian-status-risk" />
                <span>{item}</span>
              </li>
            ))}
          </ul>
        </EvidencePanel>
      </div>

      <CommandPanel>
        <SectionHeader
          eyebrow="Seção C"
          title="Como protegemos por design"
          description="Fluxo assistido: voluntário → minimização → análise → responsável → ação humana → relatório controlado."
        />
        <OperationalTimeline items={privacyDesignFlow} />
      </CommandPanel>

      <div className="grid items-start gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <ActionPanel
          eyebrow="Seção D"
          title="MVP e limitações"
          description="Transparência para hackathon, pilotos e avaliação institucional."
        >
          <ul className="grid gap-3">
            {mvpLimitationsList.map(item=> (
              <li key={item} className="guardian-console-mini-card text-sm leading-6 text-slate-300">
                {item}
              </li>
            ))}
          </ul>
          <div className="mt-5 rounded-md border border-amber-400/25 bg-amber-950/20 p-4">
            <div className="text-sm font-semibold text-amber-100">Não é compliance legal completo</div>
            <p className="mt-2 text-sm leading-6 text-slate-400">
              Este MVP demonstra princípios de privacidade e consentimento. Produção exigiria política formal, DPO,
              contratos e revisão jurídica — fora do escopo desta demonstração.
            </p>
          </div>
        </ActionPanel>

        <CommandPanel
          eyebrow="Privacidade por canal"
          title="Matriz de consentimento e integrações futuras"
          description="Cada canal tem escopo, permissão e status. Integrações reais exigiriam opt-in, termos e configuração."
        >
          <div className="guardian-channel-matrix">
            {channelPolicies.map(([name, scope, status])=> (
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

      <div className="grid items-start gap-6 lg:grid-cols-2">
        <EvidencePanel
          eyebrow="Redaction e dados sensíveis"
          title="Minimização na prática"
          description="Quando aplicável, mascaramos CPF, telefone, e-mail e chaves antes da análise."
        >
          <div className="grid gap-3 text-sm leading-6 text-slate-400">
            <p>Não pedimos senha, Pix, código SMS, CPF ou documento para operar a demo.</p>
            <p>
              Se conteúdo sensível for colado por engano, o fluxo orienta a não compartilhar e a usar canal oficial do
              banco ou autoridade competente.
            </p>
            <p>O responsável vê casos para <strong className="text-slate-200">proteger</strong>, não para vigiar a pessoa protegida.</p>
          </div>
        </EvidencePanel>

        <ActionPanel
          eyebrow="Humano no loop"
          title="Prevenção pré-dano"
          description="O sistema recomenda pausa e verificação; decisões críticas ficam com pessoas de confiança."
        >
          <div className="rounded-md border border-cyan-400/25 bg-cyan-950/20 p-4">
            <p className="text-sm leading-6 text-slate-300">
              Trust Lock pausa ações perigosas. Proof of Trust usa canal independente. Trusted Circle no MVP é simulado.
              Relatório e Recovery orientam — não denunciam nem bloqueiam contas automaticamente.
            </p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            <Link href="/intake">
              <Button variant="ghost" className="h-10">Intake técnico</Button>
            </Link>
            <Link href="/family-console">
              <Button variant="ghost" className="h-10">Guardian Console</Button>
            </Link>
          </div>
          <p className="app-muted-text mt-4 text-xs">
            Documentação: docs/assisted-protection-privacy.md
          </p>
        </ActionPanel>
      </div>
    </PageShell>
  )
}
