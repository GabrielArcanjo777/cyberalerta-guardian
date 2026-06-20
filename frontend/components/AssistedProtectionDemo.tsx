"use client"

import React, {useEffect, useState} from 'react'
import Link from 'next/link'
import Button from '@/components/Button'
import Card from '@/components/Card'
import {AppBadge, AppCardTitle, AppSectionTitle} from '@/components/AppPrimitives'
import {riskStatusClass} from '@/lib/appStatus'
import ProofOfTrustChecklist from '@/components/ProofOfTrustChecklist'
import PrivacyConsentChecklist from '@/components/PrivacyConsentChecklist'
import {assistedDemoPrivacyNotice} from '@/lib/privacyConsent'
import {
  assistedDemoMeta,
  assistedDemoSteps,
  decisionTraceTimeline,
  proofOfTrustChecklist,
  reportPreview,
} from '@/lib/assistedDemoFlow'
import {getGuardianConsoleCase} from '@/lib/api'
import type {AdminCase} from '@/lib/types'

function DemoStep({
  order,
  title,
  children,
  id,
}:{
  order: number
  title: string
  children: React.ReactNode
  id: string
}){
  return (
    <section id={id} className="assisted-demo-step guardian-motion-in scroll-mt-28">
      <div className="assisted-demo-step-head">
        <span className="assisted-demo-step-number">{String(order).padStart(2, '0')}</span>
        <AppSectionTitle className="!mt-0">{title}</AppSectionTitle>
      </div>
      <div className="mt-5">{children}</div>
    </section>
  )
}

