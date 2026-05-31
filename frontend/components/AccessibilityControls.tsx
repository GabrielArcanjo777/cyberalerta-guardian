"use client"

import React, {useEffect, useState} from 'react'

const largeTextClass = 'guardian-large-text'
const highContrastClass = 'guardian-high-contrast'

function applyRootClass(className:string, enabled:boolean){
  document.documentElement.classList.toggle(className, enabled)
}

export default function AccessibilityControls(){
  const [largeText,setLargeText]=useState(false)
  const [highContrast,setHighContrast]=useState(false)

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

  return (
    <div className="guardian-a11y-controls flex flex-wrap items-center gap-1.5" role="group" aria-label="Controles de acessibilidade">
      <span className="hidden text-xs font-bold uppercase tracking-wide text-slate-400 2xl:inline">Acessibilidade</span>
      <button
        type="button"
        aria-pressed={largeText}
        aria-label="Ativar ou desativar texto grande"
        onClick={toggleLargeText}
        className={`${buttonClass} ${largeText ? 'border-cyan-300/50 bg-cyan-300/15 text-cyan-100' : 'border-white/10 bg-white/[0.06] text-slate-200 hover:border-cyan-300/30 hover:bg-white/[0.1]'}`}
      >
        Texto grande
      </button>
      <button
        type="button"
        aria-pressed={highContrast}
        aria-label="Ativar ou desativar alto contraste"
        onClick={toggleHighContrast}
        className={`${buttonClass} ${highContrast ? 'border-cyan-300/50 bg-cyan-300/15 text-cyan-100' : 'border-white/10 bg-white/[0.06] text-slate-200 hover:border-cyan-300/30 hover:bg-white/[0.1]'}`}
      >
        Contraste
      </button>
    </div>
  )
}
