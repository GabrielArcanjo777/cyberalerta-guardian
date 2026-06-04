"use client"

import React from 'react'
import {RevealGroup, RevealItem, type RevealVariant} from '@/components/Reveal'

type Props = React.HTMLAttributes<HTMLElement> & {
  as?: React.ElementType
  delay?: number
  variant?: RevealVariant
}

export default function HomeScrollReveal({
  children,
  className='',
  as='section',
  delay=0,
  variant='revealDefault',
  ...rest
}: Props){
  return (
    <RevealGroup as={as} className={className} delay={delay} variant={variant} {...rest}>
      {React.Children.map(children, (child,index)=> (
        <RevealItem index={index}>{child}</RevealItem>
      ))}
    </RevealGroup>
  )
}
