import React from 'react'

type FloatingCardTone = 'danger' | 'neutral' | 'safe'

type Props = {
  title: string
  lines: string[]
  icon: 'warning' | 'shield' | 'users'
  tone?: FloatingCardTone
  className?: string
  style?: React.CSSProperties
}

function WarningIcon(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3.7 2.7 20.2h18.6L12 3.7Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="M12 8.2v5.5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M12 17.1h.01" fill="none" stroke="currentColor" strokeWidth="2.4" strokeLinecap="round" />
    </svg>
  )
}

function ShieldIcon(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3.2 5.2 5.9v5.2c0 4.5 2.8 8 6.8 9.7 4-1.7 6.8-5.2 6.8-9.7V5.9L12 3.2Z" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
      <path d="m8.8 12 2.3 2.3 5-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function UsersIcon(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M9.5 11.2a3 3 0 1 0 0-6 3 3 0 0 0 0 6Z" fill="none" stroke="currentColor" strokeWidth="1.8" />
      <path d="M4.2 19.2c.6-3.1 2.5-5 5.3-5s4.7 1.9 5.3 5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M15.2 11.7a2.5 2.5 0 1 0 0-5" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
      <path d="M16.6 14.2c1.9.4 3.2 1.9 3.7 4.2" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" />
    </svg>
  )
}

function Icon({icon}:{icon: Props['icon']}){
  if(icon === 'warning') return <WarningIcon />
  if(icon === 'users') return <UsersIcon />
  return <ShieldIcon />
}

export default function FloatingCard({title, lines, icon, tone='neutral', className='', style}:Props){
  return (
    <article className={`floating-card floating-card-${tone} ${className}`.trim()} style={style}>
      <div className="floating-card-icon">
        <Icon icon={icon} />
      </div>
      <div>
        <h3>{title}</h3>
        {lines.map((line,index)=> (
          <p key={line} className={index === 1 && tone === 'danger' ? 'floating-card-risk' : undefined}>
            {line}
          </p>
        ))}
      </div>
    </article>
  )
}
