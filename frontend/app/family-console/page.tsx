"use client"

import React, {useEffect, useState} from 'react'
import FamilyConsole from '@/components/FamilyConsole'
import Card from '@/components/Card'
import {mockAnalyzeResult} from '@/lib/mockData'
import type {TrustedCircleAlert} from '@/lib/types'

const storageKey = 'cyberalerta:lastTrustedCircleAlert'

export default function FamilyConsolePage(){
  const [alert,setAlert]=useState<TrustedCircleAlert>(mockAnalyzeResult.trusted_circle_alert)

  useEffect(()=>{
    try{
      const raw = window.localStorage.getItem(storageKey)
      if(raw){
        setAlert(JSON.parse(raw))
      }
    }catch{
      setAlert(mockAnalyzeResult.trusted_circle_alert)
    }
  },[])

  return (
    <section className="mx-auto max-w-6xl space-y-6 pb-12">
      <div className="rounded-lg border border-slate-200 bg-white p-6 shadow-[0_14px_36px_rgba(15,23,42,0.07)] sm:p-8">
        <div className="max-w-3xl">
          <div className="inline-flex rounded border border-slate-200 bg-slate-50 px-3 py-1 text-xs font-bold uppercase tracking-[0.18em] text-slate-600">
            Sprint 5
          </div>
          <h1 className="mt-5 text-4xl font-black tracking-tight text-slate-950 sm:text-5xl">Family Console</h1>
          <p className="mt-4 text-base leading-7 text-slate-600">
            Acao rapida para contato de confianca. Esta tela transforma o alerta do Guardian em uma resposta simples para o familiar agir no momento certo.
          </p>
        </div>
      </div>

      <FamilyConsole alert={alert} backHref="/before-pix" backLabel="Voltar para analise" />

      <Card className="border-dashed border-slate-300 bg-slate-50/70">
        <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">MVP safety note</div>
        <p className="mt-2 text-sm leading-6 text-slate-700">
          Este console nao envia mensagens reais e nao coleta telefone. Ele mostra como o contato de confianca deve agir a partir da analise defensiva do CyberAlerta Guardian.
        </p>
      </Card>
    </section>
  )
}
