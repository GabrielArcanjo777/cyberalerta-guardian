import React from 'react'
import {
  ActionPanel,
  DecisionPanel,
  EvidencePanel,
  StatusRail,
} from '@/components/CommandCenter'
import {RevealGroup, RevealItem} from '@/components/Reveal'

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
    <RevealGroup as="div" className="guardian-intervention-console" variant="panel" amount={0.24} delayChildren={0.08} stagger={0.07}>
      <RevealItem className="guardian-console-topline" index={0}>
        <div>
          <div className="guardian-panel-eyebrow">Console de intervenção Guardian</div>
          <h2 className="mt-2 text-2xl font-semibold text-white">Decisão rastreável antes do dano</h2>
        </div>
        <div className="guardian-console-lock">TRUST LOCK</div>
      </RevealItem>

      <div className="guardian-console-grid grid gap-4 lg:grid-cols-[1.05fr_0.95fr]">
        <RevealItem className="guardian-console-layer" index={1}>
          <DecisionPanel eyebrow="Mensagem recebida" className="p-0 guardian-console-message-panel">
            <RevealItem className="guardian-received-message" index={2}>
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold uppercase text-slate-500">
                <span>Origem não verificada</span>
                <span>WhatsApp simulado</span>
              </div>
              <p className="text-base font-semibold leading-7 text-slate-100">
                &ldquo;Mãe, troquei de número. Preciso fazer um Pix urgente. Não liga agora.&rdquo;
              </p>
            </RevealItem>

            <RevealItem index={3}>
              <StatusRail
                className="mt-4"
                items={[
                  {label:'Risco', value:'alto - 87/100', tone:'risk'},
                  {label:'Pausa', value:'protetiva ativada', tone:'warn'},
                  {label:'Contato seguro', value:'Gabriel', tone:'ready'},
                ]}
              />
            </RevealItem>
          </DecisionPanel>
        </RevealItem>

        <RevealItem className="guardian-console-layer" index={4}>
          <ActionPanel eyebrow="Próxima ação segura" title="Confirmar antes de transferir">
            <RevealItem index={5}>
              <p className="text-base font-semibold leading-7 text-slate-200">
                Confirmar com Gabriel pelo contato salvo antes de qualquer transferência.
              </p>
            </RevealItem>
            <div className="mt-5 grid gap-3 sm:grid-cols-2">
              <RevealItem className="guardian-console-mini-card guardian-console-lock-card" index={6}>
                <div className="text-xs font-semibold uppercase text-slate-500">Trust Lock</div>
                <div className="mt-2 text-sm font-semibold text-white">Pausa protetiva ativada</div>
              </RevealItem>
              <RevealItem className="guardian-console-mini-card guardian-console-contact-card" index={7}>
                <div className="text-xs font-semibold uppercase text-slate-500">Guardian</div>
                <div className="mt-2 text-sm font-semibold text-white">Contato seguro: Gabriel</div>
              </RevealItem>
            </div>
          </ActionPanel>
        </RevealItem>
      </div>

      <div className="guardian-console-grid grid gap-4 lg:grid-cols-[0.82fr_1.18fr]">
        <RevealItem className="guardian-console-layer" index={8}>
          <EvidencePanel eyebrow="Sinais detectados" title="Evidências defensivas">
            <div className="guardian-evidence-grid">
              {signals.map((signal,index)=> (
                <RevealItem as="span" key={signal} className="guardian-evidence-chip" index={index + 9}>
                  {signal}
                </RevealItem>
              ))}
            </div>
          </EvidencePanel>
        </RevealItem>

        <RevealItem className="guardian-console-layer" index={14}>
          <DecisionPanel eyebrow="Trace resumido" title="Linha de decisão dos agentes">
            <ol className="guardian-operational-timeline">
              {timeline.map((item,index)=> (
                <RevealItem as="li" key={`${item.title}-${index}`} className="guardian-timeline-item" index={index + 15}>
                  <span className="guardian-timeline-index">{String(index + 1).padStart(2,'0')}</span>
                  <div>
                    <div className="text-sm font-semibold text-white">{item.title}</div>
                    <p className="mt-1 text-sm leading-6 text-slate-400">{item.body}</p>
                  </div>
                </RevealItem>
              ))}
            </ol>
          </DecisionPanel>
        </RevealItem>
      </div>
    </RevealGroup>
  )
}
