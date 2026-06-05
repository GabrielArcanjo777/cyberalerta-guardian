"use client"

import React, {useEffect, useState} from 'react'
import {getConnectorsStatus, postOCRPreview, postURLCheck} from '@/lib/api'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppCardTitle, AppSectionTitle, AppStatus} from '@/components/AppPrimitives'
import {connectorStatusClass, connectorStatusLabel} from '@/lib/appStatus'
import type {ConnectorResult, ConnectorStatus, OCRPreviewResponse} from '@/lib/types'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

const integrationCards = [
  {
    title:'Inteligência de URL',
    status:'mock' as const,
    tier:'mvp' as const,
    analyzes:'URLs suspeitas, domínio, parâmetros e palavras sensíveis.',
    doesNotAnalyze:'Não consulta Safe Browsing, VirusTotal ou urlscan.io no MVP.',
    privacy:'Análise local/simulada. Nenhum dado enviado a provedor externo.',
    consent:'Exige URL enviada voluntariamente.',
    availability:'Disponível no MVP em modo simulado.',
  },
  {
    title:'OCR de prints',
    status:'mock' as const,
    tier:'mvp' as const,
    analyzes:'Texto simulado de prints enviados pelo usuário.',
    doesNotAnalyze:'Não envia imagens reais para Azure Vision ou outro OCR.',
    privacy:'Nenhuma imagem real sai do ambiente no MVP.',
    consent:'Exige print/conteúdo enviado voluntariamente.',
    availability:'Disponível no MVP como preview simulado.',
  },
  {
    title:'E-mail com consentimento',
    status:'future' as const,
    tier:'future' as const,
    analyzes:'E-mails suspeitos encaminhados ou compartilhados com permissão.',
    doesNotAnalyze:'Não acessa caixa de e-mail real nem lê mensagens automaticamente.',
    privacy:'Microsoft Graph futuro com escopos limitados e opt-in.',
    consent:'Exige opt-in explícito.',
    availability:'Visão futura.',
  },
  {
    title:'Extensão do navegador',
    status:'future' as const,
    tier:'future' as const,
    analyzes:'URL atual e texto selecionado pelo usuário.',
    doesNotAnalyze:'Não coleta histórico de navegação.',
    privacy:'Minimização: somente URL/texto selecionado.',
    consent:'Exige ação manual do usuário.',
    availability:'Visão futura.',
  },
  {
    title:'WhatsApp Business com consentimento',
    status:'future' as const,
    tier:'future' as const,
    analyzes:'Mensagens compartilhadas por fluxo opt-in.',
    doesNotAnalyze:'Não lê WhatsApp pessoal nem monitora conversas.',
    privacy:'Somente canal aprovado, com consentimento e transparência.',
    consent:'Exige opt-in por canal.',
    availability:'Visão futura.',
  },
  {
    title:'Alertas familiares',
    status:'ready' as const,
    tier:'mvp' as const,
    analyzes:'Alertas simulados para contato de confiança.',
    doesNotAnalyze:'Não envia SMS, WhatsApp ou e-mail real no MVP.',
    privacy:'Painel simulado sem coleta de telefone real.',
    consent:'Acionado pelo fluxo da análise.',
    availability:'Disponível no MVP como simulação.',
  },
]

function tierLabel(tier:'mvp'|'future'){
  return tier === 'mvp' ? 'Disponível no MVP' : 'Visão futura'
}

