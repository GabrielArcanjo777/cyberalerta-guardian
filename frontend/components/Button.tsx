import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?: 'primary'|'ghost'}

export default function Button({variant='primary', children, className='', ...props}:Props){
  const base = 'inline-flex min-h-11 items-center justify-center rounded-md px-4 py-2 text-sm font-bold transition duration-200 disabled:cursor-not-allowed disabled:opacity-60'
  const v = variant === 'primary'
    ? 'border border-teal-300/45 bg-teal-500 text-slate-950 shadow-[0_14px_34px_rgba(20,184,166,0.22)] hover:border-teal-200/70 hover:bg-teal-300 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-300'
    : 'border border-white/12 bg-slate-950/72 text-slate-100 shadow-sm backdrop-blur hover:border-teal-300/40 hover:bg-slate-900 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-teal-300'
  return (
    <button className={`${base} ${v} ${className}`.trim()} {...props}>{children}</button>
  )
}
