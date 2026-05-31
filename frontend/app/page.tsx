"use client"

import React from 'react'
import Link from 'next/link'
import GuardianInterventionConsole from '@/components/GuardianInterventionConsole'
import HomeGuardianCoreVisual from '@/components/HomeGuardianCoreVisual'
import HomeScrollReveal from '@/components/HomeScrollReveal'

const proofPoints = [
  'Canal simples para a pessoa protegida',
  'Console inteligente para o responsável',
  'Pausa protetiva antes do dano',
]

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
  {
    title:'SafetyPolicy',
    body:'Mantém as respostas defensivas, educativas e seguras, sem ensinar golpes ou expor instruções ofensivas.',
    tone:'safe',
  },
]

const caseSteps = [
  'Dona Lúcia recebe uma mensagem de um falso filho pedindo Pix urgente.',
  'Ela encaminha a mensagem pelo canal simples do Guardian.',
  'O sistema responde com orientação curta: não pagar e confirmar por contato salvo.',
  'O caso chega ao Gabriel no Guardian Console com sinais e risco.',
  'Trust Lock pausa a ação e a verificação segura evita prejuízo.',
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
      <section className="home-hero" aria-label="CyberAlerta Guardian">
        <div className="home-hero-copy">
          <div className="home-product-name">CyberAlerta Guardian</div>
          <div className="home-eyebrow">Proteção antifraude assistida</div>
          <h1>Proteção antes do golpe virar prejuízo.</h1>
          <p className="home-hero-subtitle">
            Uma plataforma de proteção assistida para familiares, cuidadores e instituições protegerem pessoas vulneráveis contra golpes por Pix, WhatsApp, links e engenharia social.
          </p>
          <div className="home-hero-actions">
            <Link href="/assisted-demo" className="home-primary-cta">Ver demonstração</Link>
            <Link href="/family-console" className="home-secondary-cta">Explorar Guardian Console</Link>
          </div>
          <div className="home-proof-strip" aria-label="Pontos de prova">
            {proofPoints.map((point)=> (
              <span key={point}>{point}</span>
            ))}
          </div>
        </div>

        <div className="home-hero-visual">
          <HomeGuardianCoreVisual />
        </div>
      </section>

      <HomeScrollReveal className="home-section">
        <HomeSectionHeader
          eyebrow="Como funciona"
          title="Uma trilha simples para quem está em risco. Um console para quem protege."
          description="O Guardian separa a experiência da pessoa protegida da operação do responsável. Simples na ponta, rastreável no console."
        />
        <div className="home-flow">
          {flowSteps.map((step)=> (
            <article key={step.number} className="home-flow-step">
              <span>{step.number}</span>
              <h3>{step.title}</h3>
              <p>{step.body}</p>
            </article>
          ))}
        </div>
      </HomeScrollReveal>

      <HomeScrollReveal className="home-section home-console-section" delay={80}>
        <div className="home-console-intro">
          <HomeSectionHeader
            eyebrow="Guardian Intervention Console"
            title="A assinatura operacional do produto."
            description="Mensagem suspeita, sinais detectados, score de risco, Trust Lock, próxima ação e trilha da decisão em uma visão única para o responsável."
          />
          <Link href="/before-pix" className="home-inline-link">Abrir análise Before Pix</Link>
        </div>
        <GuardianInterventionConsole />
      </HomeScrollReveal>

      <HomeScrollReveal className="home-section" delay={120}>
        <HomeSectionHeader
          eyebrow="Módulos críticos"
          title="Menos painel para a vítima. Mais proteção coordenada para a família."
          description="Os módulos trabalham juntos para pausar risco, orientar verificação, acionar confiança e documentar a decisão."
        />
        <div className="home-module-grid">
          {productModules.map((module,index)=> (
            <article key={module.title} className={`home-module-card home-module-${module.tone} ${index === 0 ? 'home-module-lead' : ''}`}>
              <div className="home-module-index">{String(index + 1).padStart(2,'0')}</div>
              <h3>{module.title}</h3>
              <p>{module.body}</p>
            </article>
          ))}
        </div>
      </HomeScrollReveal>

      <HomeScrollReveal className="home-section home-case-study" delay={140}>
        <div>
          <div className="home-eyebrow">Caso de uso</div>
          <h2>Dona Lúcia não precisa entender o golpe sozinha.</h2>
          <p>
            A proteção assistida entra no intervalo entre a pressão da mensagem e a transferência. O sistema reduz velocidade, mostra sinais e coloca o responsável certo no fluxo.
          </p>
          <div className="home-case-actions">
            <Link href="/chatbot-demo" className="home-secondary-cta">Ver canal simples</Link>
            <Link href="/family-console" className="home-secondary-cta">Abrir console</Link>
          </div>
        </div>
        <ol className="home-case-timeline">
          {caseSteps.map((step,index)=> (
            <li key={step}>
              <span>{String(index + 1).padStart(2,'0')}</span>
              <p>{step}</p>
            </li>
          ))}
        </ol>
      </HomeScrollReveal>

      <HomeScrollReveal className="home-section home-global-preview" delay={160}>
        <div className="home-global-map" aria-hidden="true">
          <span className="home-map-node home-map-node-a" />
          <span className="home-map-node home-map-node-b" />
          <span className="home-map-node home-map-node-c" />
          <span className="home-map-line home-map-line-a" />
          <span className="home-map-line home-map-line-b" />
        </div>
        <div>
          <div className="home-eyebrow">Visão global</div>
          <h2>Padrões de fraude mudam por região. A pausa protetiva continua a mesma.</h2>
          <p>
            Visualização simulada de padrões de golpe — não é feed real de ataques. A página global mostra como Pix, links, senhas e documentos entram na mesma lógica de prevenção pré-dano.
          </p>
          <Link href="/global" className="home-inline-link">Explorar visão global</Link>
        </div>
      </HomeScrollReveal>

      <HomeScrollReveal className="home-section home-closing" delay={180}>
        <div className="home-eyebrow">Proteção assistida</div>
        <h2>Uma camada entre a mensagem suspeita e o prejuízo.</h2>
        <p>
          O CyberAlerta Guardian foi desenhado para apoiar pessoas vulneráveis, famílias e instituições antes que a engenharia social vire perda financeira, roubo de credencial ou envio de documento.
        </p>
        <div className="home-hero-actions">
          <Link href="/assisted-demo" className="home-primary-cta">Ver demonstração completa</Link>
          <Link href="/family-console" className="home-secondary-cta">Abrir Guardian Console</Link>
        </div>
      </HomeScrollReveal>
    </div>
  )
}
