"use client"

import React, {useState} from 'react'
import {postIntakeAnalyze, postRedactPreview} from '@/lib/api'
import AIModeIndicator from '@/components/AIModeIndicator'
import AgentDecisionTrace from '@/components/AgentDecisionTrace'
import Button from '@/components/Button'
import Card from '@/components/Card'
import RiskScore from '@/components/RiskScore'
import TrustLockCard from '@/components/TrustLockCard'
import type {IntakeAnalysisResponse, IntakeChannel, RedactPreviewResponse} from '@/lib/types'

const initialMessage = 'Mae, troquei de numero. Faz um Pix urgente para essa chave: exemplo@email.com. Meu CPF e 123.456.789-00 e meu telefone e (21) 99999-9999.'

const channelOptions: {value:IntakeChannel,label:string,status:string,description:string}[] = [
  {value:'manual_text', label:'Colar mensagem manualmente', status:'Disponivel no MVP', description:'Cole apenas o trecho suspeito que voce quer analisar.'},
  {value:'screenshot_upload', label:'Enviar print', status:'Visao futura', description:'Upload com redaction antes da analise.'},
  {value:'email_forward', label:'Encaminhar e-mail suspeito', status:'Visao futura', description:'Encaminhamento voluntario de e-mail.'},
  {value:'browser_extension', label:'Extensao do navegador', status:'Visao futura', description:'Compartilhamento manual de pagina suspeita.'},
  {value:'share_sheet', label:'Share sheet', status:'Visao futura', description:'Compartilhar conteudo pelo menu do aparelho.'},
  {value:'whatsapp_business_opt_in', label:'WhatsApp Business opt-in', status:'Visao futura', description:'Somente com opt-in explicito e controlado.'},
  {value:'microsoft_graph_opt_in', label:'Microsoft Graph opt-in', status:'Visao futura', description:'Somente com permissao granular do usuario.'},
]

const actionOptions = [
  {value:'pix', label:'Pix'},
  {value:'link', label:'Link'},
  {value:'password', label:'Senha'},
  {value:'document', label:'Documento'},
  {value:'app', label:'App remoto'},
  {value:'sms_code', label:'Codigo SMS'},
]

function reportLabel(value:string){
  return value.replace(/_/g, ' ')
}

