"use client"

import React, {useState} from 'react'
import Link from 'next/link'

type DemoCase = {
  id: string
  label: string
  message: string
  origin: string
  signals: string[]
  risk: 'HIGH' | 'MED' | 'LOW'
  trustLock: string
  action: string
  recommendation: string
  audit: string
  terminal: string[]
}

const DEMO_CASES: DemoCase[] = [
  {
    id: 'pix-urgente',
    label: 'Pix urgente com número novo',
    message: 'Mãe, troquei de número. Preciso fazer um Pix urgente. Não liga agora.',
    origin: 'Número desconhecido',
    signals: ['número novo', 'urgência financeira', 'pedido para não ligar', 'pressão emocional'],
    risk: 'HIGH',
    trustLock: 'ACTIVE',
    action: 'PAUSE RESPONSE',
    recommendation: 'Confirmar com contato salvo antes de qualquer pagamento.',
    audit: 'Decisão registrada na trilha de auditoria.',
    terminal: [
      '[INPUT] mensagem suspeita recebida',
      '[SIGNAL] número novo detectado',
      '[SIGNAL] urgência financeira detectada',
      '[RISK] severidade alta',
      '[TRUST_LOCK] resposta pausada',
      '[ACTION] confirmar com contato salvo',
      '[AUDIT] decisão registrada localmente',
      '[ALERT] contato de confiança notificado',
      '[CONSOLE] caso registrado para revisão',
    ],
  },
  {
    id: 'falso-banco',
    label: 'Falso banco pedindo código',
    message: 'Banco XYZ: seu cartão foi bloqueado. Responda com o código recebido por SMS para desbloquear.',
    origin: 'Número desconhecido',
    signals: ['instituição financeira', 'pedido de código/senso', 'urgência falsa', 'link curto suspeito'],
    risk: 'HIGH',
    trustLock: 'ACTIVE',
    action: 'DO NOT SHARE',
    recommendation: 'Nunca compartilhe códigos. Fale com o banco pelo app oficial ou telefone salvo.',
    audit: 'Decisão registrada na trilha de auditoria.',
    terminal: [
      '[INPUT] mensagem suspeita recebida',
      '[SIGNAL] instituição financeira detectada',
      '[SIGNAL] pedido de código/senha detectado',
      '[RISK] severidade alta',
      '[TRUST_LOCK] resposta pausada',
      '[ACTION] não compartilhar códigos',
      '[AUDIT] decisão registrada localmente',
      '[ALERT] contato de confiança notificado',
      '[CONSOLE] caso registrado para revisão',
    ],
  },
  {
    id: 'link-suspeito',
    label: 'Link suspeito de entrega ou benefício',
    message: 'Parabéns! Você ganhou um benefício. Clique aqui para resgatar: bit.ly/xyz123',
    origin: 'Número desconhecido',
    signals: ['oferta inesperada', 'link curto', 'urgência implícita', 'remetente desconhecido'],
    risk: 'MED',
    trustLock: 'STANDBY',
    action: 'DO NOT CLICK',
    recommendation: 'Não clique em links suspeitos. Verifique pelo site oficial ou contato conhecido.',
    audit: 'Decisão registrada na trilha de auditoria.',
    terminal: [
      '[INPUT] mensagem suspeita recebida',
      '[SIGNAL] oferta inesperada detectada',
      '[SIGNAL] link curto suspeito detectado',
      '[RISK] severidade média',
      '[TRUST_LINK] modo standby',
      '[ACTION] não clicar no link',
      '[AUDIT] decisão registrada localmente',
      '[ALERT] contato de confiança notificado',
      '[CONSOLE] caso registrado para revisão',
    ],
  },
]

const RISK_COLORS: Record<DemoCase['risk'], string> = {
  HIGH: 'guardian-demo-risk-high',
  MED: 'guardian-demo-risk-med',
  LOW: 'guardian-demo-risk-low',
}

