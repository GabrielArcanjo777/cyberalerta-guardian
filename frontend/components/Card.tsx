import React from 'react'

export default function Card({children, className=''}:{children:React.ReactNode,className?:string}){
  return (
    <div className={`guardian-panel app-card app-panel guardian-card-hover rounded-md p-5 text-slate-100 ${className}`.trim()}>
      {children}
    </div>
  )
}
