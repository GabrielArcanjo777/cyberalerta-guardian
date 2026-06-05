"use client"

import React, {useState} from 'react'
import Link from 'next/link'
import {analyzeMessage} from '@/lib/api'
import TrustLockCard from '@/components/TrustLockCard'
import TrustEvidenceCard from '@/components/TrustEvidenceCard'
import AgentDecisionTrace from '@/components/AgentDecisionTrace'
import ManipulationBadges from '@/components/ManipulationBadges'
import InterventionPlaybook from '@/components/InterventionPlaybook'
import ProofOfTrust from '@/components/ProofOfTrust'
import TrustedCircleAlert from '@/components/TrustedCircleAlert'
import ReportCard from '@/components/ReportCard'
import RiskScore from '@/components/RiskScore'
import FamilyConsole from '@/components/FamilyConsole'
import AIModeIndicator from '@/components/AIModeIndicator'
import MLScamIntelligenceCard from '@/components/MLScamIntelligenceCard'
import Card from '@/components/Card'
import Button from '@/components/Button'
import type {TrustedCircleAlert as TrustedCircleAlertModel} from '@/lib/types'
import {TrustPipeline} from '@/components/AppPrimitives'
import PrivacyConsentChecklist from '@/components/PrivacyConsentChecklist'
import {beforePixPrivacyNotice} from '@/lib/privacyConsent'
import {OperationalTimeline, PageHeader, PageShell, StatusRail} from '@/components/CommandCenter'

const initialMessage = 'Mãe, troquei de número. Meu celular quebrou. Preciso pagar uma conta urgente. Faz um Pix de R$ 780? Não liga agora porque estou em reunião.'

const actionOptions = [
  {value: 'pix', label: 'Pix'},
  {value: 'link', label: 'Link'},
  {value: 'password', label: 'Senha'},
  {value: 'document', label: 'Documento'},
  {value: 'app', label: 'App remoto'},
  {value: 'sms_code', label: 'Código SMS'},
]

function humanize(value:string){
  return value.replace(/_/g, ' ')
}

const fallbackTrustedAlert: TrustedCircleAlertModel = {
  should_alert: false,
  contact_name: 'Gabriel',
  relationship: 'neto',
  urgency: 'low',
  person_at_risk: 'Dona Lúcia',
  risk_summary: 'Nenhum alerta familiar necessário neste momento.',
  scam_type: 'sem golpe crítico confirmado',
  recommended_action: 'Monitore e confirme por outro canal antes de qualquer ação.',
  suggested_message: 'Dona Lúcia, vamos confirmar essa mensagem juntos antes de você agir.',
  status: 'monitoring',
  is_simulated: true,
  message: 'Nenhum alerta familiar necessario neste momento.'
}

