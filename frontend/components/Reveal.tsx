"use client"

import React, {CSSProperties, useEffect, useRef, useState} from 'react'

const variantConfig = {
  soft: {amount: 0.15, delayChildren: 0.08, stagger: 0.09, y: 30, blur: 6, duration: 620},
  default: {amount: 0.15, delayChildren: 0.1, stagger: 0.1, y: 28, blur: 6, duration: 560},
  hero: {amount: 0.15, delayChildren: 0.06, stagger: 0.08, y: 24, blur: 5, duration: 540},
  panel: {amount: 0.15, delayChildren: 0.08, stagger: 0.08, y: 30, blur: 6, duration: 600},
  card: {amount: 0.1, delayChildren: 0.05, stagger: 0.08, y: 24, blur: 5, duration: 520},
  fast: {amount: 0.1, delayChildren: 0.04, stagger: 0.06, y: 22, blur: 4, duration: 500},
  revealSlow: {amount: 0.55, delayChildren: 0.18, stagger: 0.14, y: 42, blur: 8, duration: 760},
  revealDefault: {amount: 0.42, delayChildren: 0.1, stagger: 0.09, y: 32, blur: 6, duration: 620},
  revealFast: {amount: 0.25, delayChildren: 0.04, stagger: 0.06, y: 24, blur: 5, duration: 500},
}

export type RevealVariant = keyof typeof variantConfig

type RevealContextValue = {
  delayChildren: number
  stagger: number
  visible: boolean
}

const RevealContext = React.createContext<RevealContextValue>({
  delayChildren: variantConfig.default.delayChildren,
  stagger: variantConfig.default.stagger,
  visible: true,
})

type RevealStyle = CSSProperties & {
  '--reveal-delay'?: string
  '--reveal-stagger'?: string
  '--reveal-y'?: string
  '--reveal-blur'?: string
  '--reveal-duration'?: string
  '--reveal-item-delay'?: string
}

type BaseProps = React.HTMLAttributes<HTMLElement> & {
  as?: React.ElementType
  amount?: number
  delay?: number
  margin?: string
  once?: boolean
  variant?: RevealVariant
}

type GroupProps = BaseProps & {
  delayChildren?: number
  stagger?: number
}

type ItemProps = React.HTMLAttributes<HTMLElement> & {
  as?: React.ElementType
  delay?: number
  index?: number
}

function useReveal({amount, margin='0px 0px -6% 0px', once=true}: {amount: number, margin?: string, once?: boolean}){
  const ref = useRef<HTMLElement | null>(null)
  const [visible,setVisible] = useState(false)

  useEffect(()=>{
    const node = ref.current
    if(!node) return

    const reducedMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches
    if(reducedMotion){
      setVisible(true)
      return
    }

    const observer = new IntersectionObserver(([entry])=>{
      if(entry.isIntersecting){
        setVisible(true)
        if(once) observer.disconnect()
      } else if(!once) {
        setVisible(false)
      }
    }, {threshold: Math.min(Math.max(amount, 0), 1), rootMargin: margin})

    observer.observe(node)
    return ()=>observer.disconnect()
  },[amount, margin, once])

  return {ref, visible}
}

function buildStyle(config: typeof variantConfig[RevealVariant], style?: CSSProperties, delay=0): RevealStyle {
  return {
    ...style,
    '--reveal-delay': `${delay / 1000}s`,
    '--reveal-stagger': `${config.stagger}s`,
    '--reveal-y': `${config.y}px`,
    '--reveal-blur': `${config.blur}px`,
    '--reveal-duration': `${config.duration}ms`,
  }
}

export function Reveal({
  children,
  className='',
  style,
  as='div',
  amount,
  delay=0,
  margin,
  once=true,
  variant='default',
  ...rest
}: BaseProps){
  const config = variantConfig[variant]
  const {ref, visible} = useReveal({amount: amount ?? config.amount, margin, once})
  const Component = as as React.ElementType

  return (
    <RevealContext.Provider value={{delayChildren: config.delayChildren, stagger: config.stagger, visible}}>
      <Component
        ref={ref}
        className={`reveal reveal-${variant} ${visible ? 'is-visible' : ''} ${className}`.trim()}
        style={buildStyle(config, style, delay)}
        {...rest}
      >
        {children}
      </Component>
    </RevealContext.Provider>
  )
}

export function RevealGroup({
  children,
  className='',
  style,
  as='section',
  amount,
  delay=0,
  delayChildren,
  margin,
  once=true,
  stagger,
  variant='default',
  ...rest
}: GroupProps){
  const config = variantConfig[variant]
  const {ref, visible} = useReveal({amount: amount ?? config.amount, margin, once})
  const groupConfig = {
    delayChildren: delayChildren ?? config.delayChildren,
    stagger: stagger ?? config.stagger,
    visible,
  }
  const Component = as as React.ElementType

  return (
    <RevealContext.Provider value={groupConfig}>
      <Component
        ref={ref}
        className={`reveal-group reveal-${variant} ${visible ? 'is-visible' : ''} ${className}`.trim()}
        style={buildStyle(config, style, delay)}
        {...rest}
      >
        {children}
      </Component>
    </RevealContext.Provider>
  )
}

export function RevealItem({
  children,
  className='',
  style,
  as='div',
  delay,
  index=0,
  ...rest
}: ItemProps){
  const context = React.useContext(RevealContext)
  const Component = as as React.ElementType
  const itemDelay = delay ?? ((context.delayChildren + (index * context.stagger)) * 1000)

  return (
    <Component
      className={`reveal-item ${context.visible ? 'is-visible' : ''} ${className}`.trim()}
      style={{
        ...style,
        '--reveal-item-delay': `${itemDelay / 1000}s`,
      } as RevealStyle}
      {...rest}
    >
      {children}
    </Component>
  )
}

export function ScrollScene({className='', ...props}: GroupProps){
  return <RevealGroup className={`scroll-scene ${className}`.trim()} {...props} />
}
