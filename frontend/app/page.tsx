"use client"

import React from 'react'
import Link from 'next/link'
import HeroSection from '@/components/HeroSection'
import TerminalLogPanel from '@/components/TerminalLogPanel'
import DecisionPreview from '@/components/DecisionPreview'
import {RevealGroup, RevealItem} from '@/components/Reveal'
import {Locale, useGuardianLocale} from '@/lib/i18n'
import {
  Inbox, Filter, ShieldAlert, Fingerprint, Workflow, Send, CheckCircle,
  Banknote, Link2, Landmark, Users, KeyRound, AlarmClock,
} from 'lucide-react'

const PIPELINE_ICONS = [Inbox, Filter, ShieldAlert, Fingerprint, Workflow, Send, CheckCircle]
const DETECT_ICONS = [Banknote, Link2, Landmark, Users, KeyRound, AlarmClock]

const homeCopy:Record<Locale, {
  terminalEyebrow:string
  terminalTitle:string
  terminalNote:string
  detectEyebrow:string
  detectTitle:string
  detectItems:string[]
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
    terminalEyebrow:'EM TEMPO REAL',
    terminalTitle:'Veja os alertas suspeitos chegando no painel',
    terminalNote:'Dados de demonstração — ambiente local',
    detectEyebrow:'O QUE DETECTAMOS',
    detectTitle:'Os golpes mais comuns no WhatsApp',
    detectItems:[
      'Golpe do Pix',
      'Link falso',
      'Falso banco',
      'Parente pedindo dinheiro',
      'Código de verificação',
      'Urgência e manipulação',
    ],
    pipelineEyebrow:'COMO FUNCIONA',
    pipelineTitle:'Do WhatsApp ao alerta, em segundos',
    pipelineSteps:[
      'Mensagem recebida',
      'Conversa normal descartada',
      'Risco classificado',
      'Motivo identificado',
      'Só o suspeito é salvo',
      'Alerta enviado',
      'Você decide',
    ],
    closingEyebrow:'PROTEÇÃO CONTÍNUA',
    closingTitle:'Um alerta antes de alguém cair no golpe.',
    closingBody:'O CyberAlerta analisa as mensagens recebidas, ignora as conversas normais e avisa você quando aparece um sinal de golpe — Pix urgente, link falso, falso banco ou pressão emocional. Com privacidade por padrão e uso só com autorização.',
    closingPrimary:'Ver demonstração',
    closingSecondary:'Conectar WhatsApp',
    statusNote:'Demonstração local · WhatsApp via Evolution (não-oficial) · privacidade por padrão',
  },
  'en-US': {
    terminalEyebrow:'REAL TIME',
    terminalTitle:'Watch suspicious alerts arrive on the panel',
    terminalNote:'Demonstration data — local environment',
    detectEyebrow:'WHAT WE DETECT',
    detectTitle:'The most common WhatsApp scams',
    detectItems:[
      'Pix scam',
      'Fake link',
      'Fake bank',
      'Relative asking for money',
      'Verification code',
      'Urgency & manipulation',
    ],
    pipelineEyebrow:'HOW IT WORKS',
    pipelineTitle:'From WhatsApp to alert, in seconds',
    pipelineSteps:[
      'Message received',
      'Normal chat discarded',
      'Risk classified',
      'Reason identified',
      'Only the suspicious is saved',
      'Alert sent',
      'You decide',
    ],
    closingEyebrow:'CONTINUOUS PROTECTION',
    closingTitle:'An alert before someone falls for a scam.',
    closingBody:'CyberAlerta analyzes incoming messages, ignores normal conversations, and warns you when a scam signal appears — urgent Pix, fake link, fake bank or emotional pressure. Privacy by default and authorized use only.',
    closingPrimary:'See demo',
    closingSecondary:'Connect WhatsApp',
    statusNote:'Local demo · WhatsApp via Evolution (unofficial) · privacy by default',
  },
}

export default function Home(){
  const [locale] = useGuardianLocale()
  const copy = homeCopy[locale]

  return (
    <div className="home-hermes-page">
      <HeroSection />

      {/* Terminal — alertas em tempo real */}
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

      {/* Decisão — 2 cards + trilha */}
      <DecisionPreview />

      {/* O que detectamos */}
      <section id="solucoes" className="home-section home-pipeline-section">
        <RevealGroup amount={0.24} delayChildren={0.04} staggerChildren={0.08}>
          <RevealItem className="home-section-label">
            <span className="home-label">{copy.detectEyebrow}</span>
            <h2>{copy.detectTitle}</h2>
          </RevealItem>
          <RevealGroup className="home-pipeline" amount={0.28}>
            {copy.detectItems.map((item, i)=> {
              const Icon = DETECT_ICONS[i % DETECT_ICONS.length]
              return (
                <RevealItem key={item} className="home-pipeline-step">
                  <span className="home-pipeline-icon-wrap">
                    <Icon className="home-pipeline-icon" />
                  </span>
                  <span className="home-pipeline-label">{item}</span>
                </RevealItem>
              )
            })}
          </RevealGroup>
        </RevealGroup>
      </section>

      {/* Como funciona */}
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

      {/* Fechamento */}
      <section id="contato" className="home-section home-closing">
        <RevealGroup className="home-final-content" amount={0.24} delayChildren={0.04} staggerChildren={0.08}>
          <RevealItem className="home-section-label">
            <span className="home-label">{copy.closingEyebrow}</span>
          </RevealItem>
          <RevealItem><h2>{copy.closingTitle}</h2></RevealItem>
          <RevealItem><p>{copy.closingBody}</p></RevealItem>
          <RevealItem className="home-closing-actions">
            <Link href="/assisted-demo" className="home-primary-cta">{copy.closingPrimary}</Link>
            <Link href="/whatsapp-setup" className="home-secondary-cta">{copy.closingSecondary}</Link>
          </RevealItem>
          <RevealItem className="home-status-note">{copy.statusNote}</RevealItem>
        </RevealGroup>
      </section>
    </div>
  )
}
