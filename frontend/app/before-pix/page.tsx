"use client"
import React, {useState} from 'react'
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
import Card from '@/components/Card'
import Button from '@/components/Button'

export default function BeforePix(){
  const [message,setMessage]=useState('Mae, troquei de numero. Meu celular quebrou. Preciso pagar uma conta urgente. Faz um Pix de R$ 780? Nao liga agora porque estou em reuniao.')
  const [action,setAction]=useState('pix')
  const [result,setResult]=useState<any>(null)
  const [loading,setLoading]=useState(false)
  const [error,setError]=useState('')

  async function onAnalyze(){
    setLoading(true)
    setError('')
    try{
      const payload = {
        user_name: 'Dona Lucia',
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

  return (
    <main>
      <div className="mb-8">
        <h1 className="text-3xl font-bold">Antes do Pix</h1>
        <p className="text-gray-600 mt-2">Caso principal: Dona Lucia (72 anos)</p>
      </div>

      <Card className="mb-6">
        <div className="mb-4">
          <label className="block text-sm font-semibold mb-2">Mensagem</label>
          <textarea 
            value={message} 
            onChange={e=>setMessage(e.target.value)} 
            className="w-full p-3 border border-gray-200 rounded-lg focus:ring-2 focus:ring-blue-400 focus:border-transparent" 
            rows={6} 
            aria-label="Mensagem" 
          />
        </div>

        <div className="mb-4 flex gap-4 items-end">
          <div className="flex-1">
            <label className="block text-sm font-semibold mb-2">Tipo de ação perigosa</label>
            <select 
              value={action} 
              onChange={e=>setAction(e.target.value)} 
              className="w-full p-3 border border-gray-200 rounded-lg"
            >
              <option value="pix">Pix</option>
              <option value="link">Link</option>
              <option value="password">Senha</option>
              <option value="document">Documento</option>
              <option value="app">App remoto</option>
              <option value="sms_code">Código SMS</option>
            </select>
          </div>
          <Button onClick={onAnalyze} disabled={loading}>
            {loading ? 'Analisando...' : 'Analisar com Guardian'}
          </Button>
        </div>
      </Card>

      {error && (
        <Card className="mb-6 bg-yellow-50 border-l-4 border-yellow-300">
          <p className="text-yellow-800">{error}</p>
        </Card>
      )}

      {result && (
        <>
          {result.__mock && (
            <Card className="mb-4 bg-blue-50">
              <p className="text-sm text-blue-800">ℹ️ Dados em modo demonstração (backend indisponível)</p>
            </Card>
          )}

          <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
            <div className="space-y-4">
              <RiskScore score={result.risk_score} level={result.risk_level} />
              <TrustLockCard 
                activated={result.trust_lock.activated} 
                reason={result.trust_lock.reason} 
                message={result.trust_lock.message} 
              />
              <TrustedCircleAlert alert={result.trusted_circle_alert} />
            </div>

            <div className="md:col-span-2 space-y-4">
              <Card>
                <div className="mb-2">
                  <h3 className="font-semibold">Tipo de Golpe</h3>
                  <p className="text-sm text-gray-700 mt-1">{result.scam_type}</p>
                </div>
                <div>
                  <h4 className="font-semibold text-sm">Estágio</h4>
                  <p className="text-sm text-gray-700">{result.scam_stage}</p>
                </div>
              </Card>

              <TrustEvidenceCard 
                confidence={result.trust_evidence.confidence} 
                evidence={result.trust_evidence.evidence} 
              />

              <Card>
                <h4 className="font-semibold mb-2">Manipulações detectadas</h4>
                <ManipulationBadges items={result.manipulations} />
              </Card>

              <AgentDecisionTrace items={result.agent_decision_trace} />
              <InterventionPlaybook playbook={result.intervention_playbook} />
              <ProofOfTrust items={result.proof_of_trust} />
              <ReportCard report={result.report} />
            </div>
          </div>

          <div className="flex gap-3 mt-6">
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
            <Button 
              variant="ghost"
              onClick={()=>{
                setMessage('Mae, troquei de numero. Meu celular quebrou. Preciso pagar uma conta urgente. Faz um Pix de R$ 780? Nao liga agora porque estou em reuniao.')
                setAction('pix')
                setResult(null)
              }}
            >
              Testar outro cenário
            </Button>
          </div>
        </>
      )}
    </main>
  )
}
