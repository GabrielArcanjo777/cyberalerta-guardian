"use client"

import React from 'react'
import {
  ActionPanel,
  DecisionPanel,
  EvidencePanel,
  OperationalTimeline,
  StatusRail,
} from '@/components/CommandCenter'
import {MotionCard, RevealGroup, RevealItem} from '@/components/Reveal'
import {type Locale, useGuardianLocale} from '@/lib/i18n'

const consoleCopy = {
  'pt-BR': {
    eyebrow:'Console de intervenção Guardian',
    title:'Decisão rastreável antes do dano',
    lock:'TRUST LOCK',
    statusLabel:'Status operacional do caso',
    statusCards:[
      {label:'STATUS', value:'Monitorando'},
      {label:'RISCO DETECTADO', value:'Alto'},
      {label:'AÇÃO SUGERIDA', value:'Pausar resposta'},
      {label:'CONTATO CONFIÁVEL', value:'Acionar Gabriel'},
    ],
    messageEyebrow:'Mensagem recebida',
    messageOrigin:'Origem não verificada',
    messageChannel:'WhatsApp simulado',
    message:'"Mãe, troquei de número. Preciso fazer um Pix urgente. Não liga agora."',
    statusRail:[
      {label:'Risco', value:'alto - 87/100', tone:'risk'},
      {label:'Pausa', value:'protetiva ativada', tone:'warn'},
      {label:'Contato seguro', value:'Gabriel', tone:'ready'},
    ],
    actionEyebrow:'Próxima ação segura',
    actionTitle:'Confirmar antes de transferir',
    actionBody:'Confirmar com Gabriel pelo contato salvo antes de qualquer transferência.',
    trustLockStatus:'Pausa protetiva ativada',
    guardianStatus:'Contato seguro: Gabriel',
    signalsEyebrow:'Sinais detectados',
    signalsTitle:'Evidências defensivas',
    signals:['número novo', 'urgência', 'pedido de Pix', 'isolamento da vítima', 'pedido para não ligar'],
    timelineEyebrow:'Trace resumido',
    timelineTitle:'Linha de decisão dos agentes',
    timeline:[
      {title:'Entrada voluntária', body:'Mensagem suspeita colada pela pessoa ou responsável.'},
      {title:'Classificação defensiva', body:'Sinais de manipulação e ação financeira são separados.'},
      {title:'Pausa protetiva', body:'Trust Lock interrompe a decisão antes da transferência.'},
      {title:'Verificação segura', body:'Contato salvo deve ser usado antes de qualquer pagamento.'},
      {title:'Evidência registrada', body:'A decisão fica rastreável para família e avaliação.'},
    ],
  },
  'en-US': {
    eyebrow:'Guardian intervention console',
    title:'A traceable decision before harm',
    lock:'TRUST LOCK',
    statusLabel:'Case operational status',
    statusCards:[
      {label:'STATUS', value:'Monitoring'},
      {label:'RISK DETECTED', value:'High'},
      {label:'SUGGESTED ACTION', value:'Pause response'},
      {label:'TRUSTED CONTACT', value:'Alert Gabriel'},
    ],
    messageEyebrow:'Received message',
    messageOrigin:'Unverified source',
    messageChannel:'Simulated WhatsApp',
    message:'"Mom, I changed my number. I need to make an urgent Pix transfer. Do not call now."',
    statusRail:[
      {label:'Risk', value:'high - 87/100', tone:'risk'},
      {label:'Pause', value:'protective pause active', tone:'warn'},
      {label:'Safe contact', value:'Gabriel', tone:'ready'},
    ],
    actionEyebrow:'Next safe action',
    actionTitle:'Confirm before transferring',
    actionBody:'Confirm with Gabriel through the saved contact before any transfer.',
    trustLockStatus:'Protective pause active',
    guardianStatus:'Safe contact: Gabriel',
    signalsEyebrow:'Detected signals',
    signalsTitle:'Defensive evidence',
    signals:['new number', 'urgency', 'Pix request', 'victim isolation', 'request not to call'],
    timelineEyebrow:'Decision summary',
    timelineTitle:'Agent decision timeline',
    timeline:[
      {title:'Voluntary intake', body:'Suspicious message submitted by the person or responsible contact.'},
      {title:'Defensive classification', body:'Manipulation signals and the financial action are separated.'},
      {title:'Protective pause', body:'Trust Lock interrupts the decision before the transfer.'},
      {title:'Safe verification', body:'A saved contact must be used before any payment.'},
      {title:'Evidence recorded', body:'The decision remains traceable for the family and evaluation.'},
    ],
  },
} satisfies Record<Locale, {
  eyebrow:string
  title:string
  lock:string
  statusLabel:string
  statusCards:Array<{label:string; value:string}>
  messageEyebrow:string
  messageOrigin:string
  messageChannel:string
  message:string
  statusRail:Array<{label:string; value:string; tone:'risk' | 'warn' | 'ready'}>
  actionEyebrow:string
  actionTitle:string
  actionBody:string
  trustLockStatus:string
  guardianStatus:string
  signalsEyebrow:string
  signalsTitle:string
  signals:string[]
  timelineEyebrow:string
  timelineTitle:string
  timeline:Array<{title:string; body:string}>
}>