export default function IntegrationsPage(){
  const [statuses,setStatuses]=useState<ConnectorStatus[]>([])
  const [statusMock,setStatusMock]=useState(false)
  const [url,setUrl]=useState('https://banco-seguro-atualizacao.com/login?token=abc123')
  const [urlResult,setUrlResult]=useState<ConnectorResult | null>(null)
  const [urlLoading,setUrlLoading]=useState(false)
  const [ocrContent,setOcrContent]=useState('print simulado: Mãe, troquei de número. Faz um Pix urgente agora.')
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

  const mvpCards = integrationCards.filter((card)=>card.tier === 'mvp')
  const futureCards = integrationCards.filter((card)=>card.tier === 'future')

  return (
    <PageShell>
      <PageHeader
        eyebrow="Conectores multicanal"
        title="Integrações e canais seguros"
        description="O Guardian evolui para múltiplos canais com consentimento, minimização e privacidade por design — sempre com proteção assistida antes do dano."
        detail="Nenhuma chave real, API paga, WhatsApp, e-mail ou provedor externo é chamado nesta demo."
        aside={
          <div className="space-y-5">
            <p className="text-base font-medium leading-7 text-slate-300">
              Todos os conectores rodam em modo simulado ou local por padrão.
            </p>
            <StatusRail
              items={[
                {label:'URL', value:'simulado', tone:'ready'},
                {label:'OCR', value:'preview', tone:'neutral'},
                {label:'Mensagens', value:'sem envio real', tone:'warn'},
              ]}
            />
          </div>
        }
      />

      <section>
        <div className="app-label">Disponível no MVP</div>
        <AppSectionTitle className="mt-1">Conectores ativos na demonstração</AppSectionTitle>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {mvpCards.map(card=> (
            <Card key={card.title}>
              <div className="flex items-start justify-between gap-3">
                <AppCardTitle>{card.title}</AppCardTitle>
                <AppStatus status={card.status} />
              </div>
              <div className="mt-4 space-y-2.5 app-body-text">
                <p><span className="font-medium text-slate-200">Analisa: </span>{card.analyzes}</p>
                <p><span className="font-medium text-slate-200">Não analisa: </span>{card.doesNotAnalyze}</p>
                <p><span className="font-medium text-slate-200">Privacidade: </span>{card.privacy}</p>
                <p><span className="font-medium text-slate-200">Consentimento: </span>{card.consent}</p>
              </div>
              <div className="app-integration-meta">{card.availability}</div>
            </Card>
          ))}
        </div>
      </section>

      <section className="mt-8">
        <div className="app-label">Visão futura</div>
        <AppSectionTitle className="mt-1">Canais planejados com opt-in</AppSectionTitle>
        <div className="mt-4 grid gap-4 md:grid-cols-2 xl:grid-cols-3">
          {futureCards.map(card=> (
            <Card key={card.title} className="opacity-95">
              <div className="flex items-start justify-between gap-3">
                <AppCardTitle>{card.title}</AppCardTitle>
                <AppStatus status={card.status} />
              </div>
              <div className="mt-4 space-y-2.5 app-body-text">
                <p><span className="font-medium text-slate-200">Analisa: </span>{card.analyzes}</p>
                <p><span className="font-medium text-slate-200">Não analisa: </span>{card.doesNotAnalyze}</p>
              </div>
              <div className="app-integration-meta">{tierLabel(card.tier)}</div>
            </Card>
          ))}
        </div>
      </section>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
          <div>
            <div className="app-label">Status dos adaptadores</div>
            <AppSectionTitle>Adaptadores do backend</AppSectionTitle>
            <p className="app-muted-text mt-2">Visão técnica dos provedores configurados na demo — sem expor segredos.</p>
          </div>
          {statusMock && <span className={connectorStatusClass('mock')}>fallback simulado</span>}
        </div>
        <div className="mt-5 grid gap-3 md:grid-cols-2">
          {statuses.map(connector=> (
            <div key={connector.provider} className="app-card-compact">
              <div className="flex items-start justify-between gap-3">
                <div>
                  <AppCardTitle className="text-sm">{connector.name}</AppCardTitle>
                  <div className="app-muted-text mt-1 text-xs">{connector.provider}</div>
                </div>
                <span className={connectorStatusClass(connector.mode)}>
                  {connectorStatusLabel(connector.mode)}
                </span>
              </div>
              <p className="app-body-text mt-3 text-sm">{connector.privacy}</p>
            </div>
          ))}
        </div>
      </Card>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <div className="app-label">Demo de URL</div>
          <AppSectionTitle>Verificar URL suspeita</AppSectionTitle>
          <div className="mt-5 space-y-4">
            <input
              value={url}
              onChange={event=>setUrl(event.target.value)}
              className="app-input"
            />
            <Button onClick={onURLCheck} disabled={urlLoading} className="h-12 w-full">
              {urlLoading ? 'Verificando...' : 'Verificar URL'}
            </Button>
            {urlResult && (
              <div className="space-y-3">
                {urlResult.__mock && (
                  <p className="app-action-panel text-sm font-medium text-cyan-100">
                    Modo demonstração: usando fallback local.
                  </p>
                )}
                <div className="app-action-panel">
                  <div className="app-label">Sinais de risco</div>
                  <div className="mt-3 flex flex-wrap gap-2">
                    {urlResult.risk_signals.map(signal=> (
                      <span key={signal} className="app-badge">{signal}</span>
                    ))}
                  </div>
                </div>
                <div className="app-callout">
                  <p className="app-callout-body">{urlResult.privacy_note}</p>
                </div>
              </div>
            )}
          </div>
        </Card>

        <Card>
          <div className="app-label">OCR de print suspeito</div>
          <AppSectionTitle>Simular OCR</AppSectionTitle>
          <p className="app-muted-text mt-2">Extrai texto de forma simulada para revisão defensiva — sem envio de imagem real.</p>
          <div className="mt-5 space-y-4">
            <textarea
              value={ocrContent}
              onChange={event=>setOcrContent(event.target.value)}
              rows={5}
              className="app-input app-textarea"
            />
            <Button onClick={onOCRPreview} disabled={ocrLoading} className="h-12 w-full">
              {ocrLoading ? 'Simulando...' : 'Simular OCR'}
            </Button>
            {ocrResult && (
              <div className="space-y-3">
                {ocrResult.__mock && (
                  <p className="app-action-panel text-sm font-medium text-cyan-100">
                    Modo demonstração: usando fallback local.
                  </p>
                )}
                <div className="app-action-panel">
                  <div className="app-label">Texto extraído (simulado)</div>
                  <p className="app-body-text mt-2 whitespace-pre-wrap">{ocrResult.extracted_text}</p>
                </div>
                <div className="app-callout">
                  <p className="app-callout-body">{ocrResult.privacy_note}</p>
                </div>
              </div>
            )}
          </div>
        </Card>
      </div>
    </PageShell>
  )
}
