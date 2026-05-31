"use client"

import React, {useEffect, useState} from 'react'
import {getConnectorsStatus, postOCRPreview, postURLCheck} from '@/lib/api'
import Button from '@/components/Button'
import Card from '@/components/Card'
import type {ConnectorResult, ConnectorStatus, OCRPreviewResponse} from '@/lib/types'

const integrationCards = [
  {
    title:'URL Intelligence',
    status:'mock',
    analyzes:'URLs suspeitas, dominio, parametros e palavras sensiveis.',
    doesNotAnalyze:'Nao consulta Safe Browsing, VirusTotal ou urlscan.io no MVP.',
    privacy:'Analise local/mock. Nenhum dado enviado a provedor externo.',
    consent:'Exige URL enviada voluntariamente.',
    availability:'Disponivel no MVP em modo mock.',
  },
  {
    title:'OCR de prints',
    status:'mock',
    analyzes:'Texto simulado de prints enviados pelo usuario.',
    doesNotAnalyze:'Nao envia imagens reais para Azure Vision ou outro OCR.',
    privacy:'Nenhuma imagem real sai do ambiente no MVP.',
    consent:'Exige print/conteudo enviado voluntariamente.',
    availability:'Disponivel no MVP como preview simulado.',
  },
  {
    title:'E-mail opt-in',
    status:'future',
    analyzes:'E-mails suspeitos encaminhados ou compartilhados com permissao.',
    doesNotAnalyze:'Nao acessa caixa de e-mail real nem le mensagens automaticamente.',
    privacy:'Microsoft Graph futuro com escopos limitados e opt-in.',
    consent:'Exige opt-in explicito.',
    availability:'Visao futura.',
  },
  {
    title:'Browser extension',
    status:'future',
    analyzes:'URL atual e texto selecionado pelo usuario.',
    doesNotAnalyze:'Nao coleta historico de navegacao.',
    privacy:'Minimizacao: somente URL/texto selecionado.',
    consent:'Exige acao manual do usuario.',
    availability:'Visao futura.',
  },
  {
    title:'WhatsApp Business opt-in',
    status:'future',
    analyzes:'Mensagens compartilhadas por fluxo opt-in.',
    doesNotAnalyze:'Nao le WhatsApp pessoal nem monitora conversas.',
    privacy:'Somente canal aprovado, com consentimento e transparencia.',
    consent:'Exige opt-in por canal.',
    availability:'Visao futura.',
  },
  {
    title:'Family alerts',
    status:'ready',
    analyzes:'Alertas simulados para contato de confianca.',
    doesNotAnalyze:'Nao envia SMS, WhatsApp ou e-mail real no MVP.',
    privacy:'Painel simulado sem coleta de telefone real.',
    consent:'Acionado pelo fluxo da analise.',
    availability:'Disponivel no MVP como simulacao.',
  },
]

function statusClass(status:string){
  if(status === 'ready') return 'border-emerald-200 bg-emerald-50 text-emerald-700'
  if(status === 'future') return 'border-slate-200 bg-slate-50 text-slate-600'
  return 'border-amber-200 bg-amber-50 text-amber-700'
}

