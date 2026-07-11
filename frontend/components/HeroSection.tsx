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
  phoneTitle:string
  phoneInvariant:string
  phoneSubtitle:string
  phoneInboundLabel:string
  phoneCaptured:string
  phoneFooter:string
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
    phoneTitle:'Monitoramento Guardian',
    phoneInvariant:'Nenhuma resposta enviada ao remetente.',
    phoneSubtitle:'Somente leitura · análise silenciosa',
    phoneInboundLabel:'Mensagem recebida',
    phoneCaptured:'Capturada para análise às 14:22',
    phoneFooter:'Único destino permitido: contato de confiança',
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
    phoneTitle:'Guardian monitoring',
    phoneInvariant:'No reply sent to the sender.',
    phoneSubtitle:'Read-only · silent analysis',
    phoneInboundLabel:'Inbound message',
    phoneCaptured:'Captured for analysis at 14:22',
    phoneFooter:'Only allowed destination: trusted contact',
  },
}

type Scenario = {tag:string; tone:'high'|'medium'; sent:string; outcome:string; alerted:boolean}

// Fluxo real: a mensagem é analisada em silêncio. Risco ALTO => alerta enviado
// SOMENTE ao contato de confiança. Risco MÉDIO => caso no console, sem alerta.
// O bot nunca responde no chat do golpista/pessoa protegida.
const scenariosByLocale:Record<Locale, Scenario[]> = {
  'pt-BR': [
    {tag:'Golpe do Pix', tone:'high', alerted:true, sent:'Mãe, troquei de número. Preciso fazer um Pix urgente.', outcome:'Ação segura: alertar somente o contato de confiança. Risco alto — golpe do Pix; confirme por ligação antes de transferir.'},
    {tag:'Falso banco', tone:'high', alerted:true, sent:'Banco XYZ: seu cartão foi bloqueado. Envie o código do SMS para desbloquear.', outcome:'Ação segura: alertar somente o contato de confiança. Risco alto — falso banco pedindo código de SMS.'},
    {tag:'Link falso', tone:'medium', alerted:false, sent:'Você ganhou um prêmio! Resgate aqui: bit.ly/xz9-premio', outcome:'Ação segura: registrar no Guardian Console para revisão. Sem alerta e sem resposta ao remetente.'},
  ],
  'en-US': [
    {tag:'Pix scam', tone:'high', alerted:true, sent:'Mom, I changed my number. I need to make an urgent Pix.', outcome:'Safe action: alert only the trusted contact. High risk — Pix scam; confirm by phone before any transfer.'},
    {tag:'Fake bank', tone:'high', alerted:true, sent:'Bank XYZ: your card was blocked. Send the SMS code to unblock it.', outcome:'Safe action: alert only the trusted contact. High risk — fake bank asking for an SMS code.'},
    {tag:'Fake link', tone:'medium', alerted:false, sent:'You won a prize! Claim here: bit.ly/xz9-prize', outcome:'Safe action: log it in the Guardian Console for review. No alert and no reply to the sender.'},
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
            <div className={styles.monitorAvatar}>G</div>
            <div className={styles.chatHeaderInfo}>
              <div className={styles.chatName}>{copy.phoneTitle}</div>
              <div className={styles.chatSubtitle}>{copy.phoneSubtitle}</div>
            </div>
            <div className={styles.trustBadge}>🛡</div>
          </div>
          <div key={cycleKey} className={`${styles.chatBody} ${styles.chatCycle}`}>
            <span className={styles.chatRiskTag} style={{color: toneColor, borderColor: toneColor}}>
              {scenario.tag}
            </span>
            <div className={styles.inboundMessageCard}>
              <span className={styles.inboundLabel}>{copy.phoneInboundLabel}</span>
              <span className={styles.inboundMessageText}>{scenario.sent}</span>
              <span className={styles.inboundMeta}>{copy.phoneCaptured}</span>
            </div>
            {/* Resultado da análise — nunca é uma resposta no chat */}
            <div
              className={styles.systemIntervention}
              style={{
                borderColor: toneColor,
                borderLeftColor: toneColor,
                background: scenario.alerted ? '#fdecec' : '#fff8e8',
              }}
            >
              <div className={styles.interventionIcon} style={{background: toneColor}}>
                {scenario.alerted ? '!' : '◷'}
              </div>
              <div className={styles.interventionText} style={{color: scenario.alerted ? '#7f1d1d' : '#6b3f06'}}>
                {scenario.outcome}
              </div>
            </div>
            <div
              className={styles.systemIntervention}
              style={{marginTop: 10, borderColor: '#14b8a6', borderLeftColor: '#14b8a6', background: '#eefaf6', boxShadow: '5px 5px 0 rgba(20,184,166,0.1)'}}
            >
              <div className={styles.interventionIcon} style={{background: '#14b8a6'}}>✓</div>
              <div className={styles.interventionText} style={{color: '#0f5147'}}>{copy.phoneInvariant}</div>
            </div>
          </div>
          <div className={styles.monitorFooter}>
            <span aria-hidden="true">🔒</span>
            <span>{copy.phoneFooter}</span>
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
            {copy.titleLines.map((line, i)=>(
              <span key={line} className={styles.titleLine}>
                <span
                  className={styles.titleLineInner}
                  style={{animationDelay: `${120 + i * 110}ms`}}
                >
                  {line}
                </span>
              </span>
            ))}
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
