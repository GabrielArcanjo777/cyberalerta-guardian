import React from 'react'
import Link from 'next/link'
import Card from '@/components/Card'
import {
  accessibilityChecklist,
  pilotPackages,
  privacySafeMetrics,
} from '@/lib/pilotReadiness'

export default function PilotReadiness(){
  return (
    <section className="guardian-product-page mx-auto max-w-6xl space-y-6 pb-12">
      <div className="guardian-page-header overflow-hidden">
        <div className="grid lg:grid-cols-[1.12fr_0.88fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="guardian-kicker">
              Pilot Readiness
            </div>
            <h1 className="mt-5 max-w-3xl text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">
              CyberAlerta pronto para piloto pequeno
            </h1>
            <p className="mt-4 max-w-3xl text-lg leading-8 text-slate-700">
              Uma camada de acessibilidade, modo demo e pacotes de validacao para familias, escolas, ONGs, condominios, prefeituras e empresas testarem o Guardian sem coletar dados reais.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Link
                href="/before-pix"
                className="inline-flex min-h-12 items-center justify-center rounded-lg bg-slate-950 px-5 py-3 text-sm font-bold text-white shadow-sm transition hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-950"
              >
                Abrir demo principal
              </Link>
              <Link
                href="/help-network"
                className="inline-flex min-h-12 items-center justify-center rounded-lg border border-slate-200 bg-white px-5 py-3 text-sm font-bold text-slate-700 transition hover:border-slate-300 hover:bg-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-slate-950"
              >
                Ver Rede de Ajuda
              </Link>
            </div>
          </div>
          <div className="border-t border-white/10 bg-white/[0.04] p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">MVP seguro</div>
            <p className="mt-4 text-2xl font-black tracking-tight">
              Pilotos devem usar casos simulados ou anonimizados.
            </p>
            <div className="mt-5 grid gap-3">
              {['Sem login','Sem banco de dados','Sem envio real','Sem telefones reais'].map((item)=> (
                <div key={item} className="rounded-lg border border-white/10 bg-white/[0.04] px-4 py-3 text-sm font-bold text-slate-200">
                  {item}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <Card className="border-slate-300 bg-slate-50/80">
        <div className="grid gap-4 lg:grid-cols-[0.9fr_1.1fr] lg:items-center">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Demo Mode</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Dados de demonstracao, privacidade primeiro</h2>
          </div>
          <p className="text-base font-semibold leading-7 text-slate-700">
            A prontidao de piloto mede apenas sinais agregados. O Guardian nao precisa guardar mensagens brutas, telefones, nomes reais ou historico sensivel para validar clareza, utilidade e tempo de resposta.
          </p>
        </div>
      </Card>

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-3">
        {privacySafeMetrics.map((metric)=> (
          <div key={metric.label} className="rounded-lg border border-slate-200 bg-white p-5 shadow-[0_10px_26px_rgba(15,23,42,0.05)]">
            <div className="text-xs font-bold uppercase tracking-wide text-slate-500">{metric.label}</div>
            <div className="mt-3 text-4xl font-black tracking-tight text-slate-950">{metric.value}</div>
            <p className="mt-3 text-sm font-semibold leading-6 text-slate-700">{metric.description}</p>
          </div>
        ))}
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Pacotes de piloto</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Validacao real com risco baixo</h2>
          </div>
          <span className="rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">
            sem dados sensiveis
          </span>
        </div>

        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          {pilotPackages.map((pilot)=> (
            <article key={pilot.id} className="rounded-lg border border-slate-200 bg-slate-50 p-5">
              <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                <div>
                  <div className="text-xs font-bold uppercase tracking-[0.18em] text-slate-500">{pilot.duration}</div>
                  <h3 className="mt-2 text-xl font-black leading-7 text-slate-950">{pilot.title}</h3>
                </div>
                <span className="rounded border border-slate-200 bg-white px-3 py-1 text-[10px] font-bold uppercase tracking-wide text-slate-600">
                  piloto
                </span>
              </div>

              <dl className="mt-4 grid gap-3">
                <div className="rounded-lg border border-slate-200 bg-white p-4">
                  <dt className="text-xs font-bold uppercase tracking-wide text-slate-500">Publico</dt>
                  <dd className="mt-2 text-sm font-semibold leading-6 text-slate-700">{pilot.audience}</dd>
                </div>
                <div className="rounded-lg border border-slate-200 bg-white p-4">
                  <dt className="text-xs font-bold uppercase tracking-wide text-slate-500">Objetivo</dt>
                  <dd className="mt-2 text-sm font-semibold leading-6 text-slate-700">{pilot.objective}</dd>
                </div>
              </dl>

              <div className="mt-4 grid gap-4">
                <Checklist title="Fluxo de uso" items={pilot.flow} />
                <Checklist title="Metricas" items={pilot.metrics} />
                <Checklist title="Requisitos" items={pilot.requirements} />
                <Checklist title="Riscos e limitacoes" items={pilot.risks} tone="risk" />
              </div>
            </article>
          ))}
        </div>
      </Card>

      <Card>
        <div className="grid gap-6 lg:grid-cols-[0.85fr_1.15fr]">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Acessibilidade</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Mais claro para idosos e pessoas leigas</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">
              A Sprint 17 adiciona controles simples no topo da aplicacao e reforca textos orientados a acao. O objetivo e reduzir confusao no momento de risco.
            </p>
          </div>
          <div className="grid gap-3 sm:grid-cols-2">
            {accessibilityChecklist.map((item)=> (
              <div key={item.label} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-sm font-black text-slate-950">{item.label}</div>
                <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">{item.detail}</p>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <Card className="border-dashed border-slate-300 bg-slate-50/70">
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Criterio de sucesso</div>
            <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">
              Um piloto e bem-sucedido quando pessoas leigas entendem o risco, sabem quem acionar e conseguem pausar uma decisao perigosa sem entregar dados sensiveis ao sistema.
            </p>
          </div>
          <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-bold text-slate-600">
            MVP educativo e preventivo
          </div>
        </div>
      </Card>
    </section>
  )
}

function Checklist({title, items, tone='default'}:{title:string, items:string[], tone?:'default'|'risk'}){
  return (
    <div>
      <div className={`text-xs font-bold uppercase tracking-wide ${tone === 'risk' ? 'text-red-600' : 'text-slate-500'}`}>{title}</div>
      <ul className="mt-2 space-y-2">
        {items.map((item)=> (
          <li key={item} className="flex gap-2 text-sm font-semibold leading-6 text-slate-700">
            <span className="mt-2 h-1.5 w-1.5 shrink-0 rounded-full bg-slate-950" />
            <span>{item}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}