export default function GuardianInterventionConsole(){
  const [locale] = useGuardianLocale()
  const copy = consoleCopy[locale]

  return (
    <RevealGroup className="guardian-intervention-console" amount={0.24} delayChildren={0.08} staggerChildren={0.07}>
      <RevealItem className="guardian-console-topline">
        <div>
          <div className="guardian-panel-eyebrow">{copy.eyebrow}</div>
          <h2 className="mt-2 text-2xl font-semibold text-white">{copy.title}</h2>
        </div>
        <div className="guardian-console-lock status-pill status-locked"><span className="status-dot" />{copy.lock}</div>
      </RevealItem>

      <RevealGroup className="guardian-console-product-status" aria-label={copy.statusLabel} amount={0.22} delayChildren={0.08} staggerChildren={0.06}>
        <MotionCard className="status-card status-safe">
          <span>{copy.statusCards[0].label}</span>
          <strong>{copy.statusCards[0].value}</strong>
        </MotionCard>
        <MotionCard className="status-card status-danger">
          <span>{copy.statusCards[1].label}</span>
          <strong>{copy.statusCards[1].value}</strong>
        </MotionCard>
        <MotionCard className="status-card status-warning">
          <span>{copy.statusCards[2].label}</span>
          <strong>{copy.statusCards[2].value}</strong>
        </MotionCard>
        <MotionCard className="status-card status-locked">
          <span>{copy.statusCards[3].label}</span>
          <strong>{copy.statusCards[3].value}</strong>
        </MotionCard>
      </RevealGroup>

      <RevealGroup className="grid gap-5 lg:grid-cols-[1.05fr_0.95fr]" amount={0.24} delayChildren={0.08} staggerChildren={0.08}>
        <RevealItem>
          <DecisionPanel eyebrow={copy.messageEyebrow} className="p-0">
            <div className="guardian-received-message">
              <div className="mb-3 flex flex-wrap items-center justify-between gap-2 text-xs font-semibold uppercase text-slate-500">
                <span>{copy.messageOrigin}</span>
                <span>{copy.messageChannel}</span>
              </div>
              <p className="text-base font-semibold leading-7 text-slate-100">
                {copy.message}
              </p>
            </div>

            <StatusRail className="mt-4" items={copy.statusRail} />
          </DecisionPanel>
        </RevealItem>

        <RevealItem>
          <ActionPanel eyebrow={copy.actionEyebrow} title={copy.actionTitle}>
            <p className="guardian-next-action-copy">
              {copy.actionBody}
            </p>
            <RevealGroup className="mt-5 grid gap-3 sm:grid-cols-2" amount={0.2} delayChildren={0.08} staggerChildren={0.06}>
              <MotionCard className="guardian-console-mini-card status-card status-locked">
                <div className="text-xs font-semibold uppercase text-slate-500">Trust Lock</div>
                <div className="mt-2 text-sm font-semibold text-white">{copy.trustLockStatus}</div>
              </MotionCard>
              <MotionCard className="guardian-console-mini-card status-card status-safe">
                <div className="text-xs font-semibold uppercase text-slate-500">Guardian</div>
                <div className="mt-2 text-sm font-semibold text-white">{copy.guardianStatus}</div>
              </MotionCard>
            </RevealGroup>
          </ActionPanel>
        </RevealItem>
      </RevealGroup>

      <RevealGroup className="grid gap-5 lg:grid-cols-[0.82fr_1.18fr]" amount={0.24} delayChildren={0.08} staggerChildren={0.08}>
        <RevealItem>
          <EvidencePanel eyebrow={copy.signalsEyebrow} title={copy.signalsTitle}>
            <RevealGroup className="guardian-evidence-grid" amount={0.2} delayChildren={0.08} staggerChildren={0.05}>
              {copy.signals.map((signal)=> (
                <RevealItem key={signal}>
                  <span className="guardian-evidence-chip status-pill status-warning"><span className="status-dot" />{signal}</span>
                </RevealItem>
              ))}
            </RevealGroup>
          </EvidencePanel>
        </RevealItem>

        <RevealItem>
          <DecisionPanel eyebrow={copy.timelineEyebrow} title={copy.timelineTitle}>
            <OperationalTimeline items={copy.timeline} />
          </DecisionPanel>
        </RevealItem>
      </RevealGroup>
    </RevealGroup>
  )
}
