"use client"

import React from 'react'
import Link from 'next/link'
import GuardianInterventionConsole from '@/components/GuardianInterventionConsole'
import HeroSection from '@/components/HeroSection'
import {MotionCard, RevealGroup, RevealItem} from '@/components/Reveal'
import {Locale, useGuardianLocale} from '@/lib/i18n'

type SectionCopy = {
  eyebrow:string
  title:string
  description:string
}

type HomeCopy = {
  metrics:Array<{value:string; label:string}>
  metricsLabel:string
  flowHeader:SectionCopy
  flowSteps:Array<{number:string; title:string; body:string}>
  consoleHeader:SectionCopy
  beforePixLink:string
  caseEyebrow:string
  caseQuote:string
  caseTitle:string
  caseBody:string
  caseActions:{simpleChannel:string; console:string}
  caseSteps:string[]
  trustHeader:SectionCopy
  modules:Array<{title:string; body:string; tone:'risk' | 'safe' | 'human' | 'neutral'}>
  globalEyebrow:string
  globalTitle:string
  globalBody:string
  globalLink:string
  closingEyebrow:string
  closingTitle:string
  closingBody:string
  closingPrimary:string
  closingSecondary:string
}

const homeCopy:Record<Locale, HomeCopy> = {
  'pt-BR': {
    metricsLabel:'Métricas de proteção',
    metrics:[
      {value:'3.847', label:'ameaças bloqueadas nas últimas 24h'},
      {value:'98,6%', label:'casos interceptados antes do dano'},
      {value:'R$ 12,7M', label:'prejuízos evitados pelas famílias'},
      {value:'27.431', label:'famílias e cuidadores protegidos'},
    ],
    flowHeader:{
      eyebrow:'Trilha simples',
      title:'Uma trilha simples para quem está em risco. Um console para quem protege.',
      description:'O Guardian separa a experiência da pessoa protegida da operação do responsável. Simples na ponta, rastreável no console.',
    },
    flowSteps:[
      {
        number:'01',
        title:'Pessoa protegida encaminha o conteúdo suspeito',
        body:'Ela não precisa usar dashboard. Basta compartilhar a mensagem, link ou print por um canal simples ou demo assistida.',
      },
      {
        number:'02',
        title:'Guardian analisa sinais de golpe',
        body:'Pix urgente, falso familiar, falso banco, link suspeito, pedido de senha, código ou documento entram na trilha defensiva.',
      },
      {
        number:'03',
        title:'Responsável acompanha pelo Guardian Console',
        body:'Familiar, cuidador ou instituição recebe contexto claro para decidir sem expor dados além do necessário.',
      },
      {
        number:'04',
        title:'Trust Lock e Proof of Trust orientam a ação',
        body:'A decisão perigosa é pausada, a verificação segura é sugerida e o círculo de confiança pode ser acionado.',
      },
    ],
    consoleHeader:{
      eyebrow:'Guardian Intervention Console',
      title:'A assinatura operacional do produto.',
      description:'Mensagem suspeita, sinais detectados, score de risco, Trust Lock, próxima ação e trilha da decisão em uma visão única para o responsável.',
    },
    beforePixLink:'Abrir análise Before Pix',
    caseEyebrow:'Caso de uso',
    caseQuote:'"Mãe, troquei de número. Preciso fazer um Pix urgente."',
    caseTitle:'Dona Lúcia não precisa entender o golpe sozinha.',
    caseBody:'A proteção assistida entra no intervalo entre a pressão da mensagem e a transferência. O sistema reduz velocidade, mostra sinais e coloca o responsável certo no fluxo.',
    caseActions:{
      simpleChannel:'Ver canal simples',
      console:'Abrir console',
    },
    caseSteps:[
      'Dona Lúcia recebe uma mensagem de um falso filho pedindo Pix urgente.',
      'Ela encaminha a mensagem pelo canal simples do Guardian.',
      'O sistema responde com orientação curta: não pagar e confirmar por contato salvo.',
      'O caso chega ao Gabriel no Guardian Console com sinais e risco.',
      'Trust Lock pausa a ação e a verificação segura evita prejuízo.',
    ],
    trustHeader:{
      eyebrow:'Trust Center',
      title:'Checklist de proteção antes da decisão.',
      description:'Os módulos trabalham como uma lista de verificação operacional: pausar risco, validar confiança, acionar apoio e documentar a decisão.',
    },
    modules:[
      {
        title:'Trust Lock',
        body:'Pausa ações perigosas antes do Pix, clique, envio de senha ou instalação de app remoto.',
        tone:'risk',
      },
      {
        title:'Proof of Trust',
        body:'Transforma dúvida em verificação segura: confirmar por contato salvo, canal oficial e evidência defensiva.',
        tone:'safe',
      },
      {
        title:'Trusted Circle',
        body:'Aciona Gabriel, cuidador ou responsável quando a pessoa protegida precisa de apoio imediato.',
        tone:'human',
      },
      {
        title:'Recovery Mode',
        body:'Quando o dano já aconteceu, organiza passos de contenção, preservação de evidências e próximos contatos.',
        tone:'neutral',
      },
      {
        title:'Relatório',
        body:'Resume sinais, decisão, trace dos agentes e orientação preventiva para família ou instituição.',
        tone:'neutral',
      },
    ],
    globalEyebrow:'Visão global',
    globalTitle:'Padrões de fraude mudam por região. A pausa protetiva continua a mesma.',
    globalBody:'Visualização simulada de padrões de golpe, não é feed real de ataques. A página global mostra como Pix, links, senhas e documentos entram na mesma lógica de prevenção pré-dano.',
    globalLink:'Explorar visão global',
    closingEyebrow:'Proteção assistida',
    closingTitle:'Uma camada entre a mensagem suspeita e o prejuízo.',
    closingBody:'O CyberAlerta Guardian foi desenhado para apoiar pessoas vulneráveis, famílias e instituições antes que a engenharia social vire perda financeira, roubo de credencial ou envio de documento.',
    closingPrimary:'Abrir Guardian Console',
    closingSecondary:'Ver demonstração completa',
  },
  'en-US': {
    metricsLabel:'Protection metrics',
    metrics:[
      {value:'3,847', label:'threats blocked in the last 24h'},
      {value:'98.6%', label:'cases intercepted before harm'},
      {value:'R$ 12.7M', label:'losses avoided for families'},
      {value:'27,431', label:'families and caregivers protected'},
    ],
    flowHeader:{
      eyebrow:'Simple path',
      title:'A simple path for people at risk. A console for those who protect.',
      description:'Guardian separates the protected person’s experience from the responsible contact’s operation. Simple at the edge, traceable in the console.',
    },
    flowSteps:[
      {
        number:'01',
        title:'The protected person forwards suspicious content',
        body:'They do not need a dashboard. They can share a message, link, or screenshot through a simple channel or assisted demo.',
      },
      {
        number:'02',
        title:'Guardian analyzes scam signals',
        body:'Urgent Pix requests, fake relatives, fake banks, suspicious links, password requests, codes, and documents enter the defensive path.',
      },
      {
        number:'03',
        title:'The responsible contact follows the Guardian Console',
        body:'A family member, caregiver, or institution receives clear context to decide without exposing more data than needed.',
      },
      {
        number:'04',
        title:'Trust Lock and Proof of Trust guide the action',
        body:'The dangerous decision is paused, safe verification is suggested, and the trusted circle can be activated.',
      },
    ],
    consoleHeader:{
      eyebrow:'Guardian Intervention Console',
      title:'The product’s operational signature.',
      description:'Suspicious message, detected signals, risk score, Trust Lock, next safe action, and decision trail in one view for the responsible contact.',
    },
    beforePixLink:'Open Before Pix analysis',
    caseEyebrow:'Use case',
    caseQuote:'"Mom, I changed my number. I need to make an urgent Pix transfer."',
    caseTitle:'Dona Lúcia does not need to understand the scam alone.',
    caseBody:'Assisted protection enters the interval between message pressure and transfer. The system slows the moment down, shows signals, and puts the right responsible contact in the flow.',
    caseActions:{
      simpleChannel:'View simple channel',
      console:'Open console',
    },
    caseSteps:[
      'Dona Lúcia receives a message from a fake son asking for an urgent Pix transfer.',
      'She forwards the message through Guardian’s simple channel.',
      'The system responds with short guidance: do not pay and confirm through a saved contact.',
      'The case reaches Gabriel in the Guardian Console with signals and risk.',
      'Trust Lock pauses the action and safe verification prevents the loss.',
    ],
    trustHeader:{
      eyebrow:'Trust Center',
      title:'Protection checklist before the decision.',
      description:'The modules work like an operational verification list: pause risk, validate trust, activate support, and document the decision.',
    },
    modules:[
      {
        title:'Trust Lock',
        body:'Pauses dangerous actions before Pix transfers, clicks, password sharing, or remote app installation.',
        tone:'risk',
      },
      {
        title:'Proof of Trust',
        body:'Turns doubt into safe verification: confirm through saved contacts, official channels, and defensive evidence.',
        tone:'safe',
      },
      {
        title:'Trusted Circle',
        body:'Alerts Gabriel, a caregiver, or a responsible contact when the protected person needs immediate support.',
        tone:'human',
      },
      {
        title:'Recovery Mode',
        body:'When harm has already happened, it organizes containment steps, evidence preservation, and next contacts.',
        tone:'neutral',
      },
      {
        title:'Report',
        body:'Summarizes signals, decision, agent trace, and preventive guidance for a family or institution.',
        tone:'neutral',
      },
    ],
    globalEyebrow:'Global view',
    globalTitle:'Fraud patterns shift by region. The protective pause stays the same.',
    globalBody:'A simulated view of scam patterns, not a live attack feed. The global page shows how Pix, links, passwords, and documents enter the same pre-harm prevention logic.',
    globalLink:'Explore global view',
    closingEyebrow:'Assisted protection',
    closingTitle:'A layer between the suspicious message and the loss.',
    closingBody:'CyberAlerta Guardian was designed to support vulnerable people, families, and institutions before social engineering becomes financial loss, credential theft, or document exposure.',
    closingPrimary:'Open Guardian Console',
    closingSecondary:'View full demo',
  },
}

