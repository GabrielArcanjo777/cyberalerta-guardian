import React from 'react'

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {variant?: 'primary'|'ghost'}

export default function Button({variant='primary', children, className='', ...props}:Props){
  const v = variant === 'primary' ? 'btn btn-primary' : 'btn btn-ghost'
  return (
    <button className={`${v} ${className}`.trim()} {...props}>{children}</button>
  )
}
