"use client"

import React, {useState} from 'react'
import {analyzeTextML, analyzeURLML} from '@/lib/api'
import Button from '@/components/Button'
import Card from '@/components/Card'
import MLScamIntelligenceCard from '@/components/MLScamIntelligenceCard'
import {StatusBadge} from '@/components/AppPrimitives'
import type {MLAnalysis, UrlAnalysis} from '@/lib/types'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

const initialText = 'Cenário educativo simulado: troquei de número, preciso de Pix urgente agora e não liga.'
const initialUrl = 'https://nubank-seguranca-verificacao.xyz/login?token=abc'

function SignalList({items}:{items:string[]}){
  if(!items?.length){
    return <p className="text-sm font-semibold text-slate-500">Nenhum sinal forte detectado.</p>
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item)=> (
        <StatusBadge key={item} tone="warning">{item}</StatusBadge>
      ))}
    </div>
  )
}

function UrlResultCard({result}:{result:UrlAnalysis}){
  return (
    <Card>
      <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
        <div>
          <div className="app-label">URL Security Engine</div>
          <h2 className="app-section-title mt-2">{result.categoria}</h2>
        </div>
        <StatusBadge tone={result.risco === 'alto' ? 'danger' : 'neutral'}>
          {result.risco} · {result.score}
        </StatusBadge>
      </div>
      <p className="app-action-panel mt-4 break-all text-sm font-semibold text-slate-200">{result.url}</p>
      <div className="mt-4 grid gap-3 sm:grid-cols-3">
        <div className="app-card-compact">
          <div className="app-label">Regras</div>
          <div className="mt-1 text-sm font-black text-slate-100">{result.rules_used ? 'ativas' : 'inativas'}</div>
        </div>
        <div className="app-card-compact">
          <div className="app-label">API externa</div>
          <div className="mt-1 text-sm font-black text-slate-100">{result.external_api_used ? 'sim' : 'não'}</div>
        </div>
        <div className="app-card-compact">
          <div className="app-label">Marca</div>
          <div className="mt-1 text-sm font-black text-slate-100">{result.brand_impersonation?.brand || 'não detectada'}</div>
        </div>
      </div>
      <div className="mt-4">
        <SignalList items={result.sinais_detectados} />
      </div>
      <p className="app-body-text mt-4 text-sm font-semibold">{result.explicacao}</p>
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
        description="Laboratório técnico para demonstrar classificação defensiva de texto e URL com saída explicável."
        detail="Resultado não é prova absoluta. Use como apoio educativo e preventivo, sem API externa real nesta demo."
        aside={
          <div className="space-y-5">
            <div className="text-2xl font-semibold tracking-tight text-slate-800">Ferramenta demonstrativa</div>
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
            <div className="app-label">Texto</div>
            <h2 className="app-section-title mt-2">Analisar mensagem</h2>
          </div>
          <textarea
            value={text}
            onChange={event=>setText(event.target.value)}
            rows={8}
            className="app-input app-textarea"
          />
          <Button onClick={onAnalyzeText} disabled={loadingText} className="h-12 w-full">
            {loadingText ? 'Analisando texto...' : 'Analisar texto'}
          </Button>
        </Card>

        <Card className="space-y-5">
          <div>
            <div className="app-label">URL</div>
            <h2 className="app-section-title mt-2">Analisar link</h2>
          </div>
          <input
            value={url}
            onChange={event=>setUrl(event.target.value)}
            className="app-input h-12"
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

      <Card className="border-dashed border-slate-200">
        <div className="app-label">Transparência</div>
        <p className="app-body-text mt-2 text-sm font-semibold">
          O laboratório usa endpoints locais: POST /analisar, POST /analisar-url e GET /ml/status. Nenhuma API externa real é chamada nesta sprint.
        </p>
      </Card>
    </PageShell>
  )
}
