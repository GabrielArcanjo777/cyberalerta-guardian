"use client"

import React, {useState} from 'react'
import {postRecovery} from '@/lib/api'
import Card from '@/components/Card'
import Button from '@/components/Button'
import RecoveryPlan from '@/components/RecoveryPlan'
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
  {key:'paid', label:'Fiz Pix ou transferencia', description:'Houve pagamento, Pix ou transferencia para o contato suspeito.'},
  {key:'clicked_link', label:'Cliquei em um link', description:'Abri uma pagina enviada por mensagem, SMS, e-mail ou rede social.'},
  {key:'shared_documents', label:'Enviei documento', description:'Foto, PDF, numero de documento ou dados pessoais foram enviados.'},
  {key:'shared_password', label:'Passei senha', description:'Senha, login ou resposta de seguranca foram compartilhados.'},
  {key:'installed_app', label:'Instalei aplicativo', description:'Instalei app, suporte remoto ou arquivo indicado pelo contato.'},
  {key:'shared_sms_code', label:'Enviei codigo SMS', description:'Codigo de verificacao ou token foi repassado para outra pessoa.'},
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
    <section className="guardian-product-page mx-auto max-w-6xl space-y-6 pb-12">
      <div className="guardian-page-header p-6 sm:p-8">
        <div className="max-w-3xl">
          <div className="guardian-kicker">
            Sprint 6
          </div>
          <h1 className="mt-5 text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">Ja cai em um golpe</h1>
          <p className="mt-4 text-base leading-7 text-slate-600">
            Marque o que aconteceu para gerar um plano de recuperacao preventivo, claro e organizado por prioridade.
          </p>
        </div>
      </div>

      <Card className="overflow-hidden p-0">
        <div className="border-b border-slate-200 px-5 py-4 sm:px-6">
          <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Recovery checklist</div>
          <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">O que aconteceu?</h2>
        </div>

        <div className="space-y-5 p-5 sm:p-6">
          <div className="grid gap-3 md:grid-cols-2">
            {options.map((option)=> (
              <label
                key={option.key}
                className={`cursor-pointer rounded-lg border p-4 transition ${
                  state[option.key]
                    ? 'border-slate-950 bg-slate-950 text-white shadow-[0_12px_28px_rgba(15,23,42,0.14)]'
                    : 'border-slate-200 bg-white hover:border-slate-300 hover:bg-slate-50'
                }`}
              >
                <div className="flex items-start gap-3">
                  <input
                    type="checkbox"
                    checked={state[option.key]}
                    onChange={e=>setState({...state, [option.key]: e.target.checked})}
                    className="mt-1 h-5 w-5 cursor-pointer rounded border-slate-300"
                  />
                  <div>
                    <div className={`text-sm font-black ${state[option.key] ? 'text-white' : 'text-slate-950'}`}>{option.label}</div>
                    <p className={`mt-1 text-sm leading-5 ${state[option.key] ? 'text-slate-300' : 'text-slate-500'}`}>{option.description}</p>
                  </div>
                </div>
              </label>
            ))}
          </div>

          <Button onClick={onSubmit} disabled={loading} className="h-14 w-full text-base">
            {loading ? 'Gerando plano...' : 'Gerar plano de recuperacao'}
          </Button>
        </div>
      </Card>

      <Card className="border-amber-200 bg-amber-50">
        <div className="text-xs font-bold uppercase tracking-wide text-amber-700">Responsabilidade</div>
        <p className="mt-2 text-sm font-semibold leading-6 text-slate-800">
          Esta e uma orientacao preventiva e educativa. Nao envie documentos reais aqui e nao compartilhe senhas, codigos ou dados sensiveis.
        </p>
      </Card>

      {result && <RecoveryPlan result={result} />}
    </section>
  )
}
