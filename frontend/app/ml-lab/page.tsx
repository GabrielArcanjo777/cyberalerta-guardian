"use client"

import React, {useState} from 'react'
import {analyzeTextML, analyzeURLML} from '@/lib/api'
import Button from '@/components/Button'
import Card from '@/components/Card'
import MLScamIntelligenceCard from '@/components/MLScamIntelligenceCard'
import type {MLAnalysis, UrlAnalysis} from '@/lib/types'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

const initialText = 'Cenario educativo simulado: troquei de numero, preciso de Pix urgente agora e nao liga.'
const initialUrl = 'https://nubank-seguranca-verificacao.xyz/login?token=abc'

function SignalList({items}:{items:string[]}){
  if(!items?.length){
    return <p className="text-sm font-semibold text-slate-500">Nenhum sinal forte detectado.</p>
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item)=> (
        <span key={item} className="rounded border border-slate-200 bg-white px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-600">{item}</span>
      ))}
    </div>
  )
}

function UrlResultCard({result}:{result:UrlAnalysis}){
  return (
    <Card>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">URL Security Engine</div>
          <h2 className="mt-2 text-xl font-black tracking-tight text-slate-950">{result.categoria}</h2>
        </div>
        <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${result.risco === 'alto' ? 'border-red-200 bg-red-50 text-red-700' : 'border-slate-200 bg-slate-50 text-slate-600'}`}>
          {result.risco} · {result.score}
        </span>
      </div>
      <p className="mt-4 break-all rounded-lg border border-slate-200 bg-slate-50 p-3 text-sm font-semibold text-slate-700">{result.url}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Regras</div>
          <div className="mt-1 text-sm font-black text-slate-950">{result.rules_used ? 'ativas' : 'inativas'}</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-bold uppercase tracking-wide text-slate-500">API externa</div>
          <div className="mt-1 text-sm font-black text-slate-950">{result.external_api_used ? 'sim' : 'nao'}</div>
        </div>
        <div className="rounded-lg border border-slate-200 bg-slate-50 p-3">
          <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Marca</div>
          <div className="mt-1 text-sm font-black text-slate-950">{result.brand_impersonation?.brand || 'nao detectada'}</div>
        </div>
      </div>
      <div className="mt-4">
        <SignalList items={result.sinais_detectados} />
      </div>
      <p className="mt-4 text-sm font-semibold leading-6 text-slate-700">{result.explicacao}</p>
    </Card>
  )
}

export default function MLLabPage(){
  const [text,setText]=useState(initialText)
  const [url,setUrl]=useState(initialUrl)
  const [textResult,setTextResult]=useState<MLAnalysis | null>(null)
  const [urlResult,setUrlResult]=useState<UrlAnalysis | null>(null)
  const [loadingText,setLoadingText]=useState(false)
  const [loadingUrl,setLoadingUrl]=useState(false)

  async function onAnalyzeText(){
    setLoadingText(true)
    const result = await analyzeTextML(text)
    setTextResult(result)
    setLoadingText(false)
  }

  async function onAnalyzeUrl(){
    setLoadingUrl(true)
    const result = await analyzeURLML(url)
    setUrlResult(result)
    setLoadingUrl(false)
  }

  return (
    <PageShell>
      <PageHeader
        eyebrow="ML Scam Intelligence"
        title="ML Scam Intelligence Lab"
        description="Laboratorio tecnico para demonstrar classificacao defensiva de texto e URL com saida explicavel."
        detail="Resultado nao e prova absoluta. Use como apoio educativo e preventivo, sem API externa real nesta demo."
        aside={
          <div className="space-y-5">
            <div className="text-2xl font-semibold tracking-tight text-white">Ferramenta demonstrativa</div>
            <StatusRail
              items={[
                {label:'Texto', value:'POST /analisar', tone:'ready'},
                {label:'URL', value:'POST /analisar-url', tone:'ready'},
                {label:'Status', value:'GET /ml/status', tone:'neutral'},
              ]}
            />
          </div>
        }
      />

      <div className="grid gap-6 lg:grid-cols-2">
        <Card className="space-y-5">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Texto</div>
            <h2 className="mt-2 text-xl font-black tracking-tight text-slate-950">Analisar mensagem</h2>
          </div>
          <textarea
            value={text}
            onChange={event=>setText(event.target.value)}
            rows={8}
            className="w-full rounded-lg border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
          <Button onClick={onAnalyzeText} disabled={loadingText} className="h-12 w-full">
            {loadingText ? 'Analisando texto...' : 'Analisar texto'}
          </Button>
        </Card>

        <Card className="space-y-5">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">URL</div>
            <h2 className="mt-2 text-xl font-black tracking-tight text-slate-950">Analisar link</h2>
          </div>
          <input
            value={url}
            onChange={event=>setUrl(event.target.value)}
            className="h-12 w-full rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
          />
          <Button onClick={onAnalyzeUrl} disabled={loadingUrl} className="h-12 w-full">
            {loadingUrl ? 'Analisando URL...' : 'Analisar URL'}
          </Button>
        </Card>
      </div>

      {(textResult || urlResult) && (
        <div className="grid gap-6 lg:grid-cols-2">
          {textResult && <MLScamIntelligenceCard ml={textResult} />}
          {urlResult && <UrlResultCard result={urlResult} />}
        </div>
      )}

      <Card className="border-dashed border-slate-300 bg-slate-50/70">
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Transparencia</div>
        <p className="mt-2 text-sm font-semibold leading-6 text-slate-700">
          O laboratorio usa endpoints locais: POST /analisar, POST /analisar-url e GET /ml/status. Nenhuma API externa real e chamada nesta sprint.
        </p>
      </Card>
    </PageShell>
  )
}
