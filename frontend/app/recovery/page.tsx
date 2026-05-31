"use client"

import React, {useState} from 'react'
import Link from 'next/link'
import {postRecovery} from '@/lib/api'
import Card from '@/components/Card'
import Button from '@/components/Button'
import RecoveryPlan from '@/components/RecoveryPlan'
import PrivacyConsentChecklist from '@/components/PrivacyConsentChecklist'
import {recoveryPrivacyNotice} from '@/lib/privacyConsent'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'
import type {RecoveryPayload, RecoveryResponse} from '@/lib/types'

const initialState: RecoveryPayload = {
  paid:false,
  clicked_link:false,
  shared_documents:false,
  shared_password:false,
  installed_app:false,
  shared_sms_code:false,
}

const options: {key:keyof RecoveryPayload,label:string,description:string}[] = [
  {key:'paid', label:'Fiz Pix ou transferência', description:'Houve pagamento para contato suspeito — registre apenas na demo.'},
  {key:'clicked_link', label:'Cliquei em um link', description:'Abri página enviada por mensagem, SMS ou e-mail.'},
  {key:'shared_documents', label:'Enviei documento', description:'Marque se houve envio — não cole documentos reais aqui.'},
  {key:'shared_password', label:'Passei senha', description:'Indique o tipo de ocorrência; não digite senhas reais.'},
  {key:'installed_app', label:'Instalei aplicativo', description:'App ou suporte remoto indicado pelo golpista.'},
  {key:'shared_sms_code', label:'Enviei código SMS', description:'Código repassado — acione banco e canais oficiais na vida real.'},
]

export default function Recovery(){
  const [state,setState]=useState<RecoveryPayload>(initialState)
  const [result,setResult]=useState<RecoveryResponse | null>(null)
  const [loading,setLoading]=useState(false)

  async function onSubmit(){
    setLoading(true)
    const res = await postRecovery(state)
    setResult(res)
    setLoading(false)
  }

  return (
    <PageShell maxWidth="6xl">
      <PageHeader
        eyebrow="Após o incidente"
        title="Recovery — orientação organizada"
        description="Plano educativo por prioridade quando algo já aconteceu. Não substitui banco, polícia, advogado ou canal oficial."
        detail={recoveryPrivacyNotice}
        actions={
          <Link href="/trust-center">
            <Button variant="ghost" className="h-12 w-full sm:w-auto">Trust Center</Button>
          </Link>
        }
        aside={
          <StatusRail
            items={[
              {label:'Substitui banco', value:'não', tone:'ready'},
              {label:'Dados reais', value:'não enviar', tone:'warn'},
              {label:'Decisão', value:'humana', tone:'neutral'},
            ]}
          />
        }
      />

      <PrivacyConsentChecklist compact />

      <Card className="overflow-hidden p-0">
        <div className="border-b border-white/10 px-5 py-4 sm:px-6">
          <div className="app-label">Checklist de ocorrência (demo)</div>
          <h2 className="mt-2 text-xl font-bold tracking-tight text-white">O que aconteceu?</h2>
        </div>

        <div className="space-y-5 p-5 sm:p-6">
          <div className="grid gap-3 md:grid-cols-2">
            {options.map((option)=> (
              <label
                key={option.key}
                className={`cursor-pointer rounded-md border p-4 transition ${
                  state[option.key]
                    ? 'border-cyan-400/40 bg-cyan-950/30'
                    : 'border-white/10 bg-slate-950/30 hover:border-white/20'
                }`}
              >
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={state[option.key]}
                    onChange={e=>setState({...state, [option.key]: e.target.checked})}
                    className="mt-1 h-5 w-5 cursor-pointer"
                  />
                  <div>
                    <div className="text-sm font-semibold text-white">{option.label}</div>
                    <p className="mt-1 text-sm leading-5 text-slate-400">{option.description}</p>
                  </div>
                </div>
              </label>
            ))}
          </div>

          <Button onClick={onSubmit} disabled={loading} className="h-14 w-full text-base">
            {loading ? 'Gerando plano...' : 'Gerar plano de recuperação (demo)'}
          </Button>
        </div>
      </Card>

      <Card className="border-amber-400/20 bg-amber-950/15">
        <div className="app-label text-amber-200/90">Limites do MVP</div>
        <p className="app-body-text mt-2 text-sm">
          Esta tela não registra denúncia automática nem bloqueia contas. Em caso real, preserve evidências e procure o
          banco, a polícia (ex.: DEIC) ou suporte oficial. Não compartilhe senhas, códigos ou documentos neste formulário.
        </p>
      </Card>

      {result && <RecoveryPlan result={result} />}
    </PageShell>
  )
}
