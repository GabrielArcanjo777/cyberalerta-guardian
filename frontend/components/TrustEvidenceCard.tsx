import React from 'react'
import Card from '@/components/Card'

export default function TrustEvidenceCard({confidence,evidence}:{confidence:number,evidence:string[]}){
  return (
    <Card>
      <div className="font-semibold text-lg">Evidências de confiabilidade</div>
      <div className="text-sm text-gray-600 mt-1">Confiança: <span className="font-bold text-gray-900">{confidence}%</span></div>
      <ul className="mt-3 space-y-2">
        {evidence.map((e,i)=> (
          <li key={i} className="text-sm text-gray-700 flex items-start">
            <span className="mr-2">✓</span>
            <span>{e}</span>
          </li>
        ))}
      </ul>
    </Card>
  )
}