export default function BeforePix(){
  const [message,setMessage]=useState(initialMessage)
  const [action,setAction]=useState('pix')
  const [result,setResult]=useState<any>(null)
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState('')

  async function onAnalyze(){
    setLoading(true)
    setError('')
    try{
      const payload = {
        user_name: 'Dona Lúcia',
        age_group: 'elderly',
        trusted_contact_name: 'Gabriel',
        trusted_contact_relation: 'neto',
        action_type: action,
        channel: 'whatsapp',
        message,
        already_acted: false
      }
      const res = await analyzeMessage(payload)
      setResult(res)
    }catch(err:any){
      setError('Erro ao conectar com o servidor. Usando dados de demonstração.')
    }finally{
      setLoading(false)
    }
  }

  const trustedAlert = result?.trusted_circle_alert || {
    ...fallbackTrustedAlert
  }

  function openFamilyConsole(){
    if(typeof window !== 'undefined'){
      window.localStorage.setItem('cyberalerta:lastTrustedCircleAlert', JSON.stringify(trustedAlert))
      window.location.assign('/family-console')
    }
  }

  return (
    <PageShell>
      <PageHeader
        eyebrow="Before Pix command flow"
        title="Antes do Pix"
        description="Análise defensiva do texto que você cola aqui — sem leitura invisível de conversas. Pausa protetiva e trilha para o responsável."
        detail={beforePixPrivacyNotice}
        aside={
          <div className="space-y-5">
            <StatusRail
              items={[
                {label:'Canal', value:'WhatsApp', tone:'neutral'},
                {label:'Contato seguro', value:'Gabriel', tone:'ready'},
                {label:'Ação', value:humanize(action), tone:'warn'},
              ]}
            />
            <OperationalTimeline
              items={[
                {title:'Intent scan ready'},
                {title:'Manipulation analysis ready'},
                {title:'Trust Lock armed'},
                {title:'Proof of Trust ready'},
              ]}
            />
          </div>
        }
      />

      <PrivacyConsentChecklist compact />

      <div className="grid gap-6 lg:grid-cols-[minmax(0,1.08fr)_minmax(320px,0.92fr)]">
        <Card className="overflow-hidden p-0">
          <div className="border-b border-slate-200 px-5 py-4 sm:px-6">
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Mensagem recebida</div>
            <h2 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Análise antes da transferência</h2>
          </div>
          <div className="space-y-5 p-5 sm:p-6">
            <label className="block">
              <span className="mb-2 block text-sm font-bold text-slate-700">Conteúdo da mensagem</span>
              <div className="rounded-lg border border-emerald-100 bg-emerald-50 p-4 shadow-inner">
                <div className="mb-3 flex items-center justify-between gap-3 text-xs font-bold uppercase tracking-wide text-emerald-700">
                  <span>Recebida agora</span>
                  <span>número novo</span>
                </div>
                <textarea
                  value={message}
                  onChange={e=>setMessage(e.target.value)}
                  className="min-h-[170px] w-full resize-y border-0 bg-transparent p-0 text-base leading-7 text-slate-900 placeholder:text-slate-400 focus:outline-none focus:ring-0"
                  aria-label="Mensagem"
                />
              </div>
            </label>

            <div>
              <label className="mb-2 block text-sm font-bold text-slate-700">Tipo de ação perigosa</label>
              <select
                value={action}
                onChange={e=>setAction(e.target.value)}
                className="h-12 w-full rounded-lg border border-slate-200 bg-white px-4 text-sm font-semibold text-slate-800 shadow-sm focus:border-slate-400 focus:outline-none focus:ring-2 focus:ring-slate-200"
              >
                {actionOptions.map((option)=> (
                  <option key={option.value} value={option.value}>{option.label}</option>
                ))}
              </select>
            </div>

            <Button onClick={onAnalyze} disabled={loading} className="h-14 w-full text-base">
              {loading ? 'Analisando...' : 'Analisar com Guardian'}
            </Button>
          </div>
        </Card>

        <div className="space-y-4">
          <Card>
            <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Caso</div>
            <div className="mt-4 flex items-center gap-4">
              <div className="flex h-14 w-14 items-center justify-center rounded-lg bg-slate-950 text-lg font-black text-white">DL</div>
              <div>
                <div className="text-lg font-bold text-slate-950">Dona Lúcia</div>
                <div className="text-sm font-medium text-slate-500">72 anos, ação financeira iminente</div>
              </div>
            </div>
            <div className="mt-5 grid gap-3">
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Pessoa de confiança</div>
                <div className="mt-1 text-sm font-bold text-slate-900">Gabriel, neto</div>
              </div>
              <div className="rounded-lg border border-slate-200 bg-slate-50 p-4">
                <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Estado</div>
                <div className="mt-1 text-sm font-bold text-slate-900">{result ? 'Análise concluída' : 'Aguardando análise'}</div>
              </div>
            </div>
          </Card>

          <Card>
            <TrustPipeline />
          </Card>
        </div>
      </div>

      {error && (
        <Card className="border-amber-200 bg-amber-50">
          <p className="text-sm font-semibold text-amber-800">{error}</p>
        </Card>
      )}

      {result?.__mock && (
        <Card className="border-sky-200 bg-sky-50">
          <p className="text-sm font-semibold text-sky-800">Dados em modo demonstração porque o backend não respondeu.</p>
        </Card>
      )}

      {result ? (
        <>
          <AIModeIndicator mode={result.ai_mode} />
          <div className="grid gap-6 lg:grid-cols-[minmax(280px,0.92fr)_minmax(0,1.55fr)]">
            <aside className="space-y-4 lg:sticky lg:top-6 lg:self-start">
              <RiskScore score={result.risk_score} level={result.risk_level} />
              <TrustLockCard
                activated={result.trust_lock.activated}
                reason={result.trust_lock.reason}
                message={result.trust_lock.message}
              />
              <TrustedCircleAlert alert={trustedAlert} onOpenConsole={openFamilyConsole} />
              <FamilyConsole
                alert={trustedAlert}
                backHref="/before-pix"
                backLabel="Voltar para análise"
              />
            </aside>

            <div className="space-y-4">
              <Card>
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Classificação de ameaça</div>
                <div className="mt-4 grid gap-4 sm:grid-cols-3">
                  <div className="rounded-lg border border-slate-200 bg-slate-50 p-4 sm:col-span-2">
                    <div className="text-xs font-bold uppercase tracking-wide text-slate-400">Tipo de golpe</div>
                    <p className="mt-2 text-lg font-bold leading-6 text-slate-950">{result.scam_type}</p>
                  </div>
                  <div className="rounded-lg border border-red-200 bg-red-50 p-4">
                    <div className="text-xs font-bold uppercase tracking-wide text-red-400">Estagio</div>
                    <p className="mt-2 text-sm font-bold leading-5 text-red-700">{result.scam_stage}</p>
                  </div>
                </div>
              </Card>

              <TrustEvidenceCard
                confidence={result.trust_evidence.confidence}
                evidence={result.trust_evidence.evidence}
              />

              <Card>
                <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Manipulation Badges</div>
                <h3 className="mt-2 text-xl font-bold tracking-tight text-slate-950">Padrões detectados</h3>
                <div className="mt-5">
                  <ManipulationBadges items={result.manipulations} />
                </div>
              </Card>

                <AgentDecisionTrace items={result.agent_decision_trace} decisionLedger={result.decision_ledger} />
              <MLScamIntelligenceCard ml={result.ml_analysis} url={result.url_analysis} />
              <ProofOfTrust items={result.proof_of_trust} />
              <InterventionPlaybook playbook={result.intervention_playbook} />
              <ReportCard report={result.report} />
            </div>
          </div>

          <div className="flex flex-col gap-3 sm:flex-row">
            <Button
              variant="ghost"
              onClick={()=>{
                setResult(null)
                setMessage('')
                setError('')
              }}
            >
              Reiniciar demo
            </Button>
            <Link href="/help-network">
              <Button variant="ghost" className="w-full sm:w-auto">
                Gerar plano de ajuda
              </Button>
            </Link>
            <Button
              variant="ghost"
              onClick={()=>{
                setMessage(initialMessage)
                setAction('pix')
                setResult(null)
                setError('')
              }}
            >
              Restaurar caso principal
            </Button>
          </div>
        </>
      ) : (
        <Card className="border-dashed border-slate-300 bg-slate-50/70">
          <div className="flex flex-col gap-3 sm:flex-row sm:items-center sm:justify-between">
            <div>
              <div className="text-xs font-semibold uppercase tracking-[0.2em] text-slate-500">Output console</div>
              <p className="mt-2 text-lg font-bold text-slate-950">Aguardando primeira análise do Guardian</p>
            </div>
            <div className="rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-bold text-slate-600">
              POST /analyze ready
            </div>
          </div>
        </Card>
      )}
    </PageShell>
  )
}
