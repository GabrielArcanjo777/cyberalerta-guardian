import React from 'react'

export default function Badge({children, tone='neutral'}:{children:React.ReactNode,tone?:'neutral'|'critical'|'warning'|'safe'}){
  const cls = tone === 'critical' ? 'badge badge-critical' : tone === 'warning' ? 'badge badge-warning' : tone === 'safe' ? 'badge badge-safe' : 'badge'
  return <span className={cls as string}>{children}</span>
}
