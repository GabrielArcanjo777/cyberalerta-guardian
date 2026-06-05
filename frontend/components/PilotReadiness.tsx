import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppBadge, AppCardTitle, AppSectionTitle} from '@/components/AppPrimitives'
import {MetricPanel, PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'
import {
  accessibilityChecklist,
  pilotPackages,
  privacySafeMetrics,
} from '@/lib/pilotReadiness'

export default function PilotReadiness(){
  return (
    <PageShell maxWidth="6xl">
      <PageHeader
        eyebrow="Pilot Readiness"
        title="CyberAlerta pronto para piloto pequeno"
        description="Uma camada de acessibilidade, modo demo e pacotes de validação para famílias, escolas, ONGs, condomínios, prefeituras e empresas testarem o Guardian sem coletar dados reais."
        detail="Pilotos devem usar casos simulados ou anonimizados. O objetivo é medir clareza, utilidade e tempo de resposta sem invadir privacidade."
        actions={
          <>
            <Link href="/before-pix"><Button className="h-12 w-full sm:w-auto">Abrir demo principal</Button></Link>
            <Link href="/help-network"><Button variant="ghost" className="h-12 w-full sm:w-auto">Ver Rede de Ajuda</Button></Link>
          </>
        }
        aside={
          <div className="space-y-5">
            <StatusRail
              items={[
                {label:'Login', value:'não usado', tone:'ready'},
                {label:'Banco de dados', value:'desligado', tone:'ready'},
                {label:'Envio real', value:'desligado', tone:'warn'},
                {label:'Telefones', value:'não coletados', tone:'ready'},
              ]}
            />
            <p className="text-sm leading-6 text-slate-300">
              Prontidão de piloto com métricas agregadas, textos claros e sem dados sensíveis reais.
            </p>
          </div>
        }
      />

      <Card className="border-teal-300/20">
        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div>
            <div className="app-label">Demo Mode</div>
            <AppSectionTitle>Dados de demonstração, privacidade primeiro</AppSectionTitle>
          </div>
          <p className="app-body-text text-base font-semibold leading-7">
            A prontidão de piloto mede apenas sinais agregados. O Guardian não precisa guardar mensagens brutas, telefones, nomes reais ou histórico sensível para validar clareza, utilidade e tempo de resposta.
          </p>
        </div>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {privacySafeMetrics.map((metric)=> (
          <MetricPanel key={metric.label} label={metric.description} value={metric.value} detail={metric.label} tone="safe" />
        ))}
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="app-label">Pacotes de piloto</div>
            <AppSectionTitle>Validação real com risco baixo</AppSectionTitle>
          </div>
          <AppBadge>sem dados sensíveis</AppBadge>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {pilotPackages.map((pilot)=> (
            <article key={pilot.id} className="app-card-compact p-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="app-label">{pilot.duration}</div>
                  <AppCardTitle className="mt-2 text-xl">{pilot.title}</AppCardTitle>
                </div>
                <AppBadge className="app-badge-accent">piloto</AppBadge>
              </div>

              <dl className="mt-4 grid gap-3">
                <div className="app-action-panel">
                  <dt className="app-label">Público</dt>
                  <dd className="app-body-text mt-2 text-sm font-semibold">{pilot.audience}</dd>
                </div>
                <div className="app-action-panel">
                  <dt className="app-label">Objetivo</dt>
                  <dd className="app-body-text mt-2 text-sm font-semibold">{pilot.objective}</dd>
                </div>
              </dl>

              <div className="mt-4 grid gap-4">
                <Checklist title="Fluxo de uso" items={pilot.flow} />
                <Checklist title="Métricas" items={pilot.metrics} />
                <Checklist title="Requisitos" items={pilot.requirements} />
                <Checklist title="Riscos e limitações" items={pilot.risks} tone="risk" />
              </div>
            </article>
          ))}
        </div>
      </Card>

      <Card>
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <div className="app-label">Acessibilidade</div>
            <AppSectionTitle>Mais claro para idosos e pessoas leigas</AppSectionTitle>
            <p className="app-body-text mt-3 text-sm">
              Controles simples no topo e textos orientados à ação reduzem confusão no momento de risco.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {accessibilityChecklist.map((item)=> (
              <div key={item.label} className="app-action-panel">
                <div className="text-sm font-black text-white">{item.label}</div>
                <p className="app-body-text mt-2 text-sm font-semibold">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card className="border-dashed border-white/20">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="app-label">Critério de sucesso</div>
            <p className="app-body-text mt-2 text-sm font-semibold">
              Um piloto é bem-sucedido quando pessoas leigas entendem o risco, sabem quem acionar e conseguem pausar uma decisão perigosa sem entregar dados sensíveis ao sistema.
            </p>
          </div>
          <div className="app-action-panel text-sm font-bold text-slate-200">
            MVP educativo e preventivo
          </div>
        </div>
      </Card>
    </PageShell>
  )
}

function Checklist({title, items, tone='default'}:{title:string, items:string[], tone?:'default'|'risk'}){
  return (
    <div>
      <div className={`text-xs font-bold uppercase tracking-wide ${tone === 'risk' ? 'text-red-300' : 'text-slate-400'}`}>{title}</div>
      <ul className="mt-2 space-y-2">
        {items.map((item)=> (
          <li key={item} className="flex gap-2 text-sm font-semibold leading-6 text-slate-300">
            <span className={`mt-2 h-1.5 w-1.5 shrink-0 rounded-full ${tone === 'risk' ? 'bg-red-300' : 'bg-teal-300'}`} />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