export default function AssistedProtectionDemo(){
  const [liveCase,setLiveCase]=useState<AdminCase | null>(null)
  const [backendSynced,setBackendSynced]=useState(false)

  useEffect(()=>{
    getGuardianConsoleCase(assistedDemoMeta.caseId)
      .then(caseData=>{
        setLiveCase(caseData)
        setBackendSynced(!('__mock' in caseData && caseData.__mock))
      })
      .catch(()=>{
        setLiveCase(null)
        setBackendSynced(false)
      })
  },[])

  const meta = {
    ...assistedDemoMeta,
    shortReply: liveCase?.protected_person_short_reply || assistedDemoMeta.shortReply,
    whatsappUserMessage: assistedDemoMeta.whatsappUserMessage,
    whatsappTrustedContactMessage: assistedDemoMeta.whatsappTrustedContactMessage,
    shortExplanation: assistedDemoMeta.shortExplanation,
    nextBestAction: assistedDemoMeta.nextBestAction,
    riskScore: liveCase?.risk_score ?? assistedDemoMeta.riskScore,
    riskLevel: liveCase?.risk_level ?? assistedDemoMeta.riskLevel,
    guardian: liveCase?.guardian_alias ?? assistedDemoMeta.guardian,
  }

  return (
    <div className="assisted-demo space-y-10 pb-8">
      <header className="assisted-demo-hero guardian-page-header card-primary overflow-hidden p-6 sm:p-10">
        <div className="guardian-kicker">Sprint 18G · narrativa completa</div>
        <h1 className="app-page-title mt-5 max-w-3xl">{meta.title}</h1>
        <p className="mt-4 max-w-3xl text-base font-medium leading-7 text-slate-300">{meta.subtitle}</p>
        <p className="app-muted-text mt-4 max-w-2xl text-sm">{assistedDemoPrivacyNotice}</p>
        <div className="mt-6 max-w-4xl">
          <PrivacyConsentChecklist compact />
        </div>
        {backendSynced && (
          <p className="mt-3 text-xs font-medium text-cyan-300/90">Dados do caso demo sincronizados com o backend.</p>
        )}
      </header>

      <section className="assisted-demo-priority">
        <div className="assisted-demo-priority-risk">
          <div className="app-label text-red-200/90">Risco atual</div>
          <div className="mt-3 flex flex-wrap items-end gap-3">
            <span className="guardian-case-risk-score">{meta.riskScore}</span>
            <span className={riskStatusClass(meta.riskLevel)}>{meta.riskLevel}</span>
          </div>
          <p className="mt-3 text-sm font-semibold leading-6 text-red-100/90">
            Pedido de Pix urgente com identidade nao verificada.
          </p>
        </div>

        <div className="assisted-demo-priority-action">
          <div className="app-label text-emerald-200/90">Acao recomendada</div>
          <p className="mt-3 text-lg font-semibold leading-7 text-emerald-50">
            Manter pausa protetiva e confirmar por contato salvo antes de qualquer transferencia.
          </p>
        </div>

        <div className="assisted-demo-priority-evidence">
          <div className="app-label">Evidencias secundarias</div>
          <div className="mt-3 flex flex-wrap gap-2">
            {meta.signals.slice(0, 4).map(signal=> (
              <AppBadge key={signal}>{signal}</AppBadge>
            ))}
          </div>
        </div>
      </section>

      <nav className="assisted-demo-nav sticky top-[4.5rem] z-20 rounded-md border border-white/10 bg-slate-950/90 p-2 backdrop-blur-md">
        <div className="flex gap-1 overflow-x-auto pb-1">
          {assistedDemoSteps.map(step=> (
            <a
              key={step.id}
              href={`#step-${step.id}`}
              className="assisted-demo-nav-pill shrink-0"
            >
              <span className="text-[10px] font-bold text-cyan-300/80">{String(step.order).padStart(2, '0')}</span>
              <span className="mt-0.5 block text-xs font-semibold text-slate-200">{step.label}</span>
            </a>
          ))}
        </div>
      </nav>

      <DemoStep order={1} id="step-suspicious-message" title="Mensagem suspeita">
        <div className="grid gap-6 lg:grid-cols-[1.1fr_0.9fr]">
          <div className="assisted-demo-chat">
            <div className="assisted-demo-chat-header">
              <span className="text-sm font-semibold text-white">WhatsApp mock</span>
              <AppBadge className="app-badge-accent">Risco inicial: aguardando análise</AppBadge>
            </div>
            <div className="assisted-demo-chat-body">
              <div className="assisted-demo-chat-incoming">
                <div className="text-[10px] font-semibold uppercase tracking-wide text-emerald-300/80">Contato desconhecido</div>
                <p className="mt-2 text-sm leading-6 text-emerald-50">{meta.suspiciousMessage}</p>
              </div>
            </div>
          </div>
          <Card>
            <div className="app-label">Pessoa protegida</div>
            <p className="mt-2 text-lg font-semibold text-white">{meta.protectedPerson}</p>
            <dl className="mt-4 space-y-3 text-sm">
              <div>
                <dt className="app-label">Canal</dt>
                <dd className="mt-1 text-slate-200">{meta.channel}</dd>
              </div>
              <div>
                <dt className="app-label">Tipo</dt>
                <dd className="mt-1 text-slate-200">{meta.scamType}</dd>
              </div>
            </dl>
          </Card>
        </div>
      </DemoStep>

      <DemoStep order={2} id="step-forward" title="Encaminhamento ao Guardian">
        <Card className="border-cyan-400/25">
          <div className="flex flex-col gap-4 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="app-label">Passo 2</div>
              <AppCardTitle className="mt-2">{meta.protectedPerson} encaminhou ao CyberAlerta Guardian</AppCardTitle>
              <p className="app-body-text mt-3">{meta.forwardNote}</p>
            </div>
            <div className="assisted-demo-flow-arrow" aria-hidden="true">→</div>
          </div>
          <p className="app-muted-text mt-4 text-sm">
            Consentimento explícito · minimização de dados · nenhum monitoramento de conversas privadas.
          </p>
        </Card>
      </DemoStep>

      <DemoStep order={3} id="step-short-reply" title="Resposta curta do Guardian">
        <div className="assisted-demo-chat max-w-2xl">
          <div className="assisted-demo-chat-header">
            <span className="text-sm font-semibold text-white">Guardian — resposta à pessoa protegida</span>
          </div>
          <div className="assisted-demo-chat-body">
            <div className="assisted-demo-chat-outgoing">
              <div className="text-[10px] font-semibold uppercase tracking-wide text-cyan-300/80">Guardian</div>
              <p className="mt-2 text-sm leading-6 text-cyan-50">{meta.shortReply}</p>
            </div>
          </div>
        </div>
        <p className="app-muted-text mt-4 max-w-2xl text-sm">
          Linguagem simples, tom calmo, sem jargão técnico — máximo duas frases (Protected Person Response Agent).
        </p>
        <div className="mt-5 grid gap-4 lg:grid-cols-2">
          <div className="app-action-panel border-cyan-400/20">
            <div className="app-label text-cyan-200/90">WhatsApp para pessoa protegida</div>
            <p className="mt-2 text-sm font-medium leading-6 text-cyan-50">{meta.whatsappUserMessage}</p>
          </div>
          <div className="app-action-panel border-emerald-400/20">
            <div className="app-label text-emerald-200/90">WhatsApp para contato de confianca</div>
            <p className="mt-2 text-sm font-medium leading-6 text-emerald-50">{meta.whatsappTrustedContactMessage}</p>
          </div>
          <div className="app-action-panel">
            <div className="app-label">Explicacao curta</div>
            <p className="app-body-text mt-2 text-sm">{meta.shortExplanation}</p>
          </div>
          <div className="app-action-panel">
            <div className="app-label">Proximo passo</div>
            <p className="app-body-text mt-2 text-sm font-semibold text-white">{meta.nextBestAction}</p>
          </div>
        </div>
      </DemoStep>

      <DemoStep order={4} id="step-console-case" title="Caso criado no painel">
        <div className="assisted-demo-console-preview">
          <div className="assisted-demo-console-header">
            <div>
              <div className="app-label text-cyan-300/90">Guardian Console · preview</div>
              <AppCardTitle className="mt-2">Caso para o responsável</AppCardTitle>
            </div>
            <span className={riskStatusClass(meta.riskLevel)}>{meta.riskLevel}</span>
          </div>
          <div className="mt-5 grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
            <div className="app-action-panel">
              <div className="app-label">Pessoa protegida</div>
              <p className="mt-1 font-semibold text-white">{meta.protectedPerson}</p>
            </div>
            <div className="app-action-panel">
              <div className="app-label">Responsável</div>
              <p className="mt-1 font-semibold text-white">{meta.guardian}</p>
            </div>
            <div className="app-action-panel">
              <div className="app-label">Score</div>
              <p className="mt-1 text-2xl font-semibold text-white">{meta.riskScore}<span className="text-sm text-slate-400">/100</span></p>
            </div>
          </div>
          <div className="mt-4 grid gap-4 lg:grid-cols-2">
            <div className="app-action-panel">
              <div className="app-label">Categoria</div>
              <p className="mt-1 font-semibold text-white">{meta.scamCategory}</p>
            </div>
            <div className="app-action-panel">
              <div className="app-label">ID do caso</div>
              <p className="mt-1 font-mono text-xs text-slate-300">{liveCase?.case_id || meta.caseId}</p>
            </div>
          </div>
          <div className="mt-4">
            <div className="app-label">Sinais detectados</div>
            <div className="mt-2 flex flex-wrap gap-2">
              {meta.signals.map(signal=> (
                <AppBadge key={signal}>{signal}</AppBadge>
              ))}
            </div>
          </div>
        </div>
      </DemoStep>

      <DemoStep order={5} id="step-trust-lock" title="Trust Lock — pausa protetiva">
        <Card className="card-danger border-red-400/30 bg-gradient-to-br from-red-950/40 to-slate-950/80">
          <div className="flex items-start gap-4">
            <div className="assisted-demo-lock-icon" aria-hidden="true">⏸</div>
            <div>
              <AppCardTitle className="text-red-100">{meta.trustLockTitle}</AppCardTitle>
              <p className="app-body-text mt-3">{meta.trustLockBody}</p>
              <p className="mt-4 text-sm font-semibold text-red-200/90">
                Pausa protetiva ativada antes de qualquer transferência.
              </p>
            </div>
          </div>
        </Card>
      </DemoStep>

      <DemoStep order={6} id="step-trusted-circle" title="Círculo de confiança">
        <Card className="card-risk border-amber-400/25">
          <div className="app-label text-amber-200/90">Escalonamento simulado</div>
          <p className="mt-3 text-lg font-semibold text-white">{meta.trustedCircleNote}</p>
          <div className="mt-4 app-action-panel border-amber-400/15">
            <div className="app-label">Mensagem sugerida</div>
            <p className="mt-2 text-sm font-medium text-amber-50">
              {meta.protectedPerson} recebeu uma mensagem com pedido de Pix urgente. Verifique antes de qualquer
              transferência.
            </p>
          </div>
          <p className="app-muted-text mt-3">{meta.trustedCircleDisclaimer}</p>
          <p className="mt-3 text-xs font-semibold uppercase tracking-wide text-amber-200/80">
            Nenhuma notificação real foi enviada no MVP
          </p>
          <div className="mt-4 app-action-panel">
            <p className="text-sm text-slate-300">
              O responsável <strong className="text-white">{meta.guardian}</strong> opera o Guardian Console — a pessoa
              protegida não usa painel complexo.
            </p>
          </div>
        </Card>
      </DemoStep>

      <DemoStep order={7} id="step-proof-of-trust" title="Verificação segura">
        <Card className="card-action border-emerald-400/20">
          <ProofOfTrustChecklist
            steps={proofOfTrustChecklist}
            currentStepId="confirm_independent_channel"
            subtitle="O responsável conduz o protocolo no Guardian Console — a pessoa protegida não precisa operar checklist complexo."
          />
          <p className="app-muted-text mt-4 text-sm">
            Liberar somente após confirmação por canal independente. Sem consulta a banco, governo ou CPF real.
          </p>
          <p className="mt-2 text-xs font-semibold uppercase tracking-wide text-emerald-200/70">
            Decisão registrada · manter pausa protetiva se inconclusivo
          </p>
        </Card>
      </DemoStep>

      <DemoStep order={8} id="step-decision-trace" title="Agent Decision Trace">
        <Card className="card-evidence">
          <div className="app-label">Trilha da decisão · auditável</div>
          <ol className="guardian-operational-timeline mt-5">
            {decisionTraceTimeline.map((item,index)=> (
              <li key={item.step} className="guardian-timeline-item">
                <span className="guardian-timeline-index">{String(index + 1).padStart(2, '0')}</span>
                <div>
                  <div className="text-sm font-semibold text-white">{item.step}</div>
                  <p className="mt-1 text-sm leading-6 text-slate-400">{item.detail}</p>
                </div>
              </li>
            ))}
          </ol>
        </Card>
      </DemoStep>

      <DemoStep order={9} id="step-report" title="Relatório">
        <div className="assisted-demo-report">
          <div className="app-label">Preview do relatório</div>
          <AppCardTitle className="mt-2">{reportPreview.title}</AppCardTitle>
          <dl className="mt-5 grid gap-4 sm:grid-cols-2">
            {[
              ['Resumo', reportPreview.summary],
              ['Risco', reportPreview.risk],
              ['Sinais', reportPreview.signals],
              ['Ação tomada', reportPreview.actionTaken],
              ['Recomendação', reportPreview.recommendation],
              ['Status final', reportPreview.finalStatus],
            ].map(([label,value])=> (
              <div key={label} className="app-action-panel sm:col-span-2 lg:col-span-1">
                <dt className="app-label">{label}</dt>
                <dd className="app-body-text mt-2">{value}</dd>
              </div>
            ))}
          </dl>
        </div>
      </DemoStep>

      <section className="assisted-demo-cta guardian-page-header card-primary p-6 sm:p-10">
        <AppSectionTitle>Próximos passos na demo</AppSectionTitle>
        <p className="app-muted-text mt-3 max-w-2xl">
          Explore cada módulo do produto com os mesmos dados simulados — ideal para hackathon, clientes e portfolio.
        </p>
        <div className="mt-6 grid gap-3 sm:grid-cols-2 lg:grid-cols-4">
          <Link href="/family-console"><Button className="h-12 w-full">Abrir Guardian Console</Button></Link>
          <Link href="/chatbot-demo"><Button variant="ghost" className="h-12 w-full">Testar canal simples</Button></Link>
          <Link href="/report"><Button variant="ghost" className="h-12 w-full">Ver relatório</Button></Link>
          <Link href="/trust-center"><Button variant="ghost" className="h-12 w-full">Ver Trust Center</Button></Link>
        </div>
      </section>
    </div>
  )
}
