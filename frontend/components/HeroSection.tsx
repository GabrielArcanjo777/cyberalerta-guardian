"use client"

import React from 'react'
import Link from 'next/link'
import FloatingCard from '@/components/FloatingCard'

const trustItems = [
  'Proteção 24/7',
  'Privacidade por design',
  'Conformidade LGPD',
  'Confiança verificável',
]

function ShieldIcon(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3.2 5.2 5.9v5.2c0 4.5 2.8 8 6.8 9.7 4-1.7 6.8-5.2 6.8-9.7V5.9L12 3.2Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="m9 12.2 2.1 2.1 4.8-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function PlayIcon(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <circle cx="12" cy="12" r="8.5" fill="none" stroke="currentColor" strokeWidth="1.7" />
      <path d="m10.3 8.8 5.3 3.2-5.3 3.2V8.8Z" fill="currentColor" />
    </svg>
  )
}

function ElderSilhouette(){
  return (
    <svg
      className="hero-silhouette-svg"
      viewBox="0 0 200 340"
      width="200"
      height="340"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      role="img"
      aria-label="Silhueta de pessoa idosa segurando um celular"
    >
      <ellipse cx="100" cy="200" rx="70" ry="90" fill="rgba(13,148,136,0.06)" />

      <ellipse cx="100" cy="72" rx="34" ry="38" fill="#1e2535" stroke="#0d9488" strokeWidth="0.8" strokeOpacity="0.4" />

      <path d="M66 62 Q68 30 100 28 Q132 30 134 62 Q120 48 100 46 Q80 48 66 62Z" fill="#3a3f52" />

      <rect x="92" y="108" width="16" height="18" rx="4" fill="#1e2535" />

      <path d="M38 160 Q42 125 100 122 Q158 125 162 160 L166 260 Q134 270 100 270 Q66 270 34 260Z" fill="#151b2a" stroke="#0d9488" strokeWidth="0.6" strokeOpacity="0.3" />

      <path d="M155 148 Q172 168 168 220" stroke="#1e2535" strokeWidth="22" strokeLinecap="round" fill="none" />
      <path d="M155 148 Q172 168 168 220" stroke="#252d3d" strokeWidth="18" strokeLinecap="round" fill="none" />

      <ellipse cx="166" cy="228" rx="11" ry="9" fill="#1e2535" stroke="#0d9488" strokeWidth="0.5" strokeOpacity="0.4" />

      <rect x="152" y="230" width="30" height="52" rx="5" fill="#0f172a" stroke="#0d9488" strokeWidth="1.2" />
      <rect x="156" y="235" width="22" height="38" rx="3" fill="#0d2435" />
      <rect x="156" y="235" width="22" height="38" rx="3" fill="url(#heroScreenGlow)" opacity="0.6" />

      <rect x="159" y="242" width="16" height="2" rx="1" fill="#0d9488" opacity="0.7" />
      <rect x="159" y="248" width="13" height="2" rx="1" fill="#94a3b8" opacity="0.5" />
      <rect x="159" y="254" width="15" height="2" rx="1" fill="#94a3b8" opacity="0.4" />
      <rect x="159" y="262" width="10" height="6" rx="2" fill="#dc2626" opacity="0.6" />

      <ellipse cx="130" cy="130" rx="40" ry="50" fill="rgba(13,148,136,0.04)" />

      <defs>
        <radialGradient id="heroScreenGlow" cx="50%" cy="50%" r="50%">
          <stop offset="0%" stopColor="#0d9488" stopOpacity="0.3" />
          <stop offset="100%" stopColor="#0d9488" stopOpacity="0" />
        </radialGradient>
      </defs>
    </svg>
  )
}

export default function HeroSection(){
  return (
    <section className="human-hero min-h-screen flex items-center" aria-label="CyberAlerta Guardian">
      <div className="human-hero-inner">
        <div className="human-hero-copy">
          <div className="human-hero-badge home-hero-reveal" style={{'--hero-reveal-delay':'0s'} as React.CSSProperties}>
            Proteção assistida
          </div>
          <h1 className="home-hero-reveal" style={{'--hero-reveal-delay':'0.08s'} as React.CSSProperties}>
            Proteção antes do golpe virar <span>prejuízo.</span>
          </h1>
          <p className="human-hero-subtitle home-hero-reveal" style={{'--hero-reveal-delay':'0.16s'} as React.CSSProperties}>
            Uma camada de proteção assistida para famílias, cuidadores e instituições pausarem golpes por Pix, WhatsApp, links e engenharia social antes do dano.
          </p>
          <div className="human-hero-actions home-hero-reveal" style={{'--hero-reveal-delay':'0.24s'} as React.CSSProperties}>
            <Link href="/family-console" className="human-hero-primary">
              <ShieldIcon />
              Abrir Guardian Console
            </Link>
            <Link href="/assisted-demo" className="human-hero-secondary">
              <PlayIcon />
              Ver demonstração
            </Link>
          </div>
          <div className="human-hero-trust home-hero-reveal" style={{'--hero-reveal-delay':'0.32s'} as React.CSSProperties} aria-label="Sinais de confiança">
            {trustItems.map((item,index)=> (
              <React.Fragment key={item}>
                <span>
                  <ShieldIcon />
                  {item}
                </span>
                {index < trustItems.length - 1 && <i aria-hidden="true">·</i>}
              </React.Fragment>
            ))}
          </div>
        </div>

        <div className="human-hero-visual-zone" aria-label="Fluxo de proteção assistida">
          <div className="hero-scene-stage">
            <svg className="hero-connector-lines" viewBox="0 0 620 460" aria-hidden="true">
              <path className="hero-connector-line hero-connector-line-1" d="M400 392 C430 238 438 142 456 122" />
              <path className="hero-connector-line hero-connector-line-2" d="M402 392 C430 318 438 242 456 232" />
              <path className="hero-connector-line hero-connector-line-3" d="M398 396 C428 380 438 354 456 342" />
            </svg>

            <div className="hero-silhouette-wrap">
              <ElderSilhouette />
            </div>

            <div className="hero-floating-card-stack">
              <FloatingCard
                title="MENSAGEM SUSPEITA"
                icon="warning"
                tone="danger"
                lines={['Pedido de Pix urgente', 'RISCO ALTO']}
                className="floating-card-pipeline"
                style={{'--pipeline-delay':'0.7s'} as React.CSSProperties}
              />
              <FloatingCard
                title="GUARDIAN INTERCEPTA"
                icon="shield"
                lines={['Análise em tempo real', 'Ação pausada']}
                className="floating-card-pipeline"
                style={{'--pipeline-delay':'0.9s'} as React.CSSProperties}
              />
              <FloatingCard
                title="RESPONSÁVEL NOTIFICADO"
                icon="users"
                tone="safe"
                lines={['Responsável notificado', 'Caso registrado']}
                className="floating-card-pipeline"
                style={{'--pipeline-delay':'1.1s'} as React.CSSProperties}
              />
            </div>
          </div>
        </div>
      </div>
    </section>
  )
}
