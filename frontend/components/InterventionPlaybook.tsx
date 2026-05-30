import React from 'react'
import Card from '@/components/Card'

export default function InterventionPlaybook({playbook}:{playbook:{immediate_action:string,verification:string,family_escalation:string,recovery_fallback:string}}){
  return (
    <Card>
      <div className="font-semibold text-lg mb-3">Guia de Intervenção</div>
      <div className="space-y-3 text-sm">
        <div className="border-l-4 border-red-300 pl-3">
          <div className="font-semibold text-red-700">🚨 Ação Imediata</div>
          <div className="text-gray-700 mt-1">{playbook.immediate_action}</div>
        </div>
        <div className="border-l-4 border-blue-300 pl-3">
          <div className="font-semibold text-blue-700">✓ Verificação</div>
          <div className="text-gray-700 mt-1">{playbook.verification}</div>
        </div>
        <div className="border-l-4 border-yellow-300 pl-3">
          <div className="font-semibold text-yellow-700">👥 Informar Família</div>
          <div className="text-gray-700 mt-1">{playbook.family_escalation}</div>
        </div>
        <div className="border-l-4 border-green-300 pl-3">
          <div className="font-semibold text-green-700">🔄 Recuperação</div>
          <div className="text-gray-700 mt-1">{playbook.recovery_fallback}</div>
        </div>
      </div>
    </Card>
  )
}
