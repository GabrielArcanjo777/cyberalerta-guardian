"use client"

import React, {useEffect, useState} from 'react'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppStatus} from '@/components/AppPrimitives'
import {getSimpleChannelStatus, postSimpleChannelSubmit} from '@/lib/api'
import type {SimpleChannelStatusResponse, SimpleChannelSubmitResponse} from '@/lib/types'

const defaultMessage = 'Mãe, troquei de número. Preciso fazer um Pix urgente.'

type AnalysisEntry = {
  id: string
  role: 'submitted' | 'system' | 'typing'
  text: string
}

export default function SimpleChannelChat(){
  const [alias,setAlias]=useState('Dona Lúcia')
  const [trustedContact,setTrustedContact]=useState('Gabriel')
  const [draft,setDraft]=useState(defaultMessage)
  const [consent,setConsent]=useState(false)
  const [messages,setMessages]=useState<AnalysisEntry[]>([
    {
      id: 'welcome',
      role: 'system',
      text: 'Ingresso simulado para análise local. Nenhuma resposta será enviada ao remetente.',
    },
  ])
  const [status,setStatus]=useState<SimpleChannelStatusResponse | null>(null)
  const [lastResult,setLastResult]=useState<SimpleChannelSubmitResponse | null>(null)
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState('')

  useEffect(()=>{
    getSimpleChannelStatus().then(setStatus).catch(()=>setStatus(null))
  },[])

  async function onSend(){
    setError('')
    if(!consent){
      setError('Marque o consentimento para encaminhar a mensagem ao Guardian.')
      return
    }
    if(!draft.trim()){
      setError('Digite a mensagem suspeita que você quer revisar.')
      return
    }

    const userText = draft.trim()
    const userMessage:AnalysisEntry = {
      id: `user-${Date.now()}`,
      role: 'submitted',
      text: userText,
    }
    const analyzingId = `typing-${Date.now()}`

    setMessages(prev=>[
      ...prev,
      userMessage,
      {id: analyzingId, role: 'typing', text: 'Guardian está analisando com calma...'},
    ])
    setLoading(true)
    setDraft('')

    const response = await postSimpleChannelSubmit({
      protected_person_alias: alias.trim() || 'Pessoa protegida',
      channel: 'whatsapp_mock',
      content_type: 'text',
      content: userText,
      consent: true,
      trusted_contact_alias: trustedContact.trim() || undefined,
    })

    setLoading(false)
    setLastResult(response)

    setMessages(prev=>{
      const withoutTyping = prev.filter(message=>message.id !== analyzingId)
      const next:AnalysisEntry[] = [...withoutTyping]
      if(response.admin_case_created){
        next.push({
          id: `status-${Date.now()}`,
          role: 'system',
          text: response.__mock
            ? `Caso simulado registrado para revisão por ${trustedContact || 'contato de confiança'}. Modo demonstração local.`
            : `Caso ${response.channel_case_id} registrado no console. ${trustedContact || 'Seu contato de confiança'} pode acompanhar por lá.`,
        })
      } else {
        next.push({
          id: `status-${Date.now()}`,
          role: 'system',
          text: 'Análise concluída. Nenhuma ação urgente é necessária agora.',
        })
      }
      if(response.__mock){
        next.push({
          id: `mock-${Date.now()}`,
          role: 'system',
          text: 'Análise gerada em modo demonstração (backend indisponível). Nenhuma mensagem foi enviada.',
        })
      }
      return next
    })
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <Card className="flex flex-col overflow-hidden p-0">
        <div className="border-b border-white/10 bg-slate-950/70 px-4 py-3 sm:px-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="app-label text-emerald-300/90">Ingresso mock</div>
              <div className="mt-1 text-sm font-semibold text-white">Fila de análise · somente leitura</div>
            </div>
            <AppStatus status="mock" />
          </div>
        </div>

        <div className="flex min-h-[320px] flex-1 flex-col gap-3 overflow-y-auto p-4 sm:p-5">
          {messages.map(message=> (
            <div
              key={message.id}
              className={
                message.role === 'submitted'
                  ? 'w-full rounded-md border border-emerald-400/25 bg-emerald-950/35 px-3 py-2.5 text-sm leading-6 text-emerald-50'
                  : message.role === 'typing'
                      ? 'mr-auto max-w-[88%] rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm italic text-slate-400'
                      : 'mx-auto max-w-[95%] rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-center text-xs leading-5 text-slate-400'
              }
            >
              {message.role === 'submitted' && (
                <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-300/80">
                  Trecho encaminhado por {alias}
                </div>
              )}
              {message.text}
            </div>
          ))}
        </div>

        <div className="border-t border-white/10 p-4 sm:p-5">
          <label className="block">
            <span className="app-label">Mensagem suspeita</span>
            <textarea
              value={draft}
              onChange={event=>setDraft(event.target.value)}
              rows={3}
              className="app-input app-textarea mt-2"
              placeholder="Cole ou digite o que você recebeu..."
              disabled={loading}
            />
          </label>
          <label className="mt-3 flex items-start gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={consent}
              onChange={event=>setConsent(event.target.checked)}
              className="mt-1"
              disabled={loading}
            />
            <span>
              Autorizo o envio voluntário deste trecho para análise defensiva. O Guardian não monitora conversas privadas.
            </span>
          </label>
          {error && <p className="mt-3 text-sm font-medium text-amber-200">{error}</p>}
          <Button onClick={onSend} disabled={loading} className="mt-4 h-12 w-full">
            {loading ? 'Analisando...' : 'Encaminhar ao Guardian'}
          </Button>
        </div>
      </Card>

      <div className="space-y-4">
        <Card>
          <div className="app-label">Pessoa protegida</div>
          <input
            value={alias}
            onChange={event=>setAlias(event.target.value)}
            className="app-input mt-2"
            aria-label="Nome da pessoa protegida"
          />
          <div className="app-label mt-4">Contato de confiança</div>
          <input
            value={trustedContact}
            onChange={event=>setTrustedContact(event.target.value)}
            className="app-input mt-2"
            aria-label="Nome do contato de confiança"
          />
          <p className="app-muted-text mt-3">
            Você encaminha o trecho, o Guardian analisa em silêncio e registra o resultado. Só um golpe explícito pode gerar alerta ao contato de confiança; o remetente nunca recebe resposta.
          </p>
        </Card>

        <Card>
          <div className="app-label">Status do canal</div>
          {status ? (
            <div className="mt-3 space-y-2 app-body-text text-sm">
              <p><span className="text-slate-200">Modo:</span> {status.mode}</p>
              <p>{status.privacy_note}</p>
              <p className="text-amber-200/90">{status.demo_note}</p>
            </div>
          ) : (
            <p className="app-muted-text mt-3">Carregando status do canal...</p>
          )}
        </Card>

        {lastResult && (
          <Card>
            <div className="app-label">Resumo (para você)</div>
            <div className="mt-3 grid gap-2 text-sm">
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">Risco</span>
                <span className="font-semibold capitalize text-white">{lastResult.risk_level}</span>
              </div>
              {lastResult.trust_lock_recommended && (
                <p className="app-body-text text-amber-100/90">Pausa recomendada antes de qualquer Pix ou clique.</p>
              )}
              <div className="mt-2 rounded-md border border-cyan-400/20 bg-cyan-950/20 p-3">
                <div className="app-label text-cyan-200/90">Orientação no painel · não enviada</div>
                <p className="app-body-text mt-2 text-cyan-50/90">{lastResult.simple_reply}</p>
              </div>
            </div>
          </Card>
        )}

        <Card className="border-dashed border-amber-400/25">
          <div className="app-label text-amber-200/90">Limite do canal</div>
          <p className="app-body-text mt-2">
            Esta tela apenas submete um trecho à análise local. O canal Evolution recebe mensagens em silêncio e, quando todos os gates permitem, envia somente o alerta ao contato de confiança.
          </p>
        </Card>
      </div>
    </div>
  )
}
