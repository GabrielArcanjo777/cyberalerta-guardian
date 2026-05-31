import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import AttackGlobe3D from '@/components/AttackGlobe3D'
import {globalApplicabilityRegions, globalScenarios, globalThreatPatterns} from '@/lib/globalScenarios'

export default function GlobalApplicabilityPage(){
  const featuredScenarios = globalScenarios.filter((scenario)=>[
    'br-fake-child-pix',
    'us-gift-card',
    'us-fake-tech-support',
    'eu-fake-delivery',
    'in-otp-code',
    'af-mobile-money',
  ].includes(scenario.id))

  return (
    <section className="mx-auto max-w-7xl space-y-7 pb-14">
      <div className="guardian-panel-dark overflow-hidden rounded-lg text-white">
        <div className="grid lg:grid-cols-[1.12fr_0.88fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="guardian-kicker">
              Productization
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight text-white sm:text-5xl">Global Applicability</h1>
            <p className="mt-4 max-w-3xl text-base font-semibold leading-7 text-slate-300">
              Guardian-led fraud prevention for families and institutions.
            </p>
            <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">
              Protected person + suspicious action + unverified identity + evidence trail = protective action before financial or identity damage.
            </p>
            <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">
              <Link href="/simulator"><Button className="h-12 w-full !border-white !bg-white !text-slate-950 hover:!bg-cyan-50 sm:w-auto">Ver cenarios globais</Button></Link>
              <Link href="/dashboard"><Button variant="ghost" className="h-12 w-full sm:w-auto">Impact Dashboard</Button></Link>
            </div>
          </div>
          <div className="border-t border-white/10 bg-white/[0.04] p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">Global mechanism</div>
            <div className="mt-5 space-y-3">
              {['Dangerous intent','Manipulation pattern','Unverified identity','Protective pause'].map((item,index)=> (
                <div key={item} className="flex items-center gap-3 rounded-lg border border-white/10 bg-white/[0.04] p-4">
                  <span className="flex h-8 w-8 items-center justify-center rounded-lg bg-white text-xs font-black text-slate-950">{index + 1}</span>
                  <span className="text-sm font-bold text-slate-200">{item}</span>
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>

      <AttackGlobe3D />

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {globalApplicabilityRegions.map((region)=> (
          <Card key={region.region}>
            <div className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">{region.region}</div>
            <h2 className="mt-2 text-xl font-black tracking-tight text-slate-950">{region.focus}</h2>
            <p className="mt-3 text-sm leading-6 text-slate-600">{region.description}</p>
          </Card>
        ))}
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_0.9fr]">
        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Global scenarios</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Exemplos defensivos e simulados</h2>
          <div className="mt-5 grid gap-3">
            {featuredScenarios.map((scenario)=> (
              <div key={scenario.id} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="flex flex-col gap-2 sm:flex-row sm:items-start sm:justify-between">
                  <div>
                    <div className="text-sm font-black text-slate-950">{scenario.title}</div>
                    <div className="mt-1 text-xs font-bold uppercase tracking-wide text-slate-500">{scenario.region} - {scenario.channel}</div>
                  </div>
                  <span className={`rounded border px-3 py-1 text-[10px] font-bold uppercase tracking-wide ${scenario.expected_risk_level === 'critical' ? 'border-red-200 bg-red-50 text-red-700' : 'border-slate-200 bg-white text-slate-600'}`}>
                    {scenario.expected_risk_level}
                  </span>
                </div>
                <p className="mt-3 text-sm leading-6 text-slate-600">{scenario.global_relevance}</p>
              </div>
            ))}
          </div>
        </Card>

        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Global threat patterns</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Taticas que cruzam fronteiras</h2>
          <div className="mt-5 flex flex-wrap gap-2">
            {globalThreatPatterns.map((pattern)=> (
              <span key={pattern} className="rounded border border-slate-200 bg-slate-50 px-3 py-2 text-xs font-bold uppercase tracking-wide text-slate-700">
                {pattern}
              </span>
            ))}
          </div>
          <div className="mt-6 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <div className="text-sm font-black text-slate-950">MVP vs. produto global real</div>
            <p className="mt-2 text-sm leading-6 text-slate-600">
              O MVP demonstra a tese. Um produto global real exige localizacao, revisao juridica, privacidade por regiao, parcerias locais e validacao continua por mercado.
            </p>
          </div>
        </Card>
      </div>
    </section>
  )
}
