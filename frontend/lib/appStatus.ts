export type ConnectorStatusKey = 'mock' | 'future' | 'ready' | string

export function connectorStatusLabel(status:ConnectorStatusKey){
  if(status === 'mock') return 'SIMULADO'
  if(status === 'future') return 'FUTURO'
  if(status === 'ready') return 'PRONTO'
  return String(status).toUpperCase()
}

export function connectorStatusClass(status:ConnectorStatusKey){
  if(status === 'ready') return 'app-status app-status-ready'
  if(status === 'future') return 'app-status app-status-future'
  return 'app-status app-status-simulated'
}

export function riskStatusClass(level:string){
  if(level === 'critical') return 'app-status app-status-critical'
  if(level === 'high') return 'app-status app-status-high'
  if(level === 'medium') return 'app-status app-status-medium'
  return 'app-status app-status-neutral'
}
