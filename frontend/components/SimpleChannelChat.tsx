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
  role: 'protected' | 'guardian' | 'system'
  text: string
}

export default function SimpleChannelChat(){
  const [alias,setAlias]=useState('Dona Lucia')
  const [draft,setDraft]=useState(defaultMessage)
  const [consent,setConsent]=useState(false)
  const [messages,setMessages]=useState<ChatMessage[]>([
    {
      id: 'welcome',
      role: 'system',
      text: 'Conversa simulada — WhatsApp real nao esta conectado neste MVP.',
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
      setError('Digite a mensagem suspeita que voce quer revisar.')
      return
    }

    const userMessage:ChatMessage = {
      id: `user-${Date.now()}`,
      role: 'protected',
      text: draft.trim(),
    }
    setMessages(prev=>[...prev, userMessage])
    setLoading(true)

    const response = await postSimpleChannelSubmit({
      protected_person_alias: alias.trim() || 'Pessoa protegida',
      channel: 'whatsapp_mock',
      content_type: 'text',
      content: draft.trim(),
      consent: true,
    })

    setLoading(false)
    setLastResult(response)

    if(response.__mock){
      setMessages(prev=>[
        ...prev,
        {
          id: `guardian-${Date.now()}`,
          role: 'guardian',
          text: response.simple_reply,
        },
        {
          id: `status-${Date.now()}`,
          role: 'system',
          text: 'Modo demonstracao local: backend indisponivel, resposta simulada.',
        },
      ])
      return
    }

    setMessages(prev=>[
      ...prev,
      {
        id: `guardian-${Date.now()}`,
        role: 'guardian',
        text: response.simple_reply,
      },
      {
        id: `status-${Date.now()}`,
        role: 'system',
        text: response.admin_case_created
          ? `Caso ${response.channel_case_id} enviado ao responsavel no Guardian Console (simulado).`
          : 'Analise concluida sem abertura de caso administrativo.',
      },
    ])
    setDraft('')
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.05fr_0.95fr]">
      <Card className="flex flex-col p-0 overflow-hidden">
        <div className="border-b border-white/10 bg-slate-950/70 px-4 py-3 sm:px-5">
          <div className="flex items-center justify-between gap-3">
            <div>
              <div className="app-label text-emerald-300/90">WhatsApp mock</div>
              <div className="mt-1 text-sm font-semibold text-white">Guardian — canal simples</div>
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
              placeholder="Cole ou digite a mensagem que voce recebeu..."
            />
          </label>
          <label className="mt-3 flex items-start gap-2 text-sm text-slate-300">
            <input
              type="checkbox"
              checked={consent}
              onChange={event=>setConsent(event.target.checked)}
              className="mt-1"
            />
            <span>
              Autorizo o envio voluntario deste trecho para analise defensiva. O Guardian nao monitora conversas privadas.
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
          <p className="app-muted-text mt-3">
            Experiencia pensada para quem precisa de um canal simples — sem console complexo.
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
            <div className="app-label">Resultado da analise</div>
            <div className="mt-3 grid gap-2 text-sm">
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">Caso</span>
                <span className="font-mono text-xs text-slate-200">{lastResult.channel_case_id}</span>
              </div>
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">Risco</span>
                <span className="font-semibold capitalize text-white">{lastResult.risk_level}</span>
              </div>
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">Caso ao responsavel</span>
                <span className="text-slate-200">{lastResult.admin_case_created ? 'Sim' : 'Nao'}</span>
              </div>
              <div className="flex justify-between gap-3">
                <span className="text-slate-400">Trust Lock</span>
                <span className="text-slate-200">{lastResult.trust_lock_recommended ? 'Recomendado' : 'Nao necessario'}</span>
              </div>
            </div>
            {lastResult.__mock && (
              <p className="app-muted-text mt-3 text-xs">Resposta gerada localmente (fallback).</p>
            )}
          </Card>
        )}

        <Card className="border-dashed border-amber-400/25">
          <div className="app-label text-amber-200/90">Integracao futura</div>
          <p className="app-body-text mt-2">
            WhatsApp Business real, tokens e webhooks ficam fora deste MVP. Esta tela demonstra apenas o fluxo voluntario
            de encaminhamento e a resposta curta antes do dano.
          </p>
        </Card>
      </div>
    </div>
  )
}