export default function AssistedProtectionDemo(){
  const [caseIndex, setCaseIndex] = useState(0)
  const current = DEMO_CASES[caseIndex]

  function simulateAnother(){
    setCaseIndex(prev => (prev + 1) % DEMO_CASES.length)
  }

  return (
    <div className="guardian-demo-page">
      <div className="guardian-demo-grid" aria-hidden="true" />
      <div className="guardian-demo-glow guardian-demo-glow-a" aria-hidden="true" />
      <div className="guardian-demo-glow guardian-demo-glow-b" aria-hidden="true" />

      <section className="guardian-demo-shell">
        <div className="guardian-demo-header">
          <span className="guardian-demo-eyebrow">
            <span className="guardian-demo-eyebrow-dot" />
            DEMO DE PROTEÇÃO ASSISTIDA
          </span>
          <h1 className="guardian-demo-title">Veja como uma mensagem suspeita vira uma decisão rastreável antes do dano.</h1>
          <p className="guardian-demo-subtitle">
            Simulação local com dados demonstrativos. O bot analisa a mensagem, alerta o contato de confiança e registra o caso no console — nunca responde ao remetente. Sem envio real via WhatsApp.
          </p>
        </div>

        <div className="guardian-demo-steps">
          <div className="guardian-demo-step-header">
            <span className="guardian-demo-step-number">01</span>
            <h2 className="guardian-demo-step-title">Mensagem recebida</h2>
          </div>
          <div className="guardian-demo-step-grid">
            <div className="guardian-demo-phone">
              <div className="guardian-demo-phone-frame">
                <div className="guardian-demo-phone-notch" />
                <div className="guardian-demo-phone-screen">
                  <div className="guardian-demo-phone-status">
                    <span>14:22</span>
                    <span>●●●○○</span>
                  </div>
                  <div className="guardian-demo-phone-chat-header">
                    <div className="guardian-demo-phone-avatar" />
                    <div>
                      <div className="guardian-demo-phone-contact">Desconhecido</div>
                      <div className="guardian-demo-phone-number">{current.origin}</div>
                    </div>
                  </div>
                  <div className="guardian-demo-phone-chat-body">
                    <div className="guardian-demo-phone-bubble">
                      {current.message}
                      <span className="guardian-demo-phone-time">14:22</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <div className="guardian-demo-signals">
              <div className="guardian-demo-signals-header">
                <span className="guardian-demo-signals-label">Sinais detectados</span>
                <span className="guardian-demo-signals-count">{current.signals.length}</span>
              </div>
              <div className="guardian-demo-signals-list">
                {current.signals.map(signal => (
                  <span key={signal} className="guardian-demo-signal">{signal}</span>
                ))}
              </div>
            </div>
          </div>
        </div>

        <div className="guardian-demo-steps">
          <div className="guardian-demo-step-header">
            <span className="guardian-demo-step-number">02</span>
            <h2 className="guardian-demo-step-title">Análise do Guardian</h2>
          </div>
          <div className="guardian-demo-analysis">
            <div className="guardian-demo-hud">
              <div className="guardian-demo-hud-header">SYS_EVAL</div>
              <div className="guardian-demo-hud-row">
                <span className="guardian-demo-hud-label">RISK</span>
                <span className={`guardian-demo-hud-value ${RISK_COLORS[current.risk]}`}>{current.risk}</span>
              </div>
              <div className="guardian-demo-hud-row">
                <span className="guardian-demo-hud-label">TRUST LOCK</span>
                <span className="guardian-demo-hud-value guardian-demo-hud-value-ok">{current.trustLock}</span>
              </div>
              <div className="guardian-demo-hud-row">
                <span className="guardian-demo-hud-label">ACTION</span>
                <span className="guardian-demo-hud-value guardian-demo-hud-value-warn">{current.action}</span>
              </div>
              <div className="guardian-demo-hud-row">
                <span className="guardian-demo-hud-label">RECOMMEND</span>
                <span className="guardian-demo-hud-value guardian-demo-hud-value-safe">{current.recommendation.split(' ').slice(0, 4).join(' ')}</span>
              </div>
            </div>

            <div className="guardian-demo-explanation">
              <p className="guardian-demo-explanation-text">
                O Guardian detecta padrões comuns de golpe e pausa a ação antes da transferência.
              </p>
              <div className="guardian-demo-explanation-trace">
                <div className="guardian-demo-trace-line">
                  <span className="guardian-demo-trace-dot guardian-demo-trace-dot-1" />
                  <span className="guardian-demo-trace-label">INPUT</span>
                  <span className="guardian-demo-trace-msg">mensagem recebida</span>
                </div>
                <div className="guardian-demo-trace-line">
                  <span className="guardian-demo-trace-dot guardian-demo-trace-dot-2" />
                  <span className="guardian-demo-trace-label">SIGNAL</span>
                  <span className="guardian-demo-trace-msg">{current.signals[0]}</span>
                </div>
                <div className="guardian-demo-trace-line">
                  <span className="guardian-demo-trace-dot guardian-demo-trace-dot-3" />
                  <span className="guardian-demo-trace-label">RISK</span>
                  <span className="guardian-demo-trace-msg">severidade {current.risk === 'HIGH' ? 'alta' : current.risk === 'MED' ? 'média' : 'baixa'}</span>
                </div>
                <div className="guardian-demo-trace-line">
                  <span className="guardian-demo-trace-dot guardian-demo-trace-dot-4" />
                  <span className="guardian-demo-trace-label">ACTION</span>
                  <span className="guardian-demo-trace-msg">{current.action}</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="guardian-demo-steps">
          <div className="guardian-demo-step-header">
            <span className="guardian-demo-step-number">03</span>
            <h2 className="guardian-demo-step-title">Alerta ao contato de confiança</h2>
          </div>
          <div className="guardian-demo-action">
            <div className="guardian-demo-action-main">
              <div className="guardian-demo-action-label">Enviado ao contato de confiança + registrado no console</div>
              <p className="guardian-demo-action-text">{current.recommendation}</p>
              <div className="guardian-demo-action-status">
                <span className="guardian-demo-action-status-dot" />
                <span>{current.audit} O bot não responde ao remetente.</span>
              </div>
            </div>

            <div className="guardian-demo-terminal">
              <div className="guardian-demo-terminal-header">
                <div className="guardian-demo-terminal-dots">
                  <span className="guardian-demo-terminal-dot guardian-demo-terminal-dot-red" />
                  <span className="guardian-demo-terminal-dot guardian-demo-terminal-dot-yellow" />
                  <span className="guardian-demo-terminal-dot guardian-demo-terminal-dot-green" />
                </div>
                <span className="guardian-demo-terminal-title">guardian — demo local</span>
                <span className="guardian-demo-terminal-badge">LIVE_SYS_EVAL</span>
              </div>
              <div className="guardian-demo-terminal-body">
                {current.terminal.map((line, i) => (
                  <div key={i} className="guardian-demo-terminal-line">
                    <span className="guardian-demo-terminal-text">{line}</span>
                  </div>
                ))}
                <div className="guardian-demo-terminal-line guardian-demo-terminal-line-prompt">
                  <span className="guardian-demo-terminal-prompt">$</span>
                  <span className="guardian-demo-terminal-cursor">_</span>
                </div>
              </div>
            </div>
          </div>
        </div>

        <div className="guardian-demo-case-switcher">
          <div className="guardian-demo-case-tabs">
            {DEMO_CASES.map((c, i) => (
              <button
                key={c.id}
                type="button"
                onClick={() => setCaseIndex(i)}
                className={`guardian-demo-case-tab ${i === caseIndex ? 'is-active' : ''}`}
              >
                <span className="guardian-demo-case-tab-label">{c.label}</span>
                <span className={`guardian-demo-case-tab-risk ${RISK_COLORS[c.risk]}`}>{c.risk}</span>
              </button>
            ))}
          </div>
          <button type="button" onClick={simulateAnother} className="guardian-demo-simulate-btn">
            Simular outro caso
          </button>
        </div>

        <div className="guardian-demo-closing">
          <p className="guardian-demo-closing-text">
            Essa demonstração é local. O canal real de WhatsApp usa a Evolution API (WhatsApp Web, não-oficial) e pode ser pareado em /whatsapp-setup.
          </p>
          <div className="guardian-demo-closing-actions">
            <Link href="/login" className="guardian-demo-cta-primary">Entrar no painel</Link>
            <Link href="/" className="guardian-demo-cta-secondary">Voltar para início</Link>
          </div>
        </div>
      </section>
    </div>
  )
}
