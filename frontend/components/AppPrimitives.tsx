import React from 'react'
import {connectorStatusClass, connectorStatusLabel, type ConnectorStatusKey} from '@/lib/appStatus'

function cx(...classes: Array<string | false | undefined>){
  return classes.filter(Boolean).join(' ')
}

export function AppBadge({children, className=''}:{children:React.ReactNode, className?:string}){
  return <span className={cx('app-badge', className)}>{children}</span>
}

export function AppStatus({status, className=''}:{status:ConnectorStatusKey, className?:string}){
  return (
    <span className={cx(connectorStatusClass(status), className)}>
      {connectorStatusLabel(status)}
    </span>
  )
}

export function AppSectionTitle({children, className=''}:{children:React.ReactNode, className?:string}){
  return <h2 className={cx('app-section-title', className)}>{children}</h2>
}

export function AppCardTitle({children, className=''}:{children:React.ReactNode, className?:string}){
  return <h3 className={cx('app-card-title', className)}>{children}</h3>
}

const trustPipelineSteps = [
  'Detectar intenção',
  'Pontuar risco',
  'Pausar decisão',
  'Gerar evidência',
  'Acionar responsável, se necessário',
]

export function TrustPipeline({className=''}:{className?:string}){
  return (
    <div className={cx('app-pipeline', className)}>
      <div className="app-label">Pipeline de confiança</div>
      <ol className="app-pipeline-steps" aria-label="Pipeline de confiança">
        {trustPipelineSteps.map((step,index)=> (
          <li key={step} className="app-pipeline-step">
            <span className="app-pipeline-index" aria-hidden="true">{index + 1}</span>
            <span className="app-pipeline-label">{step}</span>
          </li>
        ))}
      </ol>
    </div>
  )
}
