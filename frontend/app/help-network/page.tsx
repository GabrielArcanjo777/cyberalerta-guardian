import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppBadge, AppCardTitle, AppSectionTitle} from '@/components/AppPrimitives'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'
import {alertTemplates, helpAudiences, helpPlaybooks} from '@/lib/helpPlaybooks'

export default function HelpNetworkPage(){
  return (
    <PageShell maxWidth="6xl">
      <PageHeader
        eyebrow="Help Network Mode"
        title="Rede de Ajuda Guardian"
        description="Proteção comunitária contra golpes digitais com consentimento, orientação mínima e privacidade por design."
        detail="Esta versão não envia alertas reais. Ela gera playbooks, mensagens sugeridas e próximos passos para quem protege."
        actions={
          <>
            <Link href="/before-pix"><Button className="h-12 w-full sm:w-auto">Analisar caso</Button></Link>
            <Link href="/family-console"><Button variant="ghost" className="h-12 w-full sm:w-auto">Guardian Console</Button></Link>
          </>
        }
        aside={
          <div className="space-y-5">
            <StatusRail
              items={[
                {label:'Alertas reais', value:'desligados', tone:'warn'},
                {label:'Telefones', value:'não coletados', tone:'ready'},
                {label:'Modo', value:'orientação', tone:'neutral'},
              ]}
            />
            <p className="text-sm leading-6 text-slate-300">
              Sem coleta de telefones reais, sem login, sem banco de dados e sem monitoramento automático.
            </p>
          </div>
        }
      />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {helpAudiences.map((audience)=> (
          <Card key={audience.title}>
            <div className="app-label">{audience.title}</div>
            <p className="app-body-text mt-3 text-sm font-semibold">{audience.description}</p>
          </Card>
        ))}
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="app-label">Playbooks</div>
            <AppSectionTitle>Ação rápida sem invadir privacidade</AppSectionTitle>
          </div>
          <AppBadge className="app-badge-accent">Demo consentida</AppBadge>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {helpPlaybooks.map((playbook)=> (
            <article key={playbook.id} className="app-card-compact p-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="app-label">{playbook.audience}</div>
                  <AppCardTitle className="mt-2">{playbook.title}</AppCardTitle>
                </div>
                <AppBadge>playbook</AppBadge>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {playbook.signals.map((signal)=> (
                  <AppBadge key={signal}>{signal}</AppBadge>
                ))}
              </div>

              <div className="mt-4 grid gap-3">
                <div className="app-action-panel">
                  <div className="app-label">Ação imediata</div>
                  <p className="app-body-text mt-2 text-sm font-semibold">{playbook.immediate_action}</p>
                </div>
                <div className="app-action-panel">
                  <div className="app-label">Quem acionar</div>
                  <p className="app-body-text mt-2 text-sm font-semibold">{playbook.who_to_notify.join(', ')}</p>
                </div>
                <div className="app-action-panel">
                  <div className="app-label">Mensagem sugerida</div>
                  <p className="app-body-text mt-2 text-sm font-semibold">"{playbook.suggested_message}"</p>
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-xs font-bold uppercase tracking-wide text-red-300">O que não fazer</div>
                  <ul className="mt-2 space-y-2">
                    {playbook.what_not_to_do.map((item)=> (
                      <li key={item} className="app-body-text text-sm font-semibold">{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wide text-teal-200">Próximos passos</div>
                  <ul className="mt-2 space-y-2">
                    {playbook.next_steps.map((item)=> (
                      <li key={item} className="app-body-text text-sm font-semibold">{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </article>
          ))}
        </div>
      </Card>

      <Card>
        <div className="app-label">Templates de alerta</div>
        <AppSectionTitle>Mensagens prontas para copiar e adaptar</AppSectionTitle>
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {alertTemplates.map((template)=> (
            <div key={template.id} className="app-action-panel">
              <div className="app-label">{template.audience}</div>
              <AppCardTitle className="mt-2 text-sm">{template.title}</AppCardTitle>
              <p className="app-body-text mt-3 text-sm font-semibold">"{template.message}"</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className="border-dashed border-white/20">
        <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr] lg:items-center">
          <div>
            <div className="app-label">Privacidade</div>
            <p className="app-body-text mt-2 text-sm font-semibold">
              A rede de ajuda funciona por consentimento: a pessoa decide o que compartilhar, a instituição recebe orientação mínima e nenhum dado sensível é persistido no MVP.
            </p>
          </div>
          <div className="app-action-panel text-sm font-bold text-slate-200">
            Sem envio real · Sem telefone real · Sem banco de dados
          </div>
        </div>
      </Card>
    </PageShell>
  )
}
