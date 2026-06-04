import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?: 'primary'|'ghost'}

export default function Button({variant='primary', children, className='', ...props}:Props){
  const base = 'inline-flex min-h-[46px] items-center justify-center rounded-[14px] px-5 py-2 text-sm font-bold transition duration-200 active:translate-y-0 disabled:cursor-not-allowed disabled:opacity-60'
  const v = variant === 'primary'
    ? 'guardian-button-primary border border-white/70 bg-gradient-to-b from-slate-50 to-cyan-100 text-slate-950 shadow-[inset_0_1px_0_rgba(255,255,255,0.72),0_12px_32px_rgba(2,6,23,0.28)] hover:-translate-y-0.5 hover:shadow-[inset_0_1px_0_rgba(255,255,255,0.84),0_18px_42px_rgba(2,6,23,0.34)] focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-[3px] focus-visible:outline-teal-300/60'
    : 'guardian-button-secondary border border-slate-500/30 bg-slate-950/48 text-slate-100 shadow-sm backdrop-blur hover:-translate-y-0.5 hover:border-cyan-300/34 hover:bg-slate-900/78 focus-visible:outline focus-visible:outline-[3px] focus-visible:outline-offset-[3px] focus-visible:outline-teal-300/50'
  return (
    <button className={`${base} ${v} ${className}`.trim()} {...props}>{children}</button>
  )
}
