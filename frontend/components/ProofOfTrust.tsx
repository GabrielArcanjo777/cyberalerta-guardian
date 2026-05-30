import React from 'react'
import Card from '@/components/Card'

export default function ProofOfTrust({items}:{items:string[]}){
  return (
    <Card>
      <div className="font-semibold text-lg mb-3">Passos de Verificação</div>
      <div className="space-y-2">
        {items.map((it,i)=> (
          <div key={i} className="text-sm flex items-start">
            <span className="font-bold text-blue-600 mr-2">{i+1}.</span>
            <span className="text-gray-700">{it}</span>
          </div>
        ))}
      </div>
    </Card>
  )
}
