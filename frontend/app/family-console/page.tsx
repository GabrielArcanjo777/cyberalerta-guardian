"use client"

import React, {useEffect, useState} from 'react'
import FamilyConsole from '@/components/FamilyConsole'
import Card from '@/components/Card'
import {PageHeader, PageShell} from '@/components/CommandCenter'
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
    <PageShell maxWidth="6xl">
      <PageHeader
        eyebrow="Console do responsável"
        title="Console da família"
        description="Ação rápida para o contato de confiança. Esta tela transforma o alerta do Guardian em uma resposta simples para o familiar agir no momento certo — com foco em Pix, WhatsApp e pessoas vulneráveis."
        detail="Simulação: nenhuma mensagem real é enviada e nenhum telefone é coletado."
      />

      <FamilyConsole alert={alert} backHref="/before-pix" backLabel="Voltar para análise" />

      <Card className="border-dashed border-white/15">
        <div className="app-label">Nota de segurança do MVP</div>
        <p className="app-body-text mt-2">
          Este console não envia mensagens reais e não coleta telefone. Ele mostra como o contato de confiança deve agir a partir da análise defensiva do CyberAlerta Guardian.
        </p>
      </Card>
    </PageShell>
  )
}
