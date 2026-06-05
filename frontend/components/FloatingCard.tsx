"use client"

import Link from 'next/link'
import {motion, type Variants} from 'framer-motion'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'
import styles from './FloatingCard.module.css'

type FloatingCardTone = 'risk' | 'lock' | 'trust' | 'human'
type FloatingCardSide = 'left' | 'right'

type FloatingCardProps = {
  index:string
  title:string
  body:string
  label:string
  badge?:string
  tone:FloatingCardTone
  side:FloatingCardSide
  delay?:number
  href?:string
}

function makeVariants(side:FloatingCardSide, reduceMotion:boolean, delay:number):Variants {
  if(reduceMotion){
    return {
      hidden:{opacity:1, x:0, y:0, scale:1},
      show:{opacity:1, x:0, y:0, scale:1, transition:{duration:0.01, delay:0}},
    }
  }

  return {
    hidden:{
      opacity:0,
      x:side === 'left' ? -24 : 24,
      y:8,
      scale:0.985,
    },
    show:{
      opacity:1,
      x:0,
      y:0,
      scale:1,
      transition:{
        duration:0.58,
        delay,
        ease:[0.22, 1, 0.36, 1],
      },
    },
  }
}

export default function FloatingCard({index,title,body,label,badge,tone,side,delay = 0,href}:FloatingCardProps){
  const shouldReduceMotion = usePrefersReducedMotion()
  const toneClass = {
    risk:styles.risk,
    lock:styles.lock,
    trust:styles.trust,
    human:styles.human,
  }[tone]
  const cardClass = `${styles.card} ${toneClass} ${href ? styles.link : ''}`
  const cardContent = (
    <>
      <div className={styles.top}>
        <span className={styles.index}>{index}</span>
        <span className={styles.label}>{label}</span>
      </div>
      {badge && <span className={styles.badge}>{badge}</span>}
      <h3 className={styles.title}>{title}</h3>
      <p className={styles.body}>{body}</p>
    </>
  )

  return (
    <motion.div
      className={styles.motion}
      initial="hidden"
      animate="show"
      variants={makeVariants(side, shouldReduceMotion, delay)}
    >
      {href ? (
        <Link href={href} className={cardClass} aria-label={`${title}. ${body}`}>
          {cardContent}
        </Link>
      ) : (
        <article className={cardClass}>
          {cardContent}
        </article>
      )}
    </motion.div>
  )
}
