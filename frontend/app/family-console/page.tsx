"use client"

import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import GuardianAdminConsole from '@/components/GuardianAdminConsole'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

export default function FamilyConsolePage(){
  return (
    <PageShell maxWidth="7xl">
      <PageHeader
        eyebrow="Painel do responsável"
        title="Guardian Console"
        description="Central operacional para familiar, cuidador ou instituição acompanhar casos recebidos da pessoa protegida — com risco, trilha da decisão e ações seguras."
        detail="Fluxo: pessoa protegida encaminha pelo canal simples → Guardian analisa → caso entra na fila → responsável age com pausa protetiva."
        actions={
          <Link href="/chatbot-demo">
            <Button variant="ghost" className="h-12 w-full sm:w-auto">Ver canal da pessoa protegida</Button>
          </Link>
        }
        aside={
          <StatusRail
            items={[
              {label:'Operador', value:'responsável', tone:'ready'},
              {label:'Armazenamento', value:'demo in-memory', tone:'neutral'},
              {label:'Envio real', value:'desligado', tone:'warn'},
            ]}
          />
        }
      />

      <GuardianAdminConsole />
    </PageShell>
  )
}
