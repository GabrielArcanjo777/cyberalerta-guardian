import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?: 'primary'|'ghost'}

export default function Button({variant='primary', children, className='', ...props}:Props){
  const base = 'inline-flex min-h-11 items-center justify-center rounded-md px-4 py-2 text-sm font-bold transition duration-200 disabled:cursor-not-allowed disabled:opacity-60'
  const v = variant === 'primary'
    ? 'border border-slate-950 bg-slate-950 text-white shadow-[0_10px_24px_rgba(2,6,23,0.18)] hover:bg-slate-800 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300'
    : 'border border-slate-300/80 bg-white/[0.88] text-slate-800 shadow-sm backdrop-blur hover:border-slate-400 hover:bg-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300'
  return (
    <button className={`${base} ${v} ${className}`.trim()} {...props}>{children}</button>
  )
}
