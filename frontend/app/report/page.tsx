import React from 'react'
import {CommandPanel, PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

export default function Report(){
  return (
    <PageShell maxWidth="6xl">
      <PageHeader
        eyebrow="Guardian report"
        title="Relatorio final gerado pelo Guardian"
        description="Resumo defensivo para explicar sinais, decisao, evidencias e proximas acoes sem expor dados sensiveis."
        aside={
          <StatusRail
            items={[
              {label:'Formato', value:'demo', tone:'neutral'},
              {label:'Persistencia', value:'sem banco', tone:'ready'},
              {label:'Uso', value:'educativo', tone:'warn'},
            ]}
          />
        }
      />

      <CommandPanel eyebrow="Report view" title="Placeholder operacional">
        <p className="text-sm font-semibold leading-6 text-slate-300">
          Esta area representa a visao final do relatorio do Guardian. A tela permanece como MVP visual, sem alterar backend, dados ou persistencia.
        </p>
      </CommandPanel>
    </PageShell>
  )
}
