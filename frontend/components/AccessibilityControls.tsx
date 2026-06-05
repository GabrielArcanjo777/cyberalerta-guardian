"use client"

import React, {useEffect, useState} from 'react'
import {useGuardianLocale, type Locale} from '@/lib/i18n'
import {setReducedMotionPreference, usePrefersReducedMotion} from '@/components/usePrefersReducedMotion'

const largeTextClass = 'guardian-large-text'
const highContrastClass = 'guardian-high-contrast'

const accessibilityCopy = {
  'pt-BR': {
    group:'Controles de acessibilidade',
    title:'Acessibilidade',
    largeText:'Texto grande',
    largeTextLabel:'Ativar ou desativar texto grande',
    contrast:'Contraste',
    contrastLabel:'Ativar ou desativar alto contraste',
    motion:'Animações',
    motionLabel:'Ativar ou desativar animações',
  },
  'en-US': {
    group:'Accessibility controls',
    title:'Accessibility',
    largeText:'Large text',
    largeTextLabel:'Enable or disable large text',
    contrast:'Contrast',
    contrastLabel:'Enable or disable high contrast',
    motion:'Animations',
    motionLabel:'Enable or disable animations',
  },
} satisfies Record<Locale, Record<string, string>>

function applyRootClass(className:string, enabled:boolean){
  document.documentElement.classList.toggle(className, enabled)
}

export default function AccessibilityControls(){
  const [locale] = useGuardianLocale()
  const copy = accessibilityCopy[locale]
  const [largeText,setLargeText] = useState(false)
  const [highContrast,setHighContrast] = useState(false)
  const shouldReduceMotion = usePrefersReducedMotion()

  useEffect(()=>{
    const storedLargeText = window.localStorage.getItem('cyberalerta:a11y:large-text') === 'true'
    const storedHighContrast = window.localStorage.getItem('cyberalerta:a11y:high-contrast') === 'true'
    setLargeText(storedLargeText)
    setHighContrast(storedHighContrast)
    applyRootClass(largeTextClass, storedLargeText)
    applyRootClass(highContrastClass, storedHighContrast)
  },[])

  function toggleLargeText(){
    const next = !largeText
    setLargeText(next)
    window.localStorage.setItem('cyberalerta:a11y:large-text', String(next))
    applyRootClass(largeTextClass, next)
  }

  function toggleHighContrast(){
    const next = !highContrast
    setHighContrast(next)
    window.localStorage.setItem('cyberalerta:a11y:high-contrast', String(next))
    applyRootClass(highContrastClass, next)
  }

  const buttonClass = 'min-h-10 rounded-md border px-2.5 py-2 text-xs font-bold uppercase tracking-wide leading-tight transition focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300'
  const activeClass = 'border-cyan-300/50 bg-cyan-300/15 text-cyan-100'
  const inactiveClass = 'border-white/10 bg-white/[0.06] text-slate-200 hover:border-cyan-300/30 hover:bg-white/[0.1]'

  return (
    <div className="guardian-a11y-controls flex flex-wrap items-center gap-1.5" role="group" aria-label={copy.group}>
      <span className="hidden text-xs font-bold uppercase tracking-wide text-slate-400 2xl:inline">{copy.title}</span>
      <button
        type="button"
        aria-pressed={largeText}
        aria-label={copy.largeTextLabel}
        onClick={toggleLargeText}
        className={`${buttonClass} ${largeText ? activeClass : inactiveClass}`}
      >
        {copy.largeText}
      </button>
      <button
        type="button"
        aria-pressed={highContrast}
        aria-label={copy.contrastLabel}
        onClick={toggleHighContrast}
        className={`${buttonClass} ${highContrast ? activeClass : inactiveClass}`}
      >
        {copy.contrast}
      </button>
      <button
        type="button"
        aria-pressed={!shouldReduceMotion}
        aria-label={copy.motionLabel}
        onClick={()=>setReducedMotionPreference(!shouldReduceMotion)}
        className={`${buttonClass} ${!shouldReduceMotion ? activeClass : inactiveClass}`}
      >
        {copy.motion}
      </button>
    </div>
  )
}
