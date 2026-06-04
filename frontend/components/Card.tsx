import React from 'react'

export default function Card({children, className=''}:{children:React.ReactNode,className?:string}){
  const hasCardTone = /\bcard-(primary|secondary|muted|risk|danger|safe|action|evidence)\b/.test(className)
  const toneClass = hasCardTone ? '' : 'card-secondary'

  return (
    <div className={`guardian-panel app-card app-panel ${toneClass} guardian-card-hover rounded-md p-5 text-slate-100 ${className}`.trim()}>
      {children}
    </div>
  )
}
