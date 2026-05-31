import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {alertTemplates, helpAudiences, helpPlaybooks} from '@/lib/helpPlaybooks'

export default function HelpNetworkPage(){
  return (
    <section className="mx-auto max-w-6xl space-y-6 pb-12">
      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-[0_14px_36px_rgba(15,23,42,0.07)]">
        <div className="grid lg:grid-cols-[1.12fr_0.88fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="inline-flex rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-slate-600">
              Help Network Mode
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">Rede de Ajuda Guardian</h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              Proteção comunitária contra golpes digitais com consentimento e privacidade.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Link href="/before-pix"><Button className="h-12 w-full sm:w-auto">Analisar caso</Button></Link>
              <Link href="/family-console"><Button variant="ghost" className="h-12 w-full sm:w-auto">Family Console</Button></Link>
            </div>
          </div>
          <div className="border-t border-slate-200 bg-slate-950 p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">MVP seguro</div>
            <p className="mt-4 text-2xl font-black tracking-tight">
              Esta versão não envia alertas reais. Ela gera orientações e mensagens sugeridas.
            </p>
            <p className="mt-4 text-sm leading-6 text-slate-300">
              Sem coleta de telefones reais, sem login, sem banco de dados e sem monitoramento automático.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {helpAudiences.map((audience)=> (
          <Card key={audience.title}>
            <div className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">{audience.title}</div>
            <p className="mt-3 text-sm font-semibold leading-6 text-slate-700">{audience.description}</p>
          </Card>
        ))}
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Playbooks</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Ação rápida sem invadir privacidade</h2>
          </div>
          <span className="rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
            Demo consentida
          </span>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {helpPlaybooks.map((playbook)=> (
            <div key={playbook.id} className="rounded-lg border border-slate-200 bg-slate-50 p-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">{playbook.audience}</div>
                  <h3 className="mt-2 text-lg font-black leading-6 text-slate-950">{playbook.title}</h3>
                </div>
                <span className="rounded border border-slate-200 bg-white px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-slate-600">
                  playbook
                </span>
              </div>

              <div className="mt-4 flex flex-wrap gap-2">
                {playbook.signals.map((signal)=> (
                  <span key={signal} className="rounded border border-slate-200 bg-white px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">{signal}</span>
                ))}
              </div>

              <div className="mt-4 grid gap-3">
                <div className="rounded-lg border border-slate-200 bg-white p-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Ação imediata</div>
                  <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">{playbook.immediate_action}</p>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Quem acionar</div>
                  <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">{playbook.who_to_notify.join(', ')}</p>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Mensagem sugerida</div>
                  <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">"{playbook.suggested_message}"</p>
                </div>
              </div>

              <div className="mt-4 grid gap-4 md:grid-cols-2">
                <div>
                  <div className="text-xs font-bold uppercase tracking-wide text-red-500">O que não fazer</div>
                  <ul className="mt-2 space-y-2">
                    {playbook.what_not_to_do.map((item)=> (
                      <li key={item} className="text-sm font-semibold leading-5 text-slate-700">{item}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <div className="text-xs font-bold uppercase tracking-wide text-emerald-700">Próximos passos</div>
                  <ul className="mt-2 space-y-2">
                    {playbook.next_steps.map((item)=> (
                      <li key={item} className="text-sm font-semibold leading-5 text-slate-700">{item}</li>
                    ))}
                  </ul>
                </div>
              </div>
            </div>
          ))}
        </div>
      </Card>

      <Card>
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Templates de alerta</div>
        <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Mensagens prontas para copiar e adaptar</h2>
        <div className="mt-5 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {alertTemplates.map((template)=> (
            <div key={template.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">{template.audience}</div>
              <h3 className="mt-2 text-sm font-black text-slate-950">{template.title}</h3>
              <p className="mt-3 text-sm font-semibold leading-6 text-slate-700">"{template.message}"</p>
            </div>
          ))}
        </div>
      </Card>

      <Card className="border-dashed border-slate-300 bg-slate-50/70">
        <div className="grid gap-4 lg:grid-cols-[1fr_0.8fr] lg:items-center">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Privacidade</div>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">
              A rede de ajuda funciona por consentimento: a pessoa decide o que compartilhar, a instituição recebe orientação mínima e nenhum dado sensível é persistido no MVP.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-bold text-slate-600">
            Sem envio real · Sem telefone real · Sem banco de dados
          </div>
        </div>
      </Card>
    </section>
  )
}
