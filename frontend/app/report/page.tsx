import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import PrivacyConsentChecklist from '@/components/PrivacyConsentChecklist'
import {reportPrivacyNotice} from '@/lib/privacyConsent'
import {CommandPanel, PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

export default function Report(){
  return (
    <PageShell maxWidth="6xl">
      <PageHeader
        eyebrow="Documentação assistida"
        title="Relatório do Guardian"
        description="Resumo para família ou instituição explicar sinais, decisão e próximas ações — sem expor dados sensíveis desnecessários."
        detail={reportPrivacyNotice}
        actions={
          <Link href="/trust-center">
            <Button variant="ghost" className="h-12 w-full sm:w-auto">Trust Center</Button>
          </Link>
        }
        aside={
          <StatusRail
            items={[
              {label:'Denúncia auto.', value:'não', tone:'ready'},
              {label:'Autoridade', value:'não substitui', tone:'warn'},
              {label:'MVP', value:'demo', tone:'neutral'},
            ]}
          />
        }
      />

      <PrivacyConsentChecklist compact />

      <CommandPanel eyebrow="Relatório" title="Visão operacional (MVP)">
        <div className="grid gap-4 text-sm leading-6 text-slate-300">
          <p>
            O relatório organiza o que foi encaminhado <strong className="text-slate-100">voluntariamente</strong>,
            os sinais detectados, a pausa protetiva recomendada e as ações do responsável. Serve para registro interno e
            alinhamento — não dispara automaticamente banco, polícia ou órgãos públicos.
          </p>
          <p>
            O usuário ou responsável decide se aciona canais oficiais, recovery ou suporte jurídico. Dados na demo são
            simulados; não use informações reais de terceiros.
          </p>
        </div>
      </CommandPanel>
    </PageShell>
  )
}
