"use client"

import React, {useMemo, useState} from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import {
  ActionPanel,
  CommandPanel,
  EvidencePanel,
  MetricPanel,
  PageHeader,
  PageShell,
  SectionHeader,
  StatusRail,
} from '@/components/CommandCenter'
import {globalScenarios, type GlobalScenario} from '@/lib/globalScenarios'

const allLabel = 'Todos'

const regions = [allLabel, ...Array.from(new Set(globalScenarios.map((scenario)=>scenario.region)))]
const risks = [allLabel, ...Array.from(new Set(globalScenarios.map((scenario)=>scenario.expected_risk_level)))]
const channels = [allLabel, ...Array.from(new Set(globalScenarios.map((scenario)=>scenario.channel)))]
const actionTypes = Array.from(new Set(globalScenarios.map((scenario)=>scenario.action_type)))

function riskClass(risk:string){
  if(risk === 'critical') return 'border-red-200 bg-red-50 text-red-800'
  if(risk === 'high') return 'border-amber-200 bg-amber-50 text-amber-800'
  if(risk === 'medium') return 'border-cyan-200 bg-cyan-50 text-cyan-800'
  return 'border-slate-200 bg-slate-50 text-slate-700'
}

function riskLabel(risk:string){
  if(risk === 'critical') return 'crítico'
  if(risk === 'high') return 'alto'
  if(risk === 'medium') return 'médio'
  if(risk === 'low') return 'baixo'
  return risk
}

function actionLabel(action:string){
  const labels:Record<string,string> = {
    pix: 'Pix / transferência',
    link: 'Link suspeito',
    password: 'Senha',
    document: 'Documento',
    app: 'App remoto',
    sms_code: 'Código SMS',
  }
  return labels[action] || action
}

function dominantRisk(items:GlobalScenario[]){
  const counts = items.reduce<Record<string,number>>((acc,scenario)=> {
    acc[scenario.expected_risk_level] = (acc[scenario.expected_risk_level] || 0) + 1
    return acc
  },{})
  return Object.entries(counts).sort((a,b)=>b[1] - a[1])[0]?.[0] || 'n/a'
}

function scenarioBrief(scenario:GlobalScenario){
  const actionMap:Record<string,string> = {
    pix: 'transferência urgente',
    link: 'clique em link suspeito',
    password: 'compartilhamento de senha',
    document: 'envio de documento',
    app: 'instalação de app remoto',
    sms_code: 'envio de código SMS',
  }

  return `Simula ${actionMap[scenario.action_type] || 'ação sensível'} por ${scenario.channel}, com identidade ou autoridade não verificada e pressão para agir rápido.`
}

