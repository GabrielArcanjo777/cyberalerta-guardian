"use client"

import React, {useEffect, useState} from 'react'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppStatus} from '@/components/AppPrimitives'
import {getSimpleChannelStatus, postSimpleChannelSubmit} from '@/lib/api'
import type {SimpleChannelStatusResponse, SimpleChannelSubmitResponse} from '@/lib/types'

const defaultMessage = 'Mae, troquei de numero. Preciso fazer um Pix urgente.'

type ChatMessage = {
  id: string
  role: 'protected' | 'guardian' | 'system' | 'typing'
  text: string
}

export default function SimpleChannelChat(){
  const [alias,setAlias]=useState('Dona Lucia')
  const [trustedContact,setTrustedContact]=useState('Gabriel')
  const [draft,setDraft]=useState(defaultMessage)
  const [consent,setConsent]=useState(false)
  const [messages,setMessages]=useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'system',
      text: 'Conversa simulada — WhatsApp real não está conectado neste MVP.',
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
    const userMessage:ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'protected',
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
      const next:ChatMessage[] = [
        ...withoutTyping,
        {
          id: `guardian-${Date.now()}`,
          role: 'guardian',
          text: response.simple_reply,
        },
      ]
      if(response.admin_case_created){
        next.push({
          id: `status-${Date.now()}`,
          role: 'system',
          text: response.__mock
            ? `Caso simulado enviado ao responsável (${trustedContact || 'contato de confiança'}). Modo demonstração local.`
            : `Caso ${response.channel_case_id} enviado ao responsável. ${trustedContact || 'Seu contato de confiança'} pode acompanhar no console.`,
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
          text: 'Resposta gerada em modo demonstração (backend indisponível).',
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
              <div className="app-label text-emerald-300/90">WhatsApp mock</div>
              <div className="mt-1 text-sm font-semibold text-white">Canal simples · só para você</div>
            </div>
            <AppStatus status="mock" />
          </div>
        </div>

        <div className="flex min-h-[320px] flex-1 flex-col gap-3 overflow-y-auto p-4 sm:p-5">
          {messages.map(message=> (
            <div
              key={message.id}
              className={
                message.role === 'protected'
                  ? 'ml-auto max-w-[88%] rounded-md border border-emerald-400/25 bg-emerald-950/35 px-3 py-2.5 text-sm leading-6 text-emerald-50'
                  : message.role === 'guardian'
                    ? 'mr-auto max-w-[88%] rounded-md border border-cyan-400/25 bg-cyan-950/30 px-3 py-2.5 text-sm leading-6 text-cyan-50'
                    : message.role === 'typing'
                      ? 'mr-auto max-w-[88%] rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-sm italic text-slate-400'
                      : 'mx-auto max-w-[95%] rounded-md border border-white/10 bg-white/[0.04] px-3 py-2 text-center text-xs leading-5 text-slate-400'
              }
            >
              {message.role === 'protected' && (
                <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-emerald-300/80">
                  {alias}
                </div>
              )}
              {message.role === 'guardian' && (
                <div className="mb-1 text-[10px] font-semibold uppercase tracking-wide text-cyan-300/80">
                  Guardian
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
            Experiência simples: você envia, o Guardian responde com calma e avisa o responsável se houver risco.
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
            </div>
          </Card>
        )}

        <Card className="border-dashed border-amber-400/25">
          <div className="app-label text-amber-200/90">Integração futura</div>
          <p className="app-body-text mt-2">
            WhatsApp Business real e envio automático ficam fora deste MVP. Nada aqui conversa com golpista nem envia mensagem real.
          </p>
        </Card>
      </div>
    </div>
  )
}
