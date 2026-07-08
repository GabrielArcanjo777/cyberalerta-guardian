"use client"

import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import GuardianAdminConsole from '@/components/GuardianAdminConsole'
import PrivacyConsentChecklist from '@/components/PrivacyConsentChecklist'
import {familyConsolePrivacyNotice} from '@/lib/privacyConsent'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

export default function FamilyConsolePage(){
  return (
    <PageShell maxWidth="7xl">
      <PageHeader
        eyebrow="Painel do responsável"
        title="Guardian Console"
        description="Central para familiar, cuidador ou instituição acompanhar casos compartilhados voluntariamente — com risco, trilha e ações seguras. Não é ferramenta de vigilância."
        detail={familyConsolePrivacyNotice}
        actions={
          <Link href="/chatbot-demo">
            <Button variant="ghost" className="h-12 w-full sm:w-auto">Ver canal da pessoa protegida</Button>
          </Link>
        }
        aside={
          <StatusRail
            items={[
              {label:'Operador', value:'responsável', tone:'ready'},
              {label:'Armazenamento', value:'SQLite (persistente)', tone:'ready'},
              {label:'Canal', value:'Evolution · não-oficial', tone:'neutral'},
            ]}
          />
        }
      />

      <GuardianAdminConsole />

      <PrivacyConsentChecklist compact title="Proteção assistida" />

    </PageShell>
  )
}
