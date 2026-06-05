"use client"

import React from 'react'
import {motion, type Variants} from 'framer-motion'
import {usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'

function cx(...classes: Array<string | false | undefined | null>){
  return classes.filter(Boolean).join(' ')
}

const revealEase: [number, number, number, number] = [0.22, 1, 0.36, 1]
const revealViewport = {once:true, amount:0.28}

function revealVariants(shouldReduceMotion:boolean, y = 26, scale = 1):Variants{
  return {
    hidden: {
      opacity: 1,
      y: shouldReduceMotion ? 0 : y,
      scale: shouldReduceMotion ? 1 : scale,
    },
    show: {
      opacity: 1,
      y: 0,
      scale: 1,
      transition: {
        duration: shouldReduceMotion ? 0.18 : 0.66,
        ease: revealEase,
      },
    },
  }
}

type ShellProps = {
  children: React.ReactNode
  className?: string
  maxWidth?: '6xl' | '7xl'
}

export function PageShell({children,className='',maxWidth='7xl'}:ShellProps){
  return (
    <section className={cx('guardian-product-page app-shell mx-auto space-y-7 pb-14', maxWidth === '6xl' ? 'max-w-6xl' : 'max-w-7xl', className)}>
      {children}
    </section>
  )
}

type PageHeaderProps = {
  eyebrow: string
  title: string
  description: string
  detail?: string
  actions?: React.ReactNode
  aside?: React.ReactNode
  className?: string
}

export function PageHeader({eyebrow,title,description,detail,actions,aside,className=''}:PageHeaderProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.header
      className={cx('guardian-page-header overflow-hidden', className)}
      initial="hidden"
      whileInView="show"
      viewport={revealViewport}
      variants={revealVariants(shouldReduceMotion, 22, 0.992)}
    >
      <div className="grid lg:grid-cols-[1.08fr_0.92fr]">
        <div className="p-6 sm:p-8 lg:p-10">
          <div className="guardian-kicker">{eyebrow}</div>
          <h1 className="app-page-title guardian-text-balance mt-5 max-w-4xl">
            {title}
          </h1>
          <p className="mt-4 max-w-3xl text-base font-medium leading-7 text-slate-300">
            {description}
          </p>
          {detail && <p className="mt-3 max-w-3xl text-sm leading-6 text-slate-400">{detail}</p>}
          {actions && <div className="mt-6 flex flex-col gap-3 sm:flex-row sm:flex-wrap">{actions}</div>}
        </div>
        {aside && (
          <div className="guardian-header-aside border-t border-white/10 p-6 text-white sm:p-8 lg:border-l lg:border-t-0 lg:p-10">
            {aside}
          </div>
        )}
      </div>
    </motion.header>
  )
}

type PanelProps = {
  children: React.ReactNode
  className?: string
  eyebrow?: string
  title?: string
  description?: string
}

export function CommandPanel({children,className='',eyebrow,title,description}:PanelProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.section
      className={cx('guardian-command-panel', className)}
      initial="hidden"
      whileInView="show"
      viewport={revealViewport}
      variants={revealVariants(shouldReduceMotion, 24, 0.992)}
    >
      {(eyebrow || title || description) && (
        <div className="guardian-panel-heading">
          {eyebrow && <div className="guardian-panel-eyebrow">{eyebrow}</div>}
          {title && <h2 className="guardian-panel-title">{title}</h2>}
          {description && <p className="guardian-panel-description">{description}</p>}
        </div>
      )}
      {children}
    </motion.section>
  )
}

export function DecisionPanel(props:PanelProps){
  return <CommandPanel {...props} className={cx('guardian-decision-panel', props.className)} />
}

export function EvidencePanel(props:PanelProps){
  return <CommandPanel {...props} className={cx('guardian-evidence-panel', props.className)} />
}

export function ActionPanel(props:PanelProps){
  return <CommandPanel {...props} className={cx('guardian-action-panel', props.className)} />
}

export function TimelinePanel(props:PanelProps){
  return <CommandPanel {...props} className={cx('guardian-timeline-panel', props.className)} />
}

export function IntelligencePanel(props:PanelProps){
  return <CommandPanel {...props} className={cx('guardian-intelligence-panel', props.className)} />
}

type MetricPanelProps = {
  label: string
  value: React.ReactNode
  detail?: string
  tone?: 'default' | 'risk' | 'safe' | 'cyan'
}

export function MetricPanel({label,value,detail,tone='default'}:MetricPanelProps){
  const shouldReduceMotion = usePrefersReducedMotion()

  return (
    <motion.div
      className={cx('guardian-metric-panel', tone !== 'default' && `guardian-metric-${tone}`)}
      initial="hidden"
      whileInView="show"
      viewport={revealViewport}
      variants={revealVariants(shouldReduceMotion, 20, 0.985)}
    >
      <div className="text-xs font-semibold uppercase text-slate-500">{detail || label}</div>
      <div className="mt-3 text-4xl font-semibold text-white">{value}</div>
      {detail && <div className="mt-2 text-sm font-semibold leading-5 text-slate-300">{label}</div>}
    </motion.div>
  )
}

type StatusRailProps = {
  items: Array<{label:string,value?:string,tone?:'ready'|'risk'|'warn'|'neutral'}>
  className?: string
}

export function StatusRail({items,className=''}:StatusRailProps){
  return (
    <div className={cx('guardian-status-rail', className)}>
      {items.map((item)=> (
        <div key={`${item.label}-${item.value || ''}`} className="guardian-status-cell">
          <span className={cx('guardian-status-dot', item.tone && `guardian-status-${item.tone}`)} />
          <div>
            <div className="text-xs font-semibold uppercase text-slate-500">{item.label}</div>
            {item.value && <div className="mt-1 text-sm font-semibold text-slate-100">{item.value}</div>}
          </div>
        </div>
      ))}
    </div>
  )
}

type TimelineProps = {
  items: Array<{title:string,body?:string}>
  className?: string
}

export function OperationalTimeline({items,className=''}:TimelineProps){
  return (
    <ol className={cx('guardian-operational-timeline', className)}>
      {items.map((item,index)=> (
        <li key={`${item.title}-${index}`} className="guardian-timeline-item">
          <span className="guardian-timeline-index">{String(index + 1).padStart(2,'0')}</span>
          <div>
            <div className="text-sm font-semibold text-white">{item.title}</div>
            {item.body && <p className="mt-1 text-sm leading-6 text-slate-400">{item.body}</p>}
          </div>
        </li>
      ))}
    </ol>
  )
}

type SectionHeaderProps = {
  eyebrow?: string
  title: string
  description?: string
  action?: React.ReactNode
}

export function SectionHeader({eyebrow,title,description,action}:SectionHeaderProps){
  return (
    <div className="guardian-section-header">
      <div>
        {eyebrow && <div className="guardian-panel-eyebrow">{eyebrow}</div>}
        <h2 className="guardian-panel-title">{title}</h2>
        {description && <p className="guardian-panel-description">{description}</p>}
      </div>
      {action}
    </div>
  )
}
