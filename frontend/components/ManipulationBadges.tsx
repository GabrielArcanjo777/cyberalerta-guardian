import React from 'react'

const badgeColors: {[key:string]: string} = {
  urgencia: 'border-red-200 bg-red-50 text-red-700',
  vinculo_familiar: 'border-sky-200 bg-sky-50 text-sky-700',
  numero_novo: 'border-amber-200 bg-amber-50 text-amber-700',
  pedido_financeiro: 'border-violet-200 bg-violet-50 text-violet-700',
  pedido_para_nao_ligar: 'border-orange-200 bg-orange-50 text-orange-700',
  promessa_financeira: 'border-fuchsia-200 bg-fuchsia-50 text-fuchsia-700',
}

function normalizeBadge(value:string){
  return value.trim().toLowerCase().replace(/\s+/g, '_')
}

export default function ManipulationBadges({items}:{items:string[]}){
  return (
    <div className="flex flex-wrap gap-2">
      {items.map((item,index)=> {
        const key = normalizeBadge(item)
        const colors = badgeColors[key] || 'border-slate-200 bg-slate-50 text-slate-700'
        return (
          <span key={`${item}-${index}`} className={`rounded border px-3 py-1.5 text-xs font-bold uppercase tracking-wide ${colors}`}>
            {key.replace(/_/g, ' ')}
          </span>
        )
      })}
    </div>
  )
}
