"use client"

import React, {useMemo, useState} from 'react'
import Link from 'next/link'
import Card from '@/components/Card'
import Button from '@/components/Button'
import {globalScenarios} from '@/lib/globalScenarios'

const regions = ['Todos', ...Array.from(new Set(globalScenarios.map((scenario)=>scenario.region)))]

export default function Simulator(){
  const [selectedRegion,setSelectedRegion]=useState('Todos')
  const scenarios = useMemo(()=> {
    if(selectedRegion === 'Todos') return globalScenarios
    return globalScenarios.filter((scenario)=>scenario.region === selectedRegion)
  },[selectedRegion])

  return (
    <main className="mx-auto max-w-6xl space-y-6 pb-12">
      <div className="overflow-hidden rounded-lg border border-slate-200 bg-white shadow-[0_14px_36px_rgba(15,23,42,0.07)]">
        <div className="grid lg:grid-cols-[1.1fr_0.9fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="inline-flex rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-slate-600">
              Global simulator
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">Simulador de cenários</h1>
            <p className="mt-4 max-w-3xl text-base leading-7 text-slate-600">
              Casos educativos e simulados para demonstrar como o Guardian sai do Pix e se aplica a pagamentos, links, senhas, documentos, códigos e apps remotos em vários mercados.
            </p>
          </div>
          <div className="border-t border-slate-200 bg-slate-950 p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">Cobertura</div>
            <div className="mt-5 grid grid-cols-2 gap-3">
              <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
                <div className="text-3xl font-black">{globalScenarios.length}</div>
                <div className="mt-1 text-xs font-bold uppercase tracking-wide text-slate-300">cenários</div>
              </div>
              <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
                <div className="text-3xl font-black">{regions.length - 1}</div>
                <div className="mt-1 text-xs font-bold uppercase tracking-wide text-slate-300">regiões</div>
              </div>
            </div>
          </div>
        </div>
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Filtro regional</div>
            <h2 className="mt-2 text-xl font-black tracking-tight text-slate-950">Cenários globais defensivos</h2>
          </div>
          <select
            value={selectedRegion}
            onChange={event=>setSelectedRegion(event.target.value)}
            className="h-11 rounded-lg border border-slate-200 bg-white px-4 text-sm font-bold text-slate-700 shadow-sm"
          >
            {regions.map((region)=> <option key={region} value={region}>{region}</option>)}
          </select>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {scenarios.map((scenario)=> (
          <Card key={scenario.id} className="flex flex-col">
            <div className="flex items-start justify-between gap-3">
              <div>
                <div className="text-xs font-bold uppercase tracking-[0.2em] text-slate-500">{scenario.region}</div>
                <h3 className="mt-2 text-lg font-black leading-6 text-slate-950">{scenario.title}</h3>
              </div>
              <span className={`rounded border px-3 py-1 text-[10px] font-bold uppercase tracking-wide ${scenario.expected_risk_level === 'critical' ? 'border-red-200 bg-red-50 text-red-700' : 'border-slate-200 bg-slate-50 text-slate-600'}`}>
                {scenario.expected_risk_level}
              </span>
            </div>
            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <p className="text-sm leading-6 text-slate-700">{scenario.message}</p>
            </div>
            <div className="mt-4 grid gap-2 text-sm">
              <p><span className="font-bold text-slate-950">Canal:</span> {scenario.channel}</p>
              <p><span className="font-bold text-slate-950">Ação:</span> {scenario.action_type}</p>
              <p><span className="font-bold text-slate-950">Golpe esperado:</span> {scenario.expected_scam_type}</p>
            </div>
            <p className="mt-4 flex-1 text-sm leading-6 text-slate-600">{scenario.global_relevance}</p>
            <div className="mt-5 flex flex-col gap-2 sm:flex-row">
              <Link href="/before-pix"><Button className="w-full">Analisar com Guardian</Button></Link>
              <Link href="/global"><Button variant="ghost" className="w-full">Contexto global</Button></Link>
            </div>
          </Card>
        ))}
      </div>
    </main>
  )
}
