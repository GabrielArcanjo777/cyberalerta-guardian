import React from 'react'

export default function Card({children, className=''}:{children:React.ReactNode,className?:string}){
  return (
    <div className={`guardian-panel guardian-card-hover rounded-md p-5 text-slate-950 ${className}`.trim()}>
      {children}
    </div>
  )
}
