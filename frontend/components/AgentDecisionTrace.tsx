import React from 'react'
import Card from '@/components/Card'

export default function AgentDecisionTrace({items}:{items:{agent:string,decision:string}[]}){
  return (
    <Card>
      <div className="font-semibold text-lg mb-3">Sequência de análise</div>
      <div className="space-y-2">
        {items.map((it,i)=> (
          <div key={i} className="text-sm border-l-4 border-blue-300 pl-3 py-1">
            <span className="font-semibold text-blue-700">{it.agent}</span>
            <span className="text-gray-600">: {it.decision}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}
