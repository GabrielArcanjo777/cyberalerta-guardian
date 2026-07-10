"use client"

import Link from 'next/link'
import {useEffect, useState} from 'react'
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
  phonePaused:string
  phoneSubtitle:string
}

const heroCopy:Record<Locale, HeroCopy> = {
  'pt-BR': {
    aria:'CyberAlerta — proteção contra golpes no WhatsApp',
    badge:'PROTEÇÃO ANTI-GOLPE · WHATSAPP',
    titleLines:['Proteja sua', 'família de golpes', 'no WhatsApp'],
    subtitle:'O sistema analisa as mensagens automaticamente, descarta as conversas normais e mostra no painel só os alertas de risco: Pix suspeito, link falso, falso banco e pedidos urgentes de dinheiro.',
    primaryCta:'Ver demonstração',
    secondaryCta:'Conectar WhatsApp',
    trustItems:[
      'Análise em tempo real',
      'Mensagens normais descartadas',
      'Só alertas suspeitos no painel',
      'Uso só com autorização',
    ],
    phonePaused:'Proteção ativa · resposta pausada',
    phoneSubtitle:'Análise de risco',
  },
  'en-US': {
    aria:'CyberAlerta — protection against WhatsApp scams',
    badge:'ANTI-SCAM PROTECTION · WHATSAPP',
    titleLines:['Protect your', 'family from scams', 'on WhatsApp'],
    subtitle:'The system analyzes messages automatically, discards normal conversations, and shows only risk alerts on the panel: suspicious Pix, fake links, fake bank and urgent money requests.',
    primaryCta:'See demo',
    secondaryCta:'Connect WhatsApp',
    trustItems:[
      'Real-time analysis',
      'Normal messages discarded',
      'Only suspicious alerts on the panel',
      'Authorized use only',
    ],
    phonePaused:'Protection active · reply paused',
    phoneSubtitle:'Risk analysis',
  },
}

type Scenario = {tag:string; tone:'high'|'medium'; sent:string; verdict:string}

const scenariosByLocale:Record<Locale, Scenario[]> = {
  'pt-BR': [
    {tag:'Golpe do Pix', tone:'high', sent:'Mãe, troquei de número. Preciso fazer um Pix urgente.', verdict:'Risco alto. Não transfira. Confirme com o contato salvo por ligação antes de qualquer Pix.'},
    {tag:'Falso banco', tone:'high', sent:'Banco XYZ: seu cartão foi bloqueado. Envie o código do SMS para desbloquear.', verdict:'Risco alto. Banco não pede código por mensagem. Não compartilhe o código.'},
    {tag:'Link falso', tone:'medium', sent:'Você ganhou um prêmio! Resgate aqui: bit.ly/xz9-premio', verdict:'Risco médio. Link suspeito. Não clique — verifique no app oficial.'},
  ],
  'en-US': [
    {tag:'Pix scam', tone:'high', sent:'Mom, I changed my number. I need to make an urgent Pix.', verdict:'High risk. Do not transfer. Confirm with a saved contact by phone before any transfer.'},
    {tag:'Fake bank', tone:'high', sent:'Bank XYZ: your card was blocked. Send the SMS code to unblock it.', verdict:'High risk. Banks never ask for codes by message. Do not share the code.'},
    {tag:'Fake link', tone:'medium', sent:'You won a prize! Claim here: bit.ly/xz9-prize', verdict:'Medium risk. Suspicious link. Do not click — check the official app.'},
  ],
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

/* ── Sentinel Mockup — phone that cycles through real scam examples ── */
function SentinelMockup({reduceMotion, scenario, cycleKey, copy}:{reduceMotion:boolean; scenario:Scenario; cycleKey:number; copy:HeroCopy}){
  const toneColor = scenario.tone === 'high' ? '#ff5c64' : '#f59e0b'
  return (
    <div className={styles.mockupContainer} aria-hidden="true">
      <RadarBackdrop reduceMotion={reduceMotion} />

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
              <div className={styles.chatName}>CyberAlerta</div>
              <div className={styles.chatSubtitle}>{copy.phoneSubtitle}</div>
            </div>
            <div className={styles.trustBadge}>⏸</div>
          </div>
          <div key={cycleKey} className={`${styles.chatBody} ${styles.chatCycle}`}>
            <span className={styles.chatRiskTag} style={{color: toneColor, borderColor: toneColor}}>
              {scenario.tag}
            </span>
            <div className={styles.chatBubbleSent}>
              <span className={styles.chatBubbleSentText}>{scenario.sent}</span>
              <span className={styles.chatTime}>14:22  ✓✓</span>
            </div>
            <div className={styles.chatBubbleRecv}>
              <span className={styles.chatBubbleRecvText}>{scenario.verdict}</span>
              <span className={styles.chatTime}>14:22  ✓</span>
            </div>
            <div className={styles.systemIntervention} style={{borderLeftColor: toneColor}}>
              <div className={styles.interventionIcon} style={{background: toneColor}}>⏸</div>
              <div className={styles.interventionText}>{copy.phonePaused}</div>
            </div>
          </div>
          <div className={styles.phoneKeyboard}>
            <span className={styles.phoneKeyboardHint}>Demo · WhatsApp via Evolution (não-oficial)</span>
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
  const scenarios = scenariosByLocale[locale]
  const [index, setIndex] = useState(0)

  useEffect(()=>{
    if(reduceMotion) return
    const id = setInterval(()=>setIndex(i=>(i + 1) % scenarios.length), 4200)
    return ()=>clearInterval(id)
  },[reduceMotion, scenarios.length])

  const scenario = scenarios[index % scenarios.length]

  return (
    <section id="plataforma" className={styles.hero} aria-label={copy.aria}>
      <div className={styles.gridBg} aria-hidden="true" />
      <div className={styles.glowBg} aria-hidden="true" />
      <div className={styles.watermark} aria-hidden="true">CYBERALERTA</div>

      <div className={styles.inner}>
        <div className={styles.copy}>
          <div className={styles.badge}>{copy.badge}</div>
          <h1 className={styles.title}>
            {copy.titleLines.map(line=><span key={line}>{line}</span>)}
          </h1>
          <p className={styles.subtitle}>{copy.subtitle}</p>
          <div className={styles.actions}>
            <Link href="/assisted-demo" className={styles.primaryCta}>{copy.primaryCta}</Link>
            <Link href="/login" className={styles.secondaryCta}>{copy.secondaryCta}</Link>
          </div>
          <div className={styles.trustStrip}>
            {copy.trustItems.map(label=><span key={label}>{label}</span>)}
          </div>
        </div>

        <div className={styles.visual}>
          <SentinelMockup reduceMotion={reduceMotion} scenario={scenario} cycleKey={index} copy={copy} />
        </div>
      </div>
    </section>
  )
}
