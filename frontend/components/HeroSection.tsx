"use client"

import Link from 'next/link'
import {motion, type Variants} from 'framer-motion'
import FloatingCard from '@/components/FloatingCard'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'
import {useGuardianLocale, type Locale} from '@/lib/i18n'
import styles from './HeroSection.module.css'

const heroEase:[number, number, number, number] = [0.22, 1, 0.36, 1]

type PipelineCard = {
  index:string
  label:string
  title:string
  body:string
  badge?:string
  tone:'risk' | 'trust' | 'human'
  side:'right'
  href:string
}

type HeroCopy = {
  aria:string
  eyebrow:string
  headlineLead:string[]
  headlineAccent:string
  subtitle:string
  primaryCta:string
  secondaryCta:string
  trustLabel:string
  trustItems:string[]
  phone:{
    eyebrow:string
    title:string
    body:string
    action:string
    status:string
  }
  pipelineLabel:string
  pipelineCards:PipelineCard[]
}

const heroCopy:Record<Locale, HeroCopy> = {
  'pt-BR': {
    aria:'CyberAlerta Guardian',
    eyebrow:'PROTEÇÃO ASSISTIDA',
    headlineLead:['Proteção antes', 'do golpe virar'],
    headlineAccent:'prejuízo.',
    subtitle:'Uma camada de proteção assistida para famílias, cuidadores e instituições pausarem golpes por Pix, WhatsApp, links e engenharia social antes do dano.',
    primaryCta:'Abrir Guardian Console',
    secondaryCta:'Ver demonstração',
    trustLabel:'Sinais de confiança',
    trustItems:[
      'Proteção 24/7',
      'Privacidade por design',
      'Conformidade LGPD',
      'Confiança verificável',
    ],
    phone:{
      eyebrow:'ALERTA DE RISCO',
      title:'Pix urgente',
      body:'Número novo solicita transferência imediata.',
      action:'Pausar ação',
      status:'Trust Lock pronto',
    },
    pipelineLabel:'Pipeline de proteção assistida',
    pipelineCards:[
      {
        index:'01',
        label:'Mensagem',
        title:'Mensagem suspeita',
        body:'Pix urgente, número novo e pressão para não ligar.',
        badge:'RISCO ALTO',
        tone:'risk',
        side:'right',
        href:'/chatbot-demo',
      },
      {
        index:'02',
        label:'Guardian',
        title:'Guardian intercepta',
        body:'Risco alto detectado. Trust Lock pausa a ação.',
        tone:'trust',
        side:'right',
        href:'/before-pix',
      },
      {
        index:'03',
        label:'Apoio',
        title:'Responsável notificado',
        body:'Contexto claro chega ao cuidador ou familiar certo.',
        tone:'human',
        side:'right',
        href:'/family-console',
      },
    ],
  },
  'en-US': {
    aria:'CyberAlerta Guardian',
    eyebrow:'ASSISTED PROTECTION',
    headlineLead:['Protection before', 'scams become'],
    headlineAccent:'losses.',
    subtitle:'An assisted protection layer for families, caregivers, and institutions to pause Pix, WhatsApp, link, and social engineering scams before harm happens.',
    primaryCta:'Open Guardian Console',
    secondaryCta:'View demo',
    trustLabel:'Trust signals',
    trustItems:[
      '24/7 protection',
      'Privacy by design',
      'LGPD compliance',
      'Verifiable trust',
    ],
    phone:{
      eyebrow:'RISK ALERT',
      title:'Urgent Pix request',
      body:'A new number requests an immediate transfer.',
      action:'Pause action',
      status:'Trust Lock ready',
    },
    pipelineLabel:'Assisted protection pipeline',
    pipelineCards:[
      {
        index:'01',
        label:'Message',
        title:'Suspicious message',
        body:'Urgent Pix request, new number, and pressure not to call.',
        badge:'HIGH RISK',
        tone:'risk',
        side:'right',
        href:'/chatbot-demo',
      },
      {
        index:'02',
        label:'Guardian',
        title:'Guardian intercepts',
        body:'High risk detected. Trust Lock pauses the action.',
        tone:'trust',
        side:'right',
        href:'/before-pix',
      },
      {
        index:'03',
        label:'Support',
        title:'Responsible contact notified',
        body:'Clear context reaches the right caregiver or family member.',
        tone:'human',
        side:'right',
        href:'/family-console',
      },
    ],
  },
}

const heroTimeline = {
  phone:0.32,
  glow:0.46,
  link:0.66,
  cards:[0.76, 1.12, 1.48],
  connectors:[1.02, 1.38],
}

function itemVariants(reduceMotion:boolean):Variants {
  if(reduceMotion){
    return {
      hidden:{opacity:1, y:0},
      show:{opacity:1, y:0, transition:{duration:0.01}},
    }
  }

  return {
    hidden:{opacity:0, y:24},
    show:{
      opacity:1,
      y:0,
      transition:{duration:0.55, ease:heroEase},
    },
  }
}

