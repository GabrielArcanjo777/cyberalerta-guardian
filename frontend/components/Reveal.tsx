"use client"

import {motion, type HTMLMotionProps, type Variants} from 'framer-motion'
import type {ReactNode} from 'react'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'

type RevealProps = Omit<HTMLMotionProps<'div'>, 'initial' | 'whileInView' | 'viewport' | 'transition' | 'variants'> & {
  children:ReactNode
  delay?:number
  amount?:number
}

type RevealGroupProps = Omit<HTMLMotionProps<'div'>, 'initial' | 'whileInView' | 'viewport' | 'transition' | 'variants'> & {
  children:ReactNode
  amount?:number
  margin?:string
  delayChildren?:number
  staggerChildren?:number
}

type RevealItemProps = Omit<HTMLMotionProps<'div'>, 'initial' | 'whileInView' | 'viewport' | 'transition'> & {
  children:ReactNode
}

type MotionCardProps = Omit<HTMLMotionProps<'article'>, 'initial' | 'whileInView' | 'viewport' | 'transition'> & {
  children:ReactNode
}

const ease:[number, number, number, number] = [0.22, 1, 0.36, 1]

const cV:Variants = {
  hidden:{},
  show:{transition:{staggerChildren:0.08}},
}

const iV:Variants = {
  hidden:{opacity:0, y:28, scale:0.988},
  show:{opacity:1, y:0, scale:1, transition:{duration:0.64, ease}},
}

const visibleV:Variants = {
  hidden:{opacity:1, y:0, scale:1},
  show:{opacity:1, y:0, scale:1, transition:{duration:0.01}},
}

export function Reveal({children, delay = 0, amount = 0.18, className, ...props}:RevealProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.div
      {...props}
      className={className}
      initial={shouldReduceMotion ? false : {opacity:0, y:28}}
      whileInView={shouldReduceMotion ? undefined : {opacity:1, y:0}}
      animate={shouldReduceMotion ? {opacity:1, y:0} : undefined}
      viewport={{once:true, amount}}
      transition={{duration:0.64, ease, delay}}
    >
      {children}
    </motion.div>
  )
}

export function RevealGroup({
  children,
  className,
  amount = 0.18,
  margin,
  delayChildren = 0,
  staggerChildren = 0.08,
  ...props
}:RevealGroupProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.div
      {...props}
      className={className}
      variants={shouldReduceMotion ? visibleV : {
        ...cV,
        show:{transition:{delayChildren, staggerChildren}},
      }}
      initial={shouldReduceMotion ? false : 'hidden'}
      whileInView={shouldReduceMotion ? undefined : 'show'}
      animate={shouldReduceMotion ? 'show' : undefined}
      viewport={{once:true, amount, margin}}
    >
      {children}
    </motion.div>
  )
}

export function RevealItem({children, className, ...props}:RevealItemProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.div
      {...props}
      className={className}
      variants={shouldReduceMotion ? visibleV : iV}
      initial={shouldReduceMotion ? false : undefined}
      animate={shouldReduceMotion ? 'show' : undefined}
    >
      {children}
    </motion.div>
  )
}

export function MotionCard({children, className, ...props}:MotionCardProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.article
      {...props}
      className={className}
      variants={shouldReduceMotion ? visibleV : iV}
      initial={shouldReduceMotion ? false : undefined}
      animate={shouldReduceMotion ? 'show' : undefined}
    >
      {children}
    </motion.article>
  )
}

export function TitleReveal(props:RevealProps){
  return <Reveal {...props} />
}

export function TextReveal(props:RevealProps){
  return <Reveal {...props} />
}

export function CardReveal(props:RevealProps){
  return <Reveal {...props} />
}

export function LineReveal({delay = 0, amount = 0.18, className, ...props}:Omit<RevealProps, 'children'>){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.div
      {...props}
      className={className}
      initial={shouldReduceMotion ? false : {opacity:0, scaleX:0}}
      whileInView={shouldReduceMotion ? undefined : {opacity:1, scaleX:1}}
      animate={shouldReduceMotion ? {opacity:1, scaleX:1} : undefined}
      viewport={{once:true, amount}}
      transition={{duration:0.64, ease, delay}}
    />
  )
}

export const containerVariants:Variants = cV
export const itemVariants:Variants = iV

export function getItemVariants(shouldReduceMotion = false):Variants{
  return shouldReduceMotion ? visibleV : iV
}
