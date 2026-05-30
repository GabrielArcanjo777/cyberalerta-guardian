import React from 'react'

export default function ManipulationBadges({items}:{items:string[]}){
  const badgeColors: {[key:string]: string} = {
    'urgencia': 'bg-red-100 text-red-800 border-red-300',
    'vinculo_familiar': 'bg-blue-100 text-blue-800 border-blue-300',
    'numero_novo': 'bg-yellow-100 text-yellow-800 border-yellow-300',
    'pedido_financeiro': 'bg-purple-100 text-purple-800 border-purple-300',
    'pedido_para_nao_ligar': 'bg-orange-100 text-orange-800 border-orange-300',
    'promessa_financeira': 'bg-pink-100 text-pink-800 border-pink-300',
  }
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((m,i)=> {
        const colors = badgeColors[m] || 'bg-gray-100 text-gray-800 border-gray-300'
        return (
          <span key={i} className={`px-3 py-1 border rounded-full text-xs font-medium ${colors}`}>
            {m.replace(/_/g, ' ')}
          </span>
        )
      })}
    </div>
  )
}
