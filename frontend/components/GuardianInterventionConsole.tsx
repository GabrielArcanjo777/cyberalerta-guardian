import React from 'react'
import {
  ActionPanel,
  DecisionPanel,
  EvidencePanel,
  OperationalTimeline,
  StatusRail,
} from '@/components/CommandCenter'

const signals = [
  'número novo',
  'urgência',
  'pedido de Pix',
  'isolamento da vítima',
  'pedido para não ligar',
]

const timeline = [
  {title:'Entrada voluntária', body:'Mensagem suspeita colada pela pessoa ou responsável.'},
  {title:'Classificação defensiva', body:'Sinais de manipulação e ação financeira são separados.'},
  {title:'Pausa protetiva', body:'Trust Lock interrompe a decisão antes da transferência.'},
  {title:'Verificação segura', body:'Contato salvo deve ser usado antes de qualquer pagamento.'},
  {title:'Evidência registrada', body:'A decisão fica rastreável para família e avaliação.'},
]

export default function GuardianInterventionConsole(){
  return (
    <div className="guardian-intervention-console">
      <div className="guardian-console-topline">
        <div>
          <div className="guardian-panel-eyebrow">Console de intervenção Guardian</div>
          <h2 className="mt-2 text-2xl font-semibold text-white">Decisão rastreável antes do dano</h2>
        </div>
        <div className="guardian-console-lock">TRUST LOCK</div>
      </div>

      <div className="grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
        <DecisionPanel eyebrow="Mensagem recebida" className="p-0">
          <div className="guardian-received-message">
            <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold uppercase text-slate-500">
              <span>Origem não verificada</span>
              <span>WhatsApp simulado</span>
            </div>
            <p className="text-base font-semibold leading-7 text-slate-100">
              "Mãe, troquei de número. Preciso fazer um Pix urgente. Não liga agora."
            </p>
          </div>

          <StatusRail
            className="mt-4"
            items={[
              {label:'Risco', value:'alto - 87/100', tone:'risk'},
              {label:'Pausa', value:'protetiva ativada', tone:'warn'},
              {label:'Contato seguro', value:'Gabriel', tone:'ready'},
            ]}
          />
        </DecisionPanel>

        <ActionPanel eyebrow="Próxima ação segura" title="Confirmar antes de transferir">
          <p className="text-base font-semibold leading-7 text-slate-200">
            Confirmar com Gabriel pelo contato salvo antes de qualquer transferência.
          </p>
          <div className="mt-5 grid gap-3 sm:grid-cols-2">
            <div className="guardian-console-mini-card">
              <div className="text-xs font-semibold uppercase text-slate-500">Trust Lock</div>
              <div className="mt-2 text-sm font-semibold text-white">Pausa protetiva ativada</div>
            </div>
            <div className="guardian-console-mini-card">
              <div className="text-xs font-semibold uppercase text-slate-500">Guardian</div>
              <div className="mt-2 text-sm font-semibold text-white">Contato seguro: Gabriel</div>
            </div>
          </div>
        </ActionPanel>
      </div>

      <div className="grid gap-4 lg:grid-cols-[0.82fr_1.18fr]">
        <EvidencePanel eyebrow="Sinais detectados" title="Evidências defensivas">
          <div className="guardian-evidence-grid">
            {signals.map((signal)=> (
              <span key={signal} className="guardian-evidence-chip">{signal}</span>
            ))}
          </div>
        </EvidencePanel>

        <DecisionPanel eyebrow="Trace resumido" title="Linha de decisão dos agentes">
          <OperationalTimeline items={timeline} />
        </DecisionPanel>
      </div>
    </div>
  )
}