function ScenarioCard({scenario,featured=false}:{scenario:GlobalScenario,featured?:boolean}){
  return (
    <article className={`guardian-scenario-card ${featured ? 'guardian-scenario-featured' : ''}`}>
      <div className="guardian-scenario-status" />
      <div className="flex flex-col gap-4 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="guardian-panel-eyebrow">{scenario.region} / {scenario.channel}</div>
          <h3 className="mt-2 text-xl font-semibold leading-7 text-slate-800">{scenario.title}</h3>
        </div>
        <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${riskClass(scenario.expected_risk_level)}`}>
          {riskLabel(scenario.expected_risk_level)}
        </span>
      </div>

      <div className="mt-3 grid grid-cols-3 gap-3">
        <div className="guardian-console-mini-card">
          <div className="text-xs font-semibold uppercase text-slate-500">Canal</div>
          <div className="mt-2 text-sm font-semibold text-slate-700">{scenario.channel}</div>
        </div>
        <div className="guardian-console-mini-card">
          <div className="text-xs font-semibold uppercase text-slate-500">Ação perigosa</div>
          <div className="mt-2 text-sm font-semibold text-slate-700">{actionLabel(scenario.action_type)}</div>
        </div>
        <div className="guardian-console-mini-card">
          <div className="text-xs font-semibold uppercase text-slate-500">Padrão esperado</div>
          <div className="mt-2 text-sm font-semibold text-slate-700">{scenario.expected_scam_type}</div>
        </div>
      </div>

      <div className="mt-5 border-l border-teal-300 bg-teal-50 p-4">
        <p className="text-sm font-semibold leading-6 text-slate-700">{scenarioBrief(scenario)}</p>
        <p className="mt-3 text-sm leading-6 text-slate-400">{scenario.global_relevance}</p>
      </div>

      <div className="mt-5 flex flex-col gap-2 sm:flex-row">
        <Link href="/before-pix" className="sm:flex-1">
          <Button className="w-full">Executar no Guardian</Button>
        </Link>
        <Link href="/global" className="sm:flex-1">
          <Button variant="ghost" className="w-full">Ver contexto global</Button>
        </Link>
      </div>
    </article>
  )
}

export default function Simulator(){
  const [selectedRegion,setSelectedRegion]=useState(allLabel)
  const [selectedRisk,setSelectedRisk]=useState(allLabel)
  const [selectedChannel,setSelectedChannel]=useState(allLabel)

  const scenarios = useMemo(()=> {
    return globalScenarios.filter((scenario)=> {
      const regionMatches = selectedRegion === allLabel || scenario.region === selectedRegion
      const riskMatches = selectedRisk === allLabel || scenario.expected_risk_level === selectedRisk
      const channelMatches = selectedChannel === allLabel || scenario.channel === selectedChannel
      return regionMatches && riskMatches && channelMatches
    })
  },[selectedRegion,selectedRisk,selectedChannel])

  const featuredScenario = scenarios.find((scenario)=>scenario.expected_risk_level === 'critical') || scenarios[0] || globalScenarios[0]
  const scenarioList = scenarios.filter((scenario)=>scenario.id !== featuredScenario.id)
  const riskDominant = dominantRisk(scenarios.length ? scenarios : globalScenarios)

  return (
    <PageShell maxWidth="7xl" className="guardian-light-page">
      <PageHeader
        eyebrow="Simulação defensiva"
        title="Laboratório de cenários globais"
        description="Teste padrões simulados de fraude por região, canal e ação perigosa para validar o comportamento defensivo do Guardian."
        detail="O laboratório demonstra como a mesma camada de pausa protetiva se adapta a Pix, links, senhas, documentos, códigos e apps remotos em mercados diferentes."
        aside={
          <div className="space-y-5">
            <StatusRail
              items={[
                {label:'Cenários', value:String(globalScenarios.length), tone:'neutral'},
                {label:'Regiões', value:String(regions.length - 1), tone:'ready'},
                {label:'Risco dominante', value:riskLabel(riskDominant), tone:riskDominant === 'critical' ? 'risk' : 'warn'},
              ]}
            />
            <p className="text-sm leading-6 text-slate-600">
              Simulações defensivas: nenhuma mensagem real é enviada, nenhum pagamento é executado e nenhum dado real é persistido.
            </p>
          </div>
        }
      />

      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-5">
        <MetricPanel label="Cenários simulados" value={globalScenarios.length} detail="catálogo" tone="cyan" />
        <MetricPanel label="Regiões cobertas" value={regions.length - 1} detail="mercados" />
        <MetricPanel label="Canais simulados" value={channels.length - 1} detail="entrada" />
        <MetricPanel label="Ações perigosas" value={actionTypes.length} detail="vetores" tone="safe" />
        <MetricPanel label="Nível dominante" value={riskLabel(riskDominant)} detail="risco" tone={riskDominant === 'critical' ? 'risk' : 'default'} />
      </div>

      <CommandPanel
        eyebrow="Filtro de cenários"
        title="Selecionar superfície de risco"
        description="Filtre a biblioteca por região, risco e canal para montar uma demo defensiva sem depender de dados reais."
      >
        <div className="grid gap-4 lg:grid-cols-[1fr_1fr_1fr_auto] lg:items-end">
          <label className="block">
            <span className="mb-2 block text-xs font-semibold uppercase text-slate-500">Região</span>
            <select value={selectedRegion} onChange={event=>setSelectedRegion(event.target.value)} className="h-12 w-full rounded-md border border-slate-500/40 px-4 text-sm font-semibold">
              {regions.map((region)=> <option key={region} value={region}>{region}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-xs font-semibold uppercase text-slate-500">Risco</span>
            <select value={selectedRisk} onChange={event=>setSelectedRisk(event.target.value)} className="h-12 w-full rounded-md border border-slate-500/40 px-4 text-sm font-semibold">
              {risks.map((risk)=> <option key={risk} value={risk}>{risk === allLabel ? risk : riskLabel(risk)}</option>)}
            </select>
          </label>
          <label className="block">
            <span className="mb-2 block text-xs font-semibold uppercase text-slate-500">Canal</span>
            <select value={selectedChannel} onChange={event=>setSelectedChannel(event.target.value)} className="h-12 w-full rounded-md border border-slate-500/40 px-4 text-sm font-semibold">
              {channels.map((channel)=> <option key={channel} value={channel}>{channel}</option>)}
            </select>
          </label>
          <div className="rounded-md border border-cyan-300/20 bg-cyan-300/10 px-4 py-3 text-sm font-semibold text-cyan-100">
            {scenarios.length} cenários
          </div>
        </div>
      </CommandPanel>

      <div className="grid items-start gap-6 xl:grid-cols-[0.9fr_1.1fr]">
        <EvidencePanel
          eyebrow="Cenário recomendado"
          title="Demo crítica para avaliação"
          description="Use este caso para demonstrar decisão rastreável, pausa protetiva e ponte com contato seguro."
        >
          <ScenarioCard scenario={featuredScenario} featured />
        </EvidencePanel>

        <ActionPanel
          eyebrow="Como interpretar"
          title="Como interpretar a simulação"
          description="Cada cenário testa uma combinação defensiva: canal, ação sensível, identidade não verificada e próxima ação segura."
        >
          <div className="grid gap-3">
            {[
              ['Região', 'Mostra adaptação cultural e de meio de pagamento.'],
              ['Canal', 'Separa SMS, e-mail, telefone, social e app de mensagem.'],
              ['Ação perigosa', 'Destaca Pix, link, senha, documento, código ou app remoto.'],
              ['Risco', 'Ajuda o avaliador a enxergar quando o Trust Lock deve aparecer.'],
            ].map(([title,body])=> (
              <div key={title} className="guardian-console-mini-card">
                <div className="text-sm font-semibold text-slate-700">{title}</div>
                <p className="mt-1 text-sm leading-6 text-slate-400">{body}</p>
              </div>
            ))}
          </div>
        </ActionPanel>
      </div>

      <CommandPanel>
        <SectionHeader
          eyebrow="Biblioteca de cenários"
          title="Cenários simulados defensivos"
          description="Cards com barra de status, contexto e ação clara para abrir a análise do Guardian."
        />
        <div className="grid gap-4 lg:grid-cols-2">
          {scenarioList.map((scenario)=> <ScenarioCard key={scenario.id} scenario={scenario} />)}
        </div>
        {scenarioList.length === 0 && (
          <div className="rounded-md border border-slate-300 bg-slate-50 p-5 text-sm font-semibold text-slate-700">
            Nenhum outro cenário encontrado com esses filtros. Ajuste a superfície de risco para ampliar a simulação.
          </div>
        )}
      </CommandPanel>
    </PageShell>
  )
}
