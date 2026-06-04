"use client"

import React from 'react'
import Link from 'next/link'
import GuardianInterventionConsole from '@/components/GuardianInterventionConsole'
import HeroSection from '@/components/HeroSection'
import {RevealGroup, RevealItem, ScrollScene} from '@/components/Reveal'

const flowSteps = [
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
]

const productModules = [
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
    body:'Aciona familiar, cuidador ou responsável quando a pessoa protegida precisa de apoio imediato.',
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
]

const caseSteps = [
  'Dona Lúcia recebe uma mensagem de um falso filho pedindo Pix urgente.',
  'Ela encaminha a mensagem pelo canal simples do Guardian.',
  'O sistema responde com orientação curta: não pagar e confirmar por contato salvo.',
  'O caso chega ao responsável no Guardian Console com sinais e risco.',
  'Trust Lock pausa a ação e a verificação segura evita prejuízo.',
]

const metrics = [
  ['3.847', 'Ameaças bloqueadas nas últimas 24h'],
  ['98,6%', 'Casos interceptados antes do dano'],
  ['R$ 12,7M', 'Prejuízos evitados pelas famílias'],
  ['27.431', 'Famílias e cuidadores protegidos'],
  ['100%', 'Privacidade e dados protegidos por design'],
]

function HomeSectionHeader({
  eyebrow,
  title,
  description,
}:{
  eyebrow:string
  title:string
  description:string
}){
  return (
    <div className="home-section-heading">
      <div className="home-eyebrow">{eyebrow}</div>
      <h2>{title}</h2>
      <p>{description}</p>
    </div>
  )
}

export default function Home(){
  return (
    <div className="home-black-page">
      <HeroSection />

      <RevealGroup as="section" className="home-section home-second-fold" variant="soft" amount={0.15} delayChildren={0.08} stagger={0.08}>
        <RevealItem as="blockquote" className="home-testimonial" index={0}>
          <p>“Quase fiz um Pix de R$ 4.850,00 para um golpista...”</p>
          <footer>Dona Lúcia, 72 anos</footer>
        </RevealItem>

        <RevealGroup as="div" className="home-metrics-row" variant="card" amount={0.1} delayChildren={0.05} stagger={0.08} aria-label="Métricas simuladas de proteção">
          {metrics.map(([value,label],index)=> (
            <RevealItem as="div" key={label} className="home-metric-item" index={index}>
              <strong>{value}</strong>
              <span>{label}</span>
            </RevealItem>
          ))}
        </RevealGroup>
      </RevealGroup>

      <ScrollScene as="section" className="home-section home-console-section scroll-scene-sticky" variant="panel" amount={0.15} delayChildren={0.08} stagger={0.08}>
        <RevealItem className="home-console-intro" index={0}>
          <HomeSectionHeader
            eyebrow="Guardian Intervention Console"
            title="A assinatura operacional do produto."
            description="Mensagem suspeita, sinais detectados, score de risco, Trust Lock, próxima ação e trilha da decisão em uma visão única para o responsável."
          />
          <Link href="/before-pix" className="home-inline-link">Abrir análise Before Pix</Link>
        </RevealItem>
        <RevealItem className="home-console-shell" index={1}>
          <GuardianInterventionConsole />
        </RevealItem>
      </ScrollScene>

      <RevealGroup as="section" className="home-section home-flow-section" variant="default" amount={0.15} delayChildren={0.1} stagger={0.1}>
        <RevealItem index={0}>
          <HomeSectionHeader
            eyebrow="Como funciona"
            title="Uma trilha simples para quem está em risco. Um console para quem protege."
            description="O Guardian separa a experiência da pessoa protegida da operação do responsável. Simples na ponta, rastreável no console."
          />
        </RevealItem>
        <div className="home-flow home-flow-sequence">
          {flowSteps.map((step,index)=> (
            <RevealItem as="article" key={step.number} className="home-flow-step" index={index + 2}>
              <span>{step.number}</span>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </RevealItem>
          ))}
        </div>
      </RevealGroup>

      <RevealGroup as="section" className="home-section home-case-study" variant="fast" amount={0.15} delayChildren={0.05} stagger={0.08}>
        <div className="home-case-copy">
          <RevealItem as="blockquote" className="home-case-quote" index={0}>
            <p>“Eu só precisava de alguém para me dizer: pare, confirme pelo número salvo.”</p>
            <footer>Dona Lúcia, 72 anos</footer>
          </RevealItem>
          <RevealItem className="home-case-context" index={1}>
            <div className="home-eyebrow">Caso Dona Lúcia</div>
            <h2>Dona Lúcia não precisa entender o golpe sozinha.</h2>
            <p>
              A proteção assistida entra no intervalo entre a pressão da mensagem e a transferência. O sistema reduz velocidade, mostra sinais e coloca o responsável certo no fluxo.
            </p>
          </RevealItem>
          <RevealItem className="home-case-actions" index={8}>
            <Link href="/family-console" className="home-primary-cta">Abrir console</Link>
            <Link href="/chatbot-demo" className="home-secondary-cta">Ver canal simples</Link>
          </RevealItem>
        </div>
        <ol className="home-case-timeline">
          {caseSteps.map((step,index)=> (
            <RevealItem as="li" key={step} index={index + 2}>
              <span>{String(index + 1).padStart(2,'0')}</span>
              <p>{step}</p>
            </RevealItem>
          ))}
        </ol>
      </RevealGroup>

      <RevealGroup as="section" className="home-section home-checklist-section" variant="default" amount={0.15} delayChildren={0.1} stagger={0.09}>
        <RevealItem index={0}>
          <HomeSectionHeader
            eyebrow="Trust Center modules"
            title="Menos painel para a vítima. Mais proteção coordenada para a família."
            description="Os módulos trabalham juntos para pausar risco, orientar verificação, acionar confiança e documentar a decisão."
          />
        </RevealItem>
        <RevealGroup as="div" className="home-module-grid" variant="card" amount={0.1} delayChildren={0.05} stagger={0.08}>
          {productModules.map((module,index)=> (
            <RevealItem
              as="article"
              key={module.title}
              className={`home-module-card home-module-${module.tone} ${index === 0 ? 'home-module-lead' : ''}`}
              index={index}
            >
              <div className="home-module-index">{String(index + 1).padStart(2,'0')}</div>
              <h3>{module.title}</h3>
              <p>{module.body}</p>
            </RevealItem>
          ))}
        </RevealGroup>
      </RevealGroup>

      <RevealGroup as="section" className="home-section home-closing" variant="default" amount={0.15} delayChildren={0.1} stagger={0.09}>
        <RevealItem index={0}>
          <div className="home-eyebrow">Proteção assistida</div>
        </RevealItem>
        <RevealItem index={1}>
          <h2>Uma camada entre a mensagem suspeita e o prejuízo.</h2>
          <p>
            O CyberAlerta Guardian foi desenhado para apoiar pessoas vulneráveis, famílias e instituições antes que a engenharia social vire perda financeira, roubo de credencial ou envio de documento.
          </p>
        </RevealItem>
        <RevealItem className="home-hero-actions" index={2}>
          <Link href="/family-console" className="home-primary-cta">Abrir Guardian Console</Link>
          <Link href="/assisted-demo" className="home-secondary-cta">Ver demonstração completa</Link>
        </RevealItem>
      </RevealGroup>
    </div>
  )
}