export default function IntakePage(){
  const [channel,setChannel]=useState<IntakeChannel>('manual_text')
  const [content,setContent]=useState(initialMessage)
  const [userConsent,setUserConsent]=useState(false)
  const [containsSensitiveData,setContainsSensitiveData]=useState(true)
  const [redactionRequested,setRedactionRequested]=useState(true)
  const [userName,setUserName]=useState('Dona Lucia')
  const [trustedContactName,setTrustedContactName]=useState('Gabriel')
  const [actionType,setActionType]=useState('pix')
  const [preview,setPreview]=useState<RedactPreviewResponse | null>(null)
  const [result,setResult]=useState<IntakeAnalysisResponse | null>(null)
  const [loadingPreview,setLoadingPreview]=useState(false)
  const [loadingAnalyze,setLoadingAnalyze]=useState(false)
  const [error,setError]=useState('')

  async function onPreview(){
    setError('')
    setLoadingPreview(true)
    const response = await postRedactPreview({content})
    setPreview(response)
    setLoadingPreview(false)
  }

  async function onAnalyze(){
    setError('')
    if(!userConsent){
      setError('Para analisar, marque o consentimento explicito. O Guardian nao monitora conversas sem sua decisao.')
      return
    }
    setLoadingAnalyze(true)
    const response = await postIntakeAnalyze({
      channel,
      content,
      user_consent: userConsent,
      contains_sensitive_data: containsSensitiveData,
      redaction_requested: redactionRequested,
      metadata_minimal: true,
      user_name: userName,
      trusted_contact_name: trustedContactName,
      action_type: actionType,
    })
    setResult(response)
    if(redactionRequested){
      setPreview({
        original_length: content.length,
        redacted_content: response.redacted_content,
        items_masked: response.privacy_report.sensitive_items_masked,
        __mock: response.__mock,
      })
    }
    setLoadingAnalyze(false)
  }

  const analysis = result?.analysis

  return (
    <section className="mx-auto max-w-7xl space-y-7 pb-14">
      <div className="guardian-panel-dark overflow-hidden rounded-lg text-white">
        <div className="grid lg:grid-cols-[1.12fr_0.88fr]">
          <div className="p-6 sm:p-8 lg:p-10">
            <div className="guardian-kicker">
              Privacy-first intake
            </div>
            <h1 className="mt-5 text-4xl font-black tracking-tight text-white sm:text-5xl">Enviar mensagem suspeita</h1>
            <p className="mt-4 max-w-3xl text-base font-semibold leading-7 text-slate-300">
              Voce escolhe o que enviar. O Guardian nao monitora suas conversas.
            </p>
          </div>
          <div className="border-t border-white/10 bg-white/[0.04] p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            <div className="text-xs font-bold uppercase tracking-[0.22em] text-cyan-300">Privacidade por design</div>
            <p className="mt-4 text-sm leading-6 text-slate-300">
              O CyberAlerta Guardian nao le suas conversas automaticamente. A analise acontece apenas quando voce decide compartilhar uma mensagem suspeita. Antes da analise, voce pode mascarar dados pessoais como CPF, telefone, e-mail e chaves Pix.
            </p>
          </div>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
        <Card className="overflow-hidden p-0">
          <div className="border-b border-slate-200 px-5 py-4 sm:px-6">
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Entrada voluntaria</div>
            <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Conteudo enviado pelo usuario</h2>
          </div>
          <div className="space-y-5 p-5 sm:p-6">
            <div>
              <label className="mb-2 block text-sm font-bold text-slate-700">Canal de entrada</label>
              <select
                value={channel}
                onChange={e=>setChannel(e.target.value as IntakeChannel)}
                className="h-12 w-full rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-800 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              >
                {channelOptions.map(option=> (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <label className="block">
              <span className="mb-2 block text-sm font-bold text-slate-700">Mensagem suspeita</span>
              <textarea
                value={content}
                onChange={e=>setContent(e.target.value)}
                rows={8}
                className="w-full rounded-lg border border-slate-200 bg-white p-4 text-sm leading-6 text-slate-900 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              />
            </label>

            <div className="grid gap-3 sm:grid-cols-3">
              <label className="block">
                <span className="mb-2 block text-sm font-bold text-slate-700">Pessoa</span>
                <input value={userName} onChange={e=>setUserName(e.target.value)} className="h-11 w-full rounded-lg border border-slate-200 px-3 text-sm font-semibold" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-bold text-slate-700">Contato</span>
                <input value={trustedContactName} onChange={e=>setTrustedContactName(e.target.value)} className="h-11 w-full rounded-lg border border-slate-200 px-3 text-sm font-semibold" />
              </label>
              <label className="block">
                <span className="mb-2 block text-sm font-bold text-slate-700">Acao</span>
                <select value={actionType} onChange={e=>setActionType(e.target.value)} className="h-11 w-full rounded-lg border border-slate-200 px-3 text-sm font-semibold">
                  {actionOptions.map(option=> <option key={option.value} value={option.value}>{option.label}</option>)}
                </select>
              </label>
            </div>

            <div className="space-y-3 rounded-lg border border-slate-200 bg-slate-50 p-4">
              <label className="flex items-start gap-3">
                <input type="checkbox" checked={userConsent} onChange={e=>setUserConsent(e.target.checked)} className="mt-1 h-5 w-5" />
                <span className="text-sm font-semibold leading-6 text-slate-700">
                  Eu escolhi compartilhar esta mensagem voluntariamente e autorizo a analise deste conteudo.
                </span>
              </label>
              <label className="flex items-start gap-3">
                <input type="checkbox" checked={redactionRequested} onChange={e=>setRedactionRequested(e.target.checked)} className="mt-1 h-5 w-5" />
                <span className="text-sm font-semibold leading-6 text-slate-700">
                  Mascarar dados pessoais antes da analise.
                </span>
              </label>
              <label className="flex items-start gap-3">
                <input type="checkbox" checked={containsSensitiveData} onChange={e=>setContainsSensitiveData(e.target.checked)} className="mt-1 h-5 w-5" />
                <span className="text-sm font-semibold leading-6 text-slate-700">
                  A mensagem pode conter dados pessoais ou sensiveis.
                </span>
              </label>
            </div>

            {error && <p className="rounded-lg border border-red-200 bg-red-50 p-3 text-sm font-semibold text-red-700">{error}</p>}

            <div className="grid gap-3 sm:grid-cols-2">
              <Button type="button" variant="ghost" onClick={onPreview} disabled={loadingPreview} className="h-12">
                {loadingPreview ? 'Mascarando...' : 'Pre-visualizar dados mascarados'}
              </Button>
              <Button type="button" onClick={onAnalyze} disabled={loadingAnalyze} className="h-12">
                {loadingAnalyze ? 'Analisando...' : 'Analisar com privacidade'}
              </Button>
            </div>
          </div>
        </Card>

        <div className="space-y-4">
          <Card>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Canais voluntarios</div>
            <div className="mt-4 grid gap-3">
              {channelOptions.map(option=> (
                <div key={option.value} className={`rounded-lg border p-4 ${option.value === channel ? 'border-slate-950 bg-slate-950 text-white' : 'border-slate-200 bg-slate-50'}`}>
                  <div className="flex items-start justify-between gap-3">
                    <div className="text-sm font-black">{option.label}</div>
                    <span className={`rounded border px-2 py-1 text-[10px] font-bold uppercase tracking-wide ${option.value === channel ? 'border-white/20 bg-white/10 text-slate-200' : 'border-slate-200 bg-white text-slate-600'}`}>
                      {option.status}
                    </span>
                  </div>
                  <p className={`mt-2 text-sm leading-5 ${option.value === channel ? 'text-slate-300' : 'text-slate-600'}`}>{option.description}</p>
                </div>
              ))}
            </div>
          </Card>
        </div>
      </div>

      {preview && (
        <Card>
          <div className="flex flex-col gap-3 sm:flex-row sm:items-start sm:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Preview de redaction</div>
              <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Texto mascarado antes da analise</h2>
            </div>
            {preview.__mock && <span className="rounded border border-sky-200 bg-sky-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-sky-700">Modo demonstracao</span>}
          </div>
          <div className="mt-4 rounded-lg border border-slate-200 bg-slate-50 p-4">
            <p className="whitespace-pre-wrap text-sm leading-6 text-slate-700">{preview.redacted_content}</p>
          </div>
          <div className="mt-4 flex flex-wrap gap-2">
            {preview.items_masked.length === 0 ? (
              <span className="rounded border border-slate-200 bg-white px-3 py-1 text-xs font-bold uppercase tracking-wide text-slate-500">Nenhum item mascarado</span>
            ) : preview.items_masked.map(item=> (
              <span key={item} className="rounded border border-emerald-200 bg-emerald-50 px-3 py-1 text-xs font-bold uppercase tracking-wide text-emerald-700">{reportLabel(item)}</span>
            ))}
          </div>
        </Card>
      )}

      {result && (
        <div className="space-y-5">
          {result.__mock && (
            <Card className="border-sky-200 bg-sky-50">
              <p className="text-sm font-semibold text-sky-800">Modo demonstracao: usando dados simulados.</p>
            </Card>
          )}

          <Card>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Privacy report</div>
            <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Relatorio de privacidade da analise</h2>
            <div className="mt-5 grid gap-3 md:grid-cols-3">
              <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
                <div className="text-xs font-bold uppercase tracking-wide text-emerald-700">Consentimento</div>
                <p className="mt-2 text-sm font-black text-slate-950">{result.privacy_report.consent_verified ? 'verificado' : 'ausente'}</p>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-bold uppercase tracking-wide text-slate-500">Monitoramento</div>
                <p className="mt-2 text-sm font-black text-slate-950">{result.privacy_report.monitoring ? 'ativo' : 'nao ha monitoramento'}</p>
              </div>
              <div className="rounded-lg border border-cyan-200 bg-cyan-50 p-4">
                <div className="text-xs font-bold uppercase tracking-wide text-cyan-700">Canal</div>
                <p className="mt-2 text-sm font-black text-slate-950">{reportLabel(result.privacy_report.channel)}</p>
              </div>
            </div>
            <p className="mt-4 text-sm font-semibold leading-6 text-slate-700">{result.privacy_report.message}</p>
          </Card>

          {analysis && (
            <div className="grid gap-6 lg:grid-cols-[minmax(280px,0.85fr)_minmax(0,1.4fr)]">
              <div className="space-y-4">
                <RiskScore score={analysis.risk_score} level={analysis.risk_level} />
                <TrustLockCard activated={analysis.trust_lock.activated} reason={analysis.trust_lock.reason} message={analysis.trust_lock.message} />
              </div>
              <div className="space-y-4">
                <AIModeIndicator mode={analysis.ai_mode} />
                <Card>
                  <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Resultado da analise</div>
                  <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">{analysis.scam_type}</h2>
                  <p className="mt-2 text-sm leading-6 text-slate-600">{analysis.report.summary}</p>
                </Card>
                <AgentDecisionTrace items={analysis.agent_decision_trace} decisionLedger={analysis.decision_ledger} />
              </div>
            </div>
          )}
        </div>
      )}
    </section>
  )
}
