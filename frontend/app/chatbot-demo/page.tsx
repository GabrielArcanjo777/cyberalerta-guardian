import React from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import SimpleChannelChat from '@/components/SimpleChannelChat'
import {PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

export default function ChatbotDemoPage(){
  return (
    <PageShell>
      <PageHeader
        eyebrow="Canal simples · Sprint 18B"
        title="Encaminhar mensagem pelo WhatsApp mock"
        description="A pessoa protegida compartilha apenas o trecho suspeito. O Guardian analisa em silêncio, mostra a orientação nesta tela e abre um caso para revisão quando necessário."
        detail="Nenhuma resposta é enviada ao remetente. Sem tokens, sem monitoramento invisível de conversas privadas e sem envio real nesta simulação."
        actions={
          <>
            <Link href="/family-console">
              <Button className="h-12 w-full sm:w-auto">Ver console do responsável</Button>
            </Link>
            <Link href="/intake">
              <Button variant="ghost" className="h-12 w-full sm:w-auto">Intake técnico completo</Button>
            </Link>
          </>
        }
        aside={
          <StatusRail
            items={[
              {label:'Canal', value:'whatsapp_mock', tone:'ready'},
              {label:'Envio real', value:'desligado', tone:'warn'},
              {label:'Consentimento', value:'obrigatorio', tone:'neutral'},
            ]}
          />
        }
      />

      <SimpleChannelChat />
    </PageShell>
  )
}