function connectorVariants(delay:number, reduceMotion:boolean):Variants {
  if(reduceMotion){
    return {
      hidden:{opacity:1, scaleY:1},
      show:{opacity:1, scaleY:1, transition:{duration:0.01}},
    }
  }

  return {
    hidden:{opacity:0, scaleY:0},
    show:{
      opacity:1,
      scaleY:1,
      transition:{duration:0.42, delay, ease:heroEase},
    },
  }
}

function PhoneFocus({copy, reduceMotion}:{copy:HeroCopy['phone']; reduceMotion:boolean}){
  return (
    <div className={styles.phoneAnchor} aria-hidden="true">
      <motion.div
        className={styles.phoneFocus}
        initial={reduceMotion ? false : {opacity:0, y:18, scale:0.97}}
        animate={{opacity:1, y:0, scale:1}}
        transition={reduceMotion ? {duration:0.01} : {duration:0.75, delay:heroTimeline.phone, ease:heroEase}}
      >
        <div className={styles.phoneSpeaker} />
        <div className={styles.phoneScreen}>
          <div className={styles.phoneStatusbar}>
            <span>09:41</span>
            <i />
          </div>
          <div className={styles.phoneAlertIcon}>!</div>
          <span className={styles.phoneEyebrow}>{copy.eyebrow}</span>
          <strong>{copy.title}</strong>
          <p>{copy.body}</p>
          <div className={styles.phoneRiskLines}><span /><span /><span /></div>
          <div className={styles.phoneAction}>{copy.action}</div>
          <div className={styles.phoneLockStatus}><i />{copy.status}</div>
        </div>
      </motion.div>
    </div>
  )
}

export default function HeroSection(){
  const shouldReduceMotion = usePrefersReducedMotion()
  const [locale] = useGuardianLocale()
  const copy = heroCopy[locale]
  const item = itemVariants(shouldReduceMotion)

  return (
    <section
      id="plataforma"
      className={`${styles.hero} ${locale === 'en-US' ? styles.heroEn : ''}`}
      aria-label={copy.aria}
    >
      <div className={styles.grid} aria-hidden="true" />
      <div className={styles.glow} aria-hidden="true" />

      <div className={styles.inner}>
        <motion.div
          className={styles.copy}
          initial="hidden"
          animate="show"
          variants={{
            hidden:{},
            show:{
              transition:{
                staggerChildren:shouldReduceMotion ? 0 : 0.07,
                delayChildren:shouldReduceMotion ? 0 : 0.08,
              },
            },
          }}
        >
          <motion.div className={styles.eyebrow} variants={item}>{copy.eyebrow}</motion.div>
          <motion.h1 className={styles.headline} variants={item}>
            {copy.headlineLead.map(line=> <span key={line}>{line}</span>)}
            <span className={styles.accent}>{copy.headlineAccent}</span>
          </motion.h1>
          <motion.p className={styles.subtitle} variants={item}>{copy.subtitle}</motion.p>
          <motion.div className={styles.actions} variants={item}>
            <Link href="/family-console" className={styles.primaryCta}>{copy.primaryCta}</Link>
            <Link href="/assisted-demo" className={styles.secondaryCta}>{copy.secondaryCta}</Link>
          </motion.div>
          <motion.div className={styles.trustStrip} variants={item} aria-label={copy.trustLabel}>
            {copy.trustItems.map(itemLabel=> <span key={itemLabel}>{itemLabel}</span>)}
          </motion.div>
        </motion.div>

        <div className={styles.visual}>
          <div className={styles.stage}>
            <div className={styles.phoneGlowAnchor} aria-hidden="true">
              <motion.div
                className={styles.phoneGlow}
                initial={shouldReduceMotion ? false : {opacity:0, scale:0.82}}
                animate={{opacity:1, scale:1}}
                transition={shouldReduceMotion ? {duration:0.01} : {duration:0.72, delay:heroTimeline.glow, ease:heroEase}}
              />
            </div>

            <PhoneFocus copy={copy.phone} reduceMotion={shouldReduceMotion} />

            <motion.div
              className={styles.phonePipelineLink}
              initial={shouldReduceMotion ? false : {opacity:0, scaleX:0}}
              animate={{opacity:1, scaleX:1}}
              transition={shouldReduceMotion ? {duration:0.01} : {duration:0.42, delay:heroTimeline.link, ease:heroEase}}
              aria-hidden="true"
            >
              <span />
            </motion.div>

            <div className={styles.pipelineStack} role="list" aria-label={copy.pipelineLabel}>
              {copy.pipelineCards.map((card,index)=> (
                <div key={card.index} className={styles.pipelineNode} role="listitem">
                  <FloatingCard
                    index={card.index}
                    label={card.label}
                    title={card.title}
                    body={card.body}
                    badge={card.badge}
                    tone={card.tone}
                    side={card.side}
                    delay={heroTimeline.cards[index]}
                    href={card.href}
                  />
                  {index < copy.pipelineCards.length - 1 && (
                    <motion.div
                      className={styles.pipelineConnector}
                      initial="hidden"
                      animate="show"
                      variants={connectorVariants(heroTimeline.connectors[index], shouldReduceMotion)}
                      aria-hidden="true"
                    >
                      <span />
                      <i />
                      <span />
                    </motion.div>
                  )}
                </div>
              ))}
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