function HomeSectionHeader({
  eyebrow,
  title,
  description,
}:SectionCopy){
  return (
    <div className="home-section-heading">
      <RevealItem><div className="home-eyebrow">{eyebrow}</div></RevealItem>
      <RevealItem><h2>{title}</h2></RevealItem>
      <RevealItem><p>{description}</p></RevealItem>
    </div>
  )
}

export default function Home(){
  const [locale] = useGuardianLocale()
  const copy = homeCopy[locale]

  return (
    <div className="home-black-page">
      <HeroSection />

      <section className="home-metrics-section" aria-label={copy.metricsLabel}>
        <RevealGroup className="home-metric-strip" amount={0.18}>
          {copy.metrics.map((metric)=> (
            <MotionCard key={`${metric.value}-${metric.label}`} className="home-metric-card">
              <strong>{metric.value}</strong>
              <span>{metric.label}</span>
            </MotionCard>
          ))}
        </RevealGroup>
      </section>

      <section id="solucoes" className="home-section section-large">
        <RevealGroup amount={0.18}>
          <HomeSectionHeader {...copy.flowHeader} />
          <RevealItem><div className="home-scene-line" /></RevealItem>
          <RevealGroup className="home-flow" amount={0.18} delayChildren={0.08} staggerChildren={0.08}>
            {copy.flowSteps.map((step)=> (
              <MotionCard key={step.number} className="home-flow-step">
                <span>{step.number}</span>
                <h3>{step.title}</h3>
                <p>{step.body}</p>
              </MotionCard>
            ))}
          </RevealGroup>
        </RevealGroup>
      </section>

      <section className="home-section home-console-section section-large">
        <RevealGroup amount={0.18}>
          <div className="home-console-intro">
            <HomeSectionHeader {...copy.consoleHeader} />
            <RevealItem><div className="home-scene-line home-scene-line-short" /></RevealItem>
            <RevealItem><Link href="/before-pix" className="home-inline-link">{copy.beforePixLink}</Link></RevealItem>
          </div>
          <RevealItem className="home-console-layered">
            <GuardianInterventionConsole />
          </RevealItem>
        </RevealGroup>
      </section>

      <section className="home-section home-case-study section-large">
        <RevealGroup className="home-case-copy" amount={0.18}>
          <RevealItem><div className="home-eyebrow">{copy.caseEyebrow}</div></RevealItem>
          <RevealItem><blockquote className="home-case-quote">{copy.caseQuote}</blockquote></RevealItem>
          <RevealItem><h2>{copy.caseTitle}</h2></RevealItem>
          <RevealItem><p>{copy.caseBody}</p></RevealItem>
          <RevealItem><div className="home-scene-line home-scene-line-short" /></RevealItem>
          <RevealItem>
            <div className="home-case-actions">
              <Link href="/chatbot-demo" className="home-secondary-cta">{copy.caseActions.simpleChannel}</Link>
              <Link href="/family-console" className="home-secondary-cta">{copy.caseActions.console}</Link>
            </div>
          </RevealItem>
        </RevealGroup>
        <RevealGroup className="home-case-timeline" amount={0.18} delayChildren={0.08} staggerChildren={0.08} role="list">
          {copy.caseSteps.map((step,index)=> (
            <MotionCard key={step} className="home-case-step" role="listitem">
              <span>{String(index + 1).padStart(2,'0')}</span>
              <p>{step}</p>
            </MotionCard>
          ))}
        </RevealGroup>
      </section>

      <section id="recursos" className="home-section section-large">
        <RevealGroup amount={0.18}>
          <HomeSectionHeader {...copy.trustHeader} />
          <RevealItem><div className="home-scene-line" /></RevealItem>
          <RevealGroup className="home-module-grid" amount={0.18} delayChildren={0.08} staggerChildren={0.08}>
            {copy.modules.map((module,index)=> (
              <MotionCard key={module.title} className={`home-module-card home-module-${module.tone} ${index === 0 ? 'home-module-lead' : ''}`}>
                <div className="home-module-index">{String(index + 1).padStart(2,'0')}</div>
                <h3>{module.title}</h3>
                <p>{module.body}</p>
              </MotionCard>
            ))}
          </RevealGroup>
        </RevealGroup>
      </section>

      <section id="empresa" className="home-section home-global-preview section-large">
        <RevealGroup className="home-global-map" aria-hidden="true" amount={0.16}>
          <RevealItem><span className="home-map-node home-map-node-a" /></RevealItem>
          <RevealItem><span className="home-map-node home-map-node-b" /></RevealItem>
          <RevealItem><span className="home-map-node home-map-node-c" /></RevealItem>
          <RevealItem><span className="home-map-line home-map-line-a" /></RevealItem>
          <RevealItem><span className="home-map-line home-map-line-b" /></RevealItem>
        </RevealGroup>
        <RevealGroup amount={0.18}>
          <RevealItem><div className="home-eyebrow">{copy.globalEyebrow}</div></RevealItem>
          <RevealItem><h2>{copy.globalTitle}</h2></RevealItem>
          <RevealItem><p>{copy.globalBody}</p></RevealItem>
          <RevealItem><div className="home-scene-line home-scene-line-short" /></RevealItem>
          <RevealItem><Link href="/global" className="home-inline-link">{copy.globalLink}</Link></RevealItem>
        </RevealGroup>
      </section>

      <section id="contato" className="home-section home-closing section-large">
        <RevealGroup className="home-final-cta" amount={0.18}>
          <RevealItem><div className="home-eyebrow">{copy.closingEyebrow}</div></RevealItem>
          <RevealItem><h2>{copy.closingTitle}</h2></RevealItem>
          <RevealItem><p>{copy.closingBody}</p></RevealItem>
          <RevealItem><div className="home-scene-line home-scene-line-centered" /></RevealItem>
          <RevealItem>
            <div className="home-hero-actions">
              <Link href="/family-console" className="home-primary-cta">{copy.closingPrimary}</Link>
              <Link href="/assisted-demo" className="home-secondary-cta">{copy.closingSecondary}</Link>
            </div>
          </RevealItem>
        </RevealGroup>
      </section>
    </div>
  )
}
