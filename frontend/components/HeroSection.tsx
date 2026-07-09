"use client"

import Link from 'next/link'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'
import {useGuardianLocale, type Locale} from '@/lib/i18n'
import styles from './HeroSection.module.css'

type HeroCopy = {
  aria:string
  badge:string
  titleLines:string[]
  subtitle:string
  primaryCta:string
  secondaryCta:string
  trustItems:string[]
}

const heroCopy:Record<Locale, HeroCopy> = {
  'pt-BR': {
    aria:'CyberAlerta Guardian',
    badge:'BETA TÉCNICO LOCAL',
    titleLines:['CYBERALERTA', 'GUARDIAN'],
    subtitle:'Monitoramento inteligente de risco com classificação explicável, automação via n8n e alertas operacionais em tempo real.',
    primaryCta:'Entrar no painel',
    secondaryCta:'Ver fluxo de risco',
    trustItems:[
      'n8n validado localmente',
      'WhatsApp via Evolution (não-oficial)',
      'Privacidade por design',
      'Decisão rastreável',
    ],
  },
  'en-US': {
    aria:'CyberAlerta Guardian',
    badge:'LOCAL TECHNICAL BETA',
    titleLines:['CYBERALERTA', 'GUARDIAN'],
    subtitle:'Intelligent risk monitoring with explainable classification, n8n automation, and real-time operational alerts.',
    primaryCta:'Sign in to panel',
    secondaryCta:'View risk flow',
    trustItems:[
      'n8n validated locally',
      'WhatsApp via Evolution (unofficial)',
      'Privacy by design',
      'Traceable decisions',
    ],
  },
}

/* ── Radar Backdrop ── */
function RadarBackdrop({reduceMotion}:{reduceMotion:boolean}){
  return (
    <div className={styles.radarBackdrop} aria-hidden="true">
      <svg className={styles.radarSvg} viewBox="0 0 400 400" fill="none" xmlns="http://www.w3.org/2000/svg">
        <circle cx="200" cy="200" r="185" stroke="rgba(20,184,166,0.06)" strokeWidth="0.5" />
        <circle cx="200" cy="200" r="130" stroke="rgba(20,184,166,0.08)" strokeWidth="0.5" />
        <circle cx="200" cy="200" r="75" stroke="rgba(20,184,166,0.12)" strokeWidth="0.5" />
        <line x1="200" y1="10" x2="200" y2="390" stroke="rgba(20,184,166,0.04)" strokeWidth="0.5" />
        <line x1="10" y1="200" x2="390" y2="200" stroke="rgba(20,184,166,0.04)" strokeWidth="0.5" />
        {!reduceMotion && (
          <g className={styles.scanSweep}>
            <line x1="200" y1="200" x2="200" y2="15" stroke="rgba(20,184,166,0.15)" strokeWidth="0.5" />
          </g>
        )}
      </svg>
    </div>
  )
}

/* ── Sentinel Mockup — Realistic Phone ── */
function SentinelMockup({reduceMotion}:{reduceMotion:boolean}){
  return (
    <div
      className={styles.mockupContainer}
      aria-hidden="true"
    >
      <RadarBackdrop reduceMotion={reduceMotion} />

      {/* Phone Mockup */}
      <div className={styles.phoneFrame}>
        <div className={styles.phoneNotch} />
        <div className={styles.phoneScreen}>
          <div className={styles.phoneStatus}>
            <span className={styles.phoneTime}>14:22</span>
            <span className={styles.phoneIcons}>●●●○○  ▮▮▮</span>
          </div>
          <div className={styles.chatHeader}>
            <div className={styles.chatAvatar} />
            <div className={styles.chatHeaderInfo}>
              <div className={styles.chatName}>CyberAlerta Guardian</div>
              <div className={styles.chatSubtitle}>Análise de risco</div>
            </div>
            <div className={styles.trustBadge}>⏸</div>
          </div>
          <div className={styles.chatBody}>
            <div className={styles.chatBubbleSent}>
              <span className={styles.chatBubbleSentText}>Recebi isso: &quot;Mãe, troquei de número. Preciso fazer um Pix urgente.&quot;</span>
              <span className={styles.chatTime}>14:22  ✓✓</span>
            </div>
            <div className={styles.chatBubbleRecv}>
              <span className={styles.chatBubbleRecvText}>Risco alto detectado. Não responda ainda. Confirme com o contato salvo antes de qualquer transferência.</span>
              <span className={styles.chatTime}>14:22  ✓</span>
            </div>
            <div className={styles.systemIntervention}>
              <div className={styles.interventionIcon}>⏸</div>
              <div className={styles.interventionText}>Trust Lock ativo · ação pausada</div>
            </div>
          </div>
          <div className={styles.phoneKeyboard}>
            <span className={styles.phoneKeyboardHint}>Demo local · WhatsApp via Evolution (não-oficial)</span>
          </div>
        </div>
      </div>
    </div>
  )
}

export default function HeroSection(){
  const reduceMotion = usePrefersReducedMotion()
  const [locale] = useGuardianLocale()
  const copy = heroCopy[locale]

  return (
    <section id="plataforma" className={styles.hero} aria-label={copy.aria}>
      <div className={styles.gridBg} aria-hidden="true" />
      <div className={styles.glowBg} aria-hidden="true" />
      <div className={styles.watermark} aria-hidden="true">GUARDIAN</div>

      <div className={styles.inner}>
        <div className={styles.copy}>
          <div className={styles.badge}>{copy.badge}</div>
          <h1 className={styles.title}>
            {copy.titleLines.map(line=><span key={line}>{line}</span>)}
          </h1>
          <p className={styles.subtitle}>{copy.subtitle}</p>
          <div className={styles.actions}>
            <Link href="/login" className={styles.primaryCta}>{copy.primaryCta}</Link>
            <Link href="/assisted-demo" className={styles.secondaryCta}>{copy.secondaryCta}</Link>
          </div>
          <div className={styles.trustStrip}>
            {copy.trustItems.map(label=><span key={label}>{label}</span>)}
          </div>
        </div>

        <div className={styles.visual}>
          <SentinelMockup reduceMotion={reduceMotion} />
        </div>
      </div>
    </section>
  )
}
