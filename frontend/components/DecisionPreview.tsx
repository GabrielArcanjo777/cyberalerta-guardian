"use client"

import React from 'react'
import {RevealGroup, RevealItem} from '@/components/Reveal'
import {useGuardianLocale, type Locale} from '@/lib/i18n'

const previewCopy:Record<Locale, {
  eyebrow:string
  title:string
  signal:{label:string; message:string; origin:string; signs:string}
  trust:{
    label:string
    severityKey:string
    severityValue:string
    actionKey:string
    actionValue:string
    recommendationKey:string
    recommendationValue:string
  }
  trail:Array<{step:string; label:string}>
}> = {
  'pt-BR': {
    eyebrow:'DECISION TRACE',
    title:'O sistema observa, interpreta e orienta',
    signal:{
      label:'SIGNAL - MENSAGEM SUSPEITA',
      message:'"Mãe, troquei de número. Preciso fazer um Pix urgente."',
      origin:'Origem: não verificada',
      signs:'Sinais: urgência, número novo, pressão emocional',
    },
    trust:{
      label:'TRUST LAYER - DECISÃO SEGURA',
      severityKey:'SEVERIDADE:',
      severityValue:'ALTA',
      actionKey:'AÇÃO:',
      actionValue:'PAUSAR RESPOSTA',
      recommendationKey:'REC:',
      recommendationValue:'CONFIRMAR COM CONTATO SALVO',
    },
    trail:[
      {step:'01', label:'Sinais detectados'},
      {step:'02', label:'Risco classificado'},
      {step:'03', label:'Ação segura sugerida'},
    ],
  },
  'en-US': {
    eyebrow:'DECISION TRACE',
    title:'The system observes, interprets, and guides',
    signal:{
      label:'SIGNAL - SUSPICIOUS MESSAGE',
      message:'"Mom, I changed my number. I need to make an urgent Pix transfer."',
      origin:'Source: unverified',
      signs:'Signals: urgency, new number, emotional pressure',
    },
    trust:{
      label:'TRUST LAYER - SAFE DECISION',
      severityKey:'SEVERITY:',
      severityValue:'HIGH',
      actionKey:'ACTION:',
      actionValue:'PAUSE RESPONSE',
      recommendationKey:'REC:',
      recommendationValue:'CONFIRM W/ SAVED CONTACT',
    },
    trail:[
      {step:'01', label:'Signals detected'},
      {step:'02', label:'Risk classified'},
      {step:'03', label:'Safe action suggested'},
    ],
  },
}

export default function DecisionPreview(){
  const [locale] = useGuardianLocale()
  const copy = previewCopy[locale]

  return (
    <section id="solucoes" className="decision-preview-v2" aria-label={copy.title}>
      <RevealGroup amount={0.24} delayChildren={0.04} staggerChildren={0.08}>
        <RevealItem className="decision-preview-header">
          <span className="decision-preview-eyebrow">{copy.eyebrow}</span>
          <h2 className="decision-preview-title">{copy.title}</h2>
        </RevealItem>

        <RevealGroup className="decision-engine-container" amount={0.34} delayChildren={0.08} staggerChildren={0.09}>
          <RevealItem className="decision-engine-panel panel-signal">
            <div className="panel-header">
              <span className="panel-dot dot-warn"></span>
              {copy.signal.label}
            </div>
            <div className="panel-body">
              <div className="suspect-message-box">
                {copy.signal.message}
              </div>
              <div className="signal-metadata">
                <div className="meta-item">
                  <span className="meta-icon" aria-hidden="true">::</span>
                  {copy.signal.origin}
                </div>
                <div className="meta-item">
                  <span className="meta-icon" aria-hidden="true">::</span>
                  {copy.signal.signs}
                </div>
              </div>
            </div>
          </RevealItem>

          <RevealItem className="decision-engine-trace">
            <svg viewBox="0 0 100 100" preserveAspectRatio="none" className="trace-svg" aria-hidden="true">
              <path d="M0,50 L30,50 L40,20 L60,80 L70,50 L100,50" className="trace-line" />
              <circle cx="50" cy="50" r="10" className="trace-node" />
            </svg>
          </RevealItem>

          <RevealItem className="decision-engine-panel panel-trust">
            <div className="panel-header">
              <span className="panel-dot dot-safe"></span>
              {copy.trust.label}
            </div>
            <div className="panel-body">
              <div className="trust-metadata">
                <div className="trust-item severity-high">
                  <span className="trust-key">{copy.trust.severityKey}</span>
                  <span className="trust-val">{copy.trust.severityValue}</span>
                </div>
                <div className="trust-item">
                  <span className="trust-key">{copy.trust.actionKey}</span>
                  <span className="trust-val">{copy.trust.actionValue}</span>
                </div>
                <div className="trust-item highlight-box">
                  <span className="trust-key">{copy.trust.recommendationKey}</span>
                  <span className="trust-val">{copy.trust.recommendationValue}</span>
                </div>
              </div>
            </div>
          </RevealItem>
        </RevealGroup>

        <RevealGroup className="decision-trail-v2" amount={0.35} delayChildren={0.08} staggerChildren={0.08}>
          {copy.trail.map((item, idx)=>(
            <RevealItem key={item.step} className="trail-step-v2">
              <div className="trail-node-v2"></div>
              <div className="trail-content-v2">
                <span className="trail-number-v2">{item.step}</span>
                <span className="trail-label-v2">{item.label}</span>
              </div>
              {idx < copy.trail.length - 1 && <div className="trail-connector-v2"></div>}
            </RevealItem>
          ))}
        </RevealGroup>
      </RevealGroup>
    </section>
  )
}
