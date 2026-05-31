import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import AttackGlobe3D from '@/components/AttackGlobe3D'
import {AppBadge, AppCardTitle, AppSectionTitle} from '@/components/AppPrimitives'
import {
  channelLabel,
  globalApplicabilityRegions,
  globalScenarios,
  globalThreatPatternGroups,
  riskLevelLabel,
  type GlobalScenario,
} from '@/lib/globalScenarios'
import {riskStatusClass} from '@/lib/appStatus'
import {MetricPanel, PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

const featuredId = 'br-fake-child-pix'
const primaryIds = ['us-gift-card', 'us-fake-tech-support', 'eu-fake-delivery']
const otherIds = ['in-otp-code', 'af-mobile-money', 'br-fake-bank-link', 'global-code-request']

function findScenario(id:string){
  return globalScenarios.find((scenario)=>scenario.id === id)
}

function FeaturedScenarioCard({scenario}:{scenario:GlobalScenario}){
  return (
    <article className="app-card-highlight">
      <div className="flex flex-wrap items-center gap-2">
        <AppBadge className="app-badge-accent">Cenário principal · Brasil</AppBadge>
        <span className={riskStatusClass(scenario.expected_risk_level)}>
          Risco {riskLevelLabel(scenario.expected_risk_level)}
        </span>
      </div>
      <AppCardTitle className="mt-4 text-xl sm:text-2xl">{scenario.title}</AppCardTitle>
      <dl className="mt-4 grid gap-3 text-sm sm:grid-cols-2">
        <div>
          <dt className="app-label">Canal</dt>
          <dd className="mt-1 font-medium text-slate-200">{channelLabel(scenario.channel)}</dd>
        </div>
        <div>
          <dt className="app-label">Região</dt>
          <dd className="mt-1 font-medium text-slate-200">{scenario.region}</dd>
        </div>
      </dl>
      <p className="app-body-text mt-4">{scenario.global_relevance}</p>
      <div className="app-callout mt-4">
        <div className="app-callout-label">Ação recomendada</div>
        <p className="app-callout-body">{scenario.recommended_action}</p>
      </div>
    </article>
  )
}

function ScenarioCard({scenario}:{scenario:GlobalScenario}){
  return (
    <article className="app-card-row">
      <div className="min-w-0 flex-1">
        <AppCardTitle>{scenario.title}</AppCardTitle>
        <p className="app-muted-text mt-1">
          {scenario.region} · {channelLabel(scenario.channel)}
        </p>
        <p className="app-body-text mt-2 line-clamp-2">{scenario.global_relevance}</p>
      </div>
      <div className="flex shrink-0 flex-col items-start gap-2 sm:items-end">
        <span className={riskStatusClass(scenario.expected_risk_level)}>
          {riskLevelLabel(scenario.expected_risk_level)}
        </span>
        <p className="max-w-[14rem] text-right text-xs font-medium leading-5 text-emerald-300/90">
          {scenario.recommended_action}
        </p>
      </div>
    </article>
  )
}

function CompactScenario({scenario}:{scenario:GlobalScenario}){
  return (
    <div className="app-card-compact flex items-center justify-between gap-3 border-l-2 border-l-cyan-500/40">
      <div className="min-w-0">
        <div className="app-card-title text-sm">{scenario.title}</div>
        <div className="app-muted-text mt-0.5 text-xs">
          {scenario.region} · {channelLabel(scenario.channel)}
        </div>
      </div>
      <span className={`${riskStatusClass(scenario.expected_risk_level)} shrink-0`}>
        {riskLevelLabel(scenario.expected_risk_level)}
      </span>
    </div>
  )
}

export default function GlobalApplicabilityPage(){
  const featured = findScenario(featuredId)!
  const primaryScenarios = primaryIds.map((id)=>findScenario(id)).filter(Boolean) as GlobalScenario[]
  const otherScenarios = otherIds.map((id)=>findScenario(id)).filter(Boolean) as GlobalScenario[]

  return (
    <PageShell>
      <PageHeader
        eyebrow="Radar de proteção assistida"
        title="Visibilidade de ameaças para proteção pré-dano."
        description="Visão simulada de padrões de golpe: a pessoa protegida encaminha o risco, o Guardian analisa, o responsável acompanha e o Trust Lock pausa a ação antes do Pix, do clique ou do compartilhamento de credencial."
        detail="Foco em WhatsApp, Pix, engenharia social e pessoas vulneráveis — com canal simples para quem precisa de ajuda e console para família ou instituição."
        actions={
          <>
            <Link href="/before-pix"><Button className="h-12 w-full sm:w-auto">Analisar mensagem suspeita</Button></Link>
            <Link href="/simulator"><Button variant="ghost" className="h-12 w-full sm:w-auto">Ver cenários simulados</Button></Link>
          </>
        }
        aside={
          <div className="space-y-5">
            <div className="app-label text-cyan-300/90">Fluxo assistido</div>
            <StatusRail
              items={[
                {label:'Encaminhamento', value:'canal simples', tone:'neutral'},
                {label:'Análise', value:'Guardian', tone:'warn'},
                {label:'Acompanhamento', value:'responsável', tone:'ready'},
                {label:'Proteção', value:'Trust Lock', tone:'risk'},
              ]}
            />
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <MetricPanel label="Padrões simulados" value={globalScenarios.length} detail="catálogo" tone="cyan" />
        <MetricPanel label="Regiões no radar" value={globalApplicabilityRegions.length} detail="mercados" />
        <MetricPanel label="Pressões mapeadas" value="18" detail="simulação" tone="risk" />
        <MetricPanel label="Ações pausadas (demo)" value="7" detail="Trust Lock" tone="safe" />
      </div>

      <AttackGlobe3D />

      <p className="app-muted-text text-center">
        Visualização simulada — não é um feed real de ataques.
      </p>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {globalApplicabilityRegions.map((region)=> (
          <Card key={region.region}>
            <div className="app-label">{region.region}</div>
            <AppSectionTitle className="mt-2 text-lg">{region.focus}</AppSectionTitle>
            <p className="app-body-text mt-3">{region.description}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
        <Card>
          <div className="app-label">Cenários globais</div>
          <AppSectionTitle>Exemplos defensivos e simulados</AppSectionTitle>
          <p className="app-muted-text mt-2">
            Destaque para o padrão brasileiro mais comum em pilotos: familiar falso pedindo Pix pelo WhatsApp.
          </p>

          <div className="mt-5">
            <FeaturedScenarioCard scenario={featured} />
          </div>

          <div className="mt-5 space-y-3">
            {primaryScenarios.map((scenario)=> (
              <ScenarioCard key={scenario.id} scenario={scenario} />
            ))}
          </div>

          <div className="mt-6 border-t border-white/10 pt-5">
            <div className="app-label">Outros padrões</div>
            <div className="mt-3 grid gap-2">
              {otherScenarios.map((scenario)=> (
                <CompactScenario key={scenario.id} scenario={scenario} />
              ))}
            </div>
          </div>
        </Card>

        <Card className="flex flex-col">
          <div className="app-label">Padrões globais de ameaça</div>
          <AppSectionTitle>Táticas que cruzam fronteiras</AppSectionTitle>
          <p className="app-body-text mt-3">
            Mesmo com canais e moedas diferentes, golpistas repetem combinações de pressão emocional, identidade falsa e pedido de ação sensível.
          </p>

          <div className="mt-5 flex flex-1 flex-col gap-3">
            {globalThreatPatternGroups.map((group)=> (
              <div key={group.title} className="app-tag-group">
                <div className="app-label">{group.title}</div>
                <div className="mt-3 flex flex-wrap gap-2">
                  {group.items.map((item)=> (
                    <AppBadge key={item}>{item}</AppBadge>
                  ))}
                </div>
              </div>
            ))}
          </div>

          <div className="app-action-panel mt-5">
            <AppCardTitle>MVP vs produto global real</AppCardTitle>
            <p className="app-body-text mt-2">
              O MVP demonstra proteção assistida antes do dano. Um produto global real exige localização, revisão jurídica, privacidade por região e validação contínua por mercado.
            </p>
          </div>
        </Card>
      </div>
    </PageShell>
  )
}
