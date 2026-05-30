import React from 'react'

export default function Section({title,children}:{title?:string,children:React.ReactNode}){
  return (
    <section className="card-strong">
      {title && <div className="section-title">{title}</div>}
      <div className="mt-3">{children}</div>
    </section>
  )
}