export default function IntegrationsPage(){
  const [statuses,setStatuses]=useState<ConnectorStatus[]>([])
  const [statusMock,setStatusMock]=useState(false)
  const [url,setUrl]=useState('https://banco-seguro-atualizacao.com/login?token=abc123')
  const [urlResult,setUrlResult]=useState<ConnectorResult | null>(null)
  const [urlLoading,setUrlLoading]=useState(false)
  const [ocrContent,setOcrContent]=useState('print simulado: Mae, troquei de numero. Faz um Pix urgente agora.')
  const [ocrResult,setOcrResult]=useState<OCRPreviewResponse | null>(null)
  const [ocrLoading,setOcrLoading]=useState(false)

  useEffect(()=>{
    getConnectorsStatus().then(response=>{
      setStatuses(response.connectors)
      setStatusMock(Boolean(response.__mock))
    })
  },[])

  async function onURLCheck(){
    setUrlLoading(true)
    const response = await postURLCheck(url)
    setUrlResult(response)
    setUrlLoading(false)
  }

  async function onOCRPreview(){
    setOcrLoading(true)
    const response = await postOCRPreview('mock', ocrContent)
    setOcrResult(response)
    setOcrLoading(false)
  }

  return (
    <section className="mx-auto max-w-7xl space-y-7 pb-14">
      <div className="guardian-panel-dark overflow-hidden rounded-lg text-white">
        <div className="grid lg:grid-cols-[1.12fr_0.88fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="guardian-kicker">
              Multi-channel connectors
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight text-white sm:text-5xl">Integracoes e canais seguros</h1>
            <p className="mt-4 max-w-3xl text-base font-semibold leading-7 text-slate-300">
              O Guardian pode evoluir para multiplos canais, sempre com consentimento e privacidade por design.
            </p>
          </div>
          <div className="border-t border-white/10 bg-white/[0.04] p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">MVP connector mode</div>
            <p className="mt-4 text-2xl font-black tracking-tight">Todos os conectores rodam em mock/local por padrao.</p>
            <p className="mt-4 text-sm leading-6 text-slate-300">
              Nenhuma chave real, API paga, WhatsApp, e-mail ou provedor externo e chamado nesta sprint.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
        {integrationCards.map(card=> (
          <Card key={card.title}>
            <div className="flex items-start justify-between gap-3">
              <h2 className="text-lg font-black tracking-tight text-slate-950">{card.title}</h2>
              <span className={`rounded border px-3 py-1 text-xs font-bold uppercase tracking-wide ${statusClass(card.status)}`}>
                {card.status}
              </span>
            </div>
            <div className="mt-4 space-y-3 text-sm leading-6">
              <p><span className="font-bold text-slate-950">Analisa: </span><span className="text-slate-600">{card.analyzes}</span></p>
              <p><span className="font-bold text-slate-950">Nao analisa: </span><span className="text-slate-600">{card.doesNotAnalyze}</span></p>
              <p><span className="font-bold text-slate-950">Privacidade: </span><span className="text-slate-600">{card.privacy}</span></p>
              <p><span className="font-bold text-slate-950">Consentimento: </span><span className="text-slate-600">{card.consent}</span></p>
            </div>
            <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 px-4 py-3 text-xs font-bold uppercase tracking-wide text-slate-600">
              {card.availability}
            </div>
          </Card>
        ))}
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Connector status</div>
            <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Backend adapters</h2>
          </div>
          {statusMock && <span className="rounded border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-sky-700">fallback mock</span>}
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {statuses.map(connector=> (
            <div key={connector.provider} className="rounded-lg border border-slate-200 bg-slate-50 p-4">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <div className="text-sm font-black text-slate-950">{connector.name}</div>
                  <div className="mt-1 text-xs font-semibold uppercase tracking-wide text-slate-500">{connector.provider}</div>
                </div>
                <span className={`rounded border px-2 py-1 text-[10px] font-bold uppercase tracking-wide ${statusClass(connector.mode)}`}>
                  {connector.mode}
                </span>
              </div>
              <p className="mt-3 text-sm leading-6 text-slate-600">{connector.privacy}</p>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">URL Check Demo</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Verificar URL suspeita</h2>
          <div className="mt-5 space-y-4">
            <input
              value={url}
              onChange={event=>setUrl(event.target.value)}
              className="h-12 w-full rounded-lg border border-slate-200 px-4 text-sm font-semibold text-slate-800 shadow-sm"
            />
            <Button onClick={onURLCheck} disabled={urlLoading} className="h-12 w-full">
              {urlLoading ? 'Verificando...' : 'Verificar URL'}
            </Button>
            {urlResult && (
              <div className="space-y-3">
                {urlResult.__mock && <p className="rounded-lg border border-sky-200 bg-sky-50 p-3 text-sm font-semibold text-sky-800">Modo demonstracao: usando fallback local.</p>}
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Sinais de risco</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {urlResult.risk_signals.map(signal=> (
                      <span key={signal} className="rounded border border-amber-200 bg-amber-50 px-3 py-1 text-xs font-bold text-amber-700">{signal}</span>
                    ))}
                  </div>
                </div>
                <p className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold leading-6 text-slate-700">{urlResult.privacy_note}</p>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">OCR de print suspeito</div>
          <h2 className="mt-2 text-2xl font-black tracking-tight text-slate-950">Simular OCR</h2>
          <div className="mt-5 space-y-4">
            <textarea
              value={ocrContent}
              onChange={event=>setOcrContent(event.target.value)}
              rows={5}
              className="w-full rounded-lg border border-slate-200 p-4 text-sm leading-6 text-slate-800 shadow-sm"
            />
            <Button onClick={onOCRPreview} disabled={ocrLoading} className="h-12 w-full">
              {ocrLoading ? 'Simulando...' : 'Simular OCR'}
            </Button>
            {ocrResult && (
              <div className="space-y-3">
                {ocrResult.__mock && <p className="rounded-lg border border-sky-200 bg-sky-50 p-3 text-sm font-semibold text-sky-800">Modo demonstracao: usando fallback local.</p>}
                <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                  <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Texto extraido simulado</div>
                  <p className="mt-2 whitespace-pre-wrap text-sm leading-6 text-slate-700">{ocrResult.extracted_text}</p>
                </div>
                <p className="rounded-lg border border-emerald-200 bg-emerald-50 p-4 text-sm font-semibold leading-6 text-slate-700">{ocrResult.privacy_note}</p>
              </div>
            )}
          </div>
        </Card>
      </div>
    </section>
  )
}
