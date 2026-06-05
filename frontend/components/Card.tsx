"use client"

import React from 'react'
import {motion, type Variants} from 'framer-motion'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'

const cardEase: [number, number, number, number] = [0.22, 1, 0.36, 1]

function cardVariants(shouldReduceMotion:boolean):Variants{
  return {
    hidden: {
      opacity: 0,
      y: shouldReduceMotion ? 0 : 20,
      scale: shouldReduceMotion ? 1 : 0.992,
    },
    show: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: shouldReduceMotion ? 0.16 : 0.58,
        ease: cardEase,
      },
    },
  }
}

export default function Card({children, className=''}:{children:React.ReactNode,className?:string}){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.div
      className={`enterprise-card guardian-panel app-card app-panel guardian-card-hover rounded-md p-5 text-slate-100 ${className}`.trim()}
      initial="hidden"
      whileInView="show"
      viewport={{once:true, amount:0.26}}
      variants={cardVariants(shouldReduceMotion)}
    >
      {children}
    </motion.div>
  )
}
