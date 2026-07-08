"use client"

import React from 'react'
import Link from 'next/link'
import HeroSection from '@/components/HeroSection'
import TerminalLogPanel from '@/components/TerminalLogPanel'
import DecisionPreview from '@/components/DecisionPreview'
import {RevealGroup, RevealItem} from '@/components/Reveal'
import {Locale, useGuardianLocale} from '@/lib/i18n'
import {Inbox, Filter, ShieldAlert, Fingerprint, Workflow, Send, CheckCircle} from 'lucide-react'

const PIPELINE_ICONS = [Inbox, Filter, ShieldAlert, Fingerprint, Workflow, Send, CheckCircle]

const homeCopy:Record<Locale, {
  terminalEyebrow:string
  terminalTitle:string
  terminalNote:string
  pipelineEyebrow:string
  pipelineTitle:string
  pipelineSteps:string[]
  closingEyebrow:string
  closingTitle:string
  closingBody:string
  closingPrimary:string
  closingSecondary:string
  statusNote:string
}> = {
  'pt-BR': {
    terminalEyebrow:'AUDIT TRAIL',
    terminalTitle:'Atividade do sistema em demonstração',
    terminalNote:'Dados demonstrativos — ambiente local',
    pipelineEyebrow:'RISK ENGINE',
    pipelineTitle:'Fluxo operacional rastreável',
    pipelineSteps:[
      'Evento recebido',
      'Normalização',
      'Classificação',
      'Idempotência',
      'n8n',
      'WhatsApp via Evolution',
      'Auditoria',
    ],
    closingEyebrow:'TRUST LAYER',
    closingTitle:'Uma camada entre a mensagem suspeita e o prejuízo.',
    closingBody:'O CyberAlerta Guardian foi desenhado para apoiar pessoas vulneráveis, famílias e instituições antes que a engenharia social vire perda financeira.',
    closingPrimary:'Entrar no painel',
    closingSecondary:'Ver fluxo de risco',
    statusNote:'Beta Técnico Local · n8n validado localmente · WhatsApp real via Evolution (não-oficial)',
  },
  'en-US': {
    terminalEyebrow:'AUDIT TRAIL',
    terminalTitle:'System activity demonstration',
    terminalNote:'Demonstrative data — local environment',
    pipelineEyebrow:'RISK ENGINE',
    pipelineTitle:'Traceable operational flow',
    pipelineSteps:[
      'Event received',
      'Normalization',
      'Classification',
      'Idempotency',
      'n8n',
      'WhatsApp via Evolution',
      'Audit',
    ],
    closingEyebrow:'TRUST LAYER',
    closingTitle:'A layer between the suspicious message and the loss.',
    closingBody:'CyberAlerta Guardian was designed to support vulnerable people, families, and institutions before social engineering becomes financial loss.',
    closingPrimary:'Sign in to panel',
    closingSecondary:'View risk flow',
    statusNote:'Local Technical Beta · n8n validated locally · real WhatsApp via Evolution (unofficial)',
  },
}

export default function Home(){
  const [locale] = useGuardianLocale()
  const copy = homeCopy[locale]

  return (
    <div className="home-hermes-page">
      <HeroSection />

      {/* Terminal — audit trail */}
      <section id="recursos" className="home-section home-terminal-section">
        <RevealGroup amount={0.28} delayChildren={0.04} staggerChildren={0.09}>
          <RevealItem className="home-section-label">
            <span className="home-label">{copy.terminalEyebrow}</span>
            <h2>{copy.terminalTitle}</h2>
          </RevealItem>
          <RevealItem>
            <TerminalLogPanel />
          </RevealItem>
          <RevealItem className="home-demo-note">{copy.terminalNote}</RevealItem>
        </RevealGroup>
      </section>

      {/* Decision preview — 2 cards + trail */}
      <DecisionPreview />

      {/* Pipeline — operational flow */}
      <section id="empresa" className="home-section home-pipeline-section">
        <RevealGroup amount={0.24} delayChildren={0.04} staggerChildren={0.08}>
          <RevealItem className="home-section-label">
            <span className="home-label">{copy.pipelineEyebrow}</span>
            <h2>{copy.pipelineTitle}</h2>
          </RevealItem>
          <RevealGroup className="home-pipeline" amount={0.28}>
            {copy.pipelineSteps.map((step, i)=> {
              const Icon = PIPELINE_ICONS[i % PIPELINE_ICONS.length]
              return (
                <RevealItem key={step} className="home-pipeline-step">
                  <span className="home-pipeline-icon-wrap">
                    <Icon className="home-pipeline-icon" />
                  </span>
                  <span className="home-pipeline-label">{step}</span>
                </RevealItem>
              )
            })}
          </RevealGroup>
        </RevealGroup>
      </section>

      {/* Closing CTA */}
      <section id="contato" className="home-section home-closing">
        <RevealGroup className="home-final-content" amount={0.24} delayChildren={0.04} staggerChildren={0.08}>
          <RevealItem className="home-section-label">
            <span className="home-label">{copy.closingEyebrow}</span>
          </RevealItem>
          <RevealItem><h2>{copy.closingTitle}</h2></RevealItem>
          <RevealItem><p>{copy.closingBody}</p></RevealItem>
          <RevealItem className="home-closing-actions">
            <Link href="/login" className="home-primary-cta">{copy.closingPrimary}</Link>
            <Link href="/assisted-demo" className="home-secondary-cta">{copy.closingSecondary}</Link>
          </RevealItem>
          <RevealItem className="home-status-note">{copy.statusNote}</RevealItem>
        </RevealGroup>
      </section>
    </div>
  )
}
