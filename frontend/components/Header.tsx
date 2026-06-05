"use client"

import React, {useEffect, useRef, useState} from 'react'
import Link from 'next/link'
import {usePathname} from 'next/navigation'
import AccessibilityControls from '@/components/AccessibilityControls'
import {Locale, useGuardianLocale} from '@/lib/i18n'

const headerCopy = {
  'pt-BR': {
    nav: [
      {href:'/#plataforma', label:'Plataforma'},
      {href:'/#solucoes', label:'Soluções'},
      {href:'/#recursos', label:'Recursos'},
      {href:'/#empresa', label:'Empresa'},
      {href:'/#contato', label:'Contato'},
    ],
    navLabel:'Navegação principal',
    settings:'Configurações',
    closeSettings:'Fechar configurações',
    openSettings:'Abrir configurações',
    openPanel:'Abrir ajustes de idioma e acessibilidade',
    settingsTitle:'Configurações',
    language:'Idioma',
    selectLanguage:'Selecionar idioma',
    console:'Acessar Console',
    portuguese:'Português',
    english:'English',
  },
  'en-US': {
    nav: [
      {href:'/#plataforma', label:'Platform'},
      {href:'/#solucoes', label:'Solutions'},
      {href:'/#recursos', label:'Resources'},
      {href:'/#empresa', label:'Company'},
      {href:'/#contato', label:'Contact'},
    ],
    navLabel:'Primary navigation',
    settings:'Settings',
    closeSettings:'Close settings',
    openSettings:'Open settings',
    openPanel:'Open language and accessibility settings',
    settingsTitle:'Settings',
    language:'Language',
    selectLanguage:'Select language',
    console:'Access Console',
    portuguese:'Português',
    english:'English',
  },
} satisfies Record<Locale, {
  nav:Array<{href:string; label:string}>
  navLabel:string
  settings:string
  closeSettings:string
  openSettings:string
  openPanel:string
  settingsTitle:string
  language:string
  selectLanguage:string
  console:string
  portuguese:string
  english:string
}>

function ShieldMark(){
  return (
    <span className="guardian-logo-mark" aria-hidden="true">
      <svg viewBox="0 0 24 24" fill="none" role="img">
        <path d="M12 3.4 18.3 6v5.3c0 4.1-2.5 7.7-6.3 9.1-3.8-1.4-6.3-5-6.3-9.1V6L12 3.4Z" stroke="currentColor" strokeWidth="1.8" strokeLinejoin="round" />
        <path d="m9.2 12.1 1.9 1.9 4-4.3" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" />
      </svg>
    </span>
  )
}

export default function Header(){
  const [locale,setLocale]=useGuardianLocale()
  const [settingsOpen,setSettingsOpen]=useState(false)
  const [scrolled,setScrolled]=useState(false)
  const headerRef = useRef<HTMLElement | null>(null)
  const pathname = usePathname()
  const isHome = pathname === '/'
  const copy = headerCopy[locale]

  useEffect(()=>{
    setSettingsOpen(false)
  },[pathname])

  useEffect(()=>{
    if(!isHome){
      setScrolled(true)
      return
    }

    function updateScrolled(){
      setScrolled(window.scrollY > 18)
    }

    updateScrolled()
    window.addEventListener('scroll', updateScrolled, {passive:true})
    return ()=>window.removeEventListener('scroll', updateScrolled)
  },[isHome])

  useEffect(()=>{
    if(!settingsOpen) return

    function onPointerDown(event:PointerEvent){
      const target = event.target as Node | null
      if(target && !headerRef.current?.contains(target)){
        setSettingsOpen(false)
      }
    }

    function onKeyDown(event:KeyboardEvent){
      if(event.key === 'Escape'){
        setSettingsOpen(false)
      }
    }

    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return ()=>{
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  },[settingsOpen])

  function onLocaleChange(nextLocale:Locale){
    setLocale(nextLocale)
    setSettingsOpen(false)
  }

  const headerClass = [
    'guardian-header sticky top-0 z-[80] mt-0 rounded-none border-b px-3 py-2.5 text-white backdrop-blur-md transition-all duration-300 sm:px-4',
    isHome && !scrolled
      ? 'border-white/[0.06] bg-[#05070b]/72 shadow-none sm:top-4 sm:mt-4 sm:rounded-md sm:border'
      : 'border-white/[0.06] bg-[#05070b]/88 shadow-[0_14px_34px_rgba(2,6,23,0.28)] sm:top-3 sm:mt-3 sm:rounded-md sm:border',
  ].join(' ')
  const navLinkClass = 'inline-flex min-h-9 shrink-0 items-center justify-center whitespace-nowrap rounded-md border border-transparent bg-transparent px-3 py-1.5 text-sm font-medium leading-tight text-slate-300/70 transition-colors duration-200 hover:text-slate-50 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300'

  const renderControlPanel = () => (
    <>
      <label className="flex min-h-10 shrink-0 items-center gap-2 rounded-md border border-white/10 bg-white/[0.045] px-2.5 text-xs font-bold uppercase text-slate-400">
        <span className="hidden sm:inline">{copy.language}</span>
        <select
          value={locale}
          onChange={event=>onLocaleChange(event.target.value as Locale)}
          className="h-8 rounded-md border border-white/10 bg-slate-900 px-2 text-xs font-bold normal-case text-slate-100 shadow-sm"
          aria-label={copy.selectLanguage}
        >
          <option value="pt-BR">{copy.portuguese}</option>
          <option value="en-US">{copy.english}</option>
        </select>
      </label>
      <AccessibilityControls />
    </>
  )

  return (
    <header ref={headerRef} className={headerClass}>
      {settingsOpen && (
        <button
          type="button"
          aria-label={copy.closeSettings}
          className="guardian-menu-shield fixed inset-0 z-[70] cursor-default bg-slate-950/62"
          onClick={()=>setSettingsOpen(false)}
        />
      )}

      <div className="relative z-[81] flex flex-col gap-2 xl:grid xl:grid-cols-[minmax(240px,auto)_minmax(0,1fr)_auto] xl:items-center xl:gap-8">
        <div className="flex min-w-0 items-center justify-between gap-3">
          <Link
            href="/"
            className="group inline-flex min-w-0 items-center gap-3"
            onClick={()=>setSettingsOpen(false)}
          >
            <ShieldMark />
            <span className="block min-w-0 truncate text-lg font-semibold leading-tight text-white group-hover:text-cyan-100">
              CyberAlerta Guardian
            </span>
          </Link>

          <button
            type="button"
            className={`${navLinkClass} xl:hidden ${settingsOpen ? 'border-cyan-300/45 bg-cyan-300/[0.12] text-white' : 'border-white/10 bg-white/[0.04]'}`}
            aria-expanded={settingsOpen}
            aria-haspopup="menu"
            aria-label={copy.openSettings}
            onClick={()=>setSettingsOpen(open=>!open)}
          >
            {copy.settings}
          </button>
        </div>

        <nav className="guardian-nav-scroll -mx-1 flex min-w-0 flex-nowrap items-center gap-1.5 overflow-x-auto px-1 pb-1 xl:mx-0 xl:justify-center xl:overflow-visible xl:pb-0 xl:pr-2" aria-label={copy.navLabel}>
          {copy.nav.map((item)=> (
            <Link key={item.href} href={item.href} className={navLinkClass}>
              {item.label}
            </Link>
          ))}
        </nav>

        <div className="hidden shrink-0 items-center justify-end gap-2 border-l border-white/10 pl-6 xl:flex">
          <button
            type="button"
            className={`${navLinkClass} border-white/10 bg-white/[0.035] px-3.5 ${settingsOpen ? 'border-cyan-300/45 bg-cyan-300/[0.12] text-white' : ''}`}
            aria-expanded={settingsOpen}
            aria-haspopup="menu"
            aria-label={copy.openPanel}
            onClick={()=>setSettingsOpen(open=>!open)}
          >
            {copy.settings}
          </button>
          <Link
            href="/family-console"
            className="inline-flex min-h-9 shrink-0 items-center justify-center rounded-md border border-cyan-300/30 bg-cyan-300/[0.1] px-3.5 py-1.5 text-sm font-bold leading-tight text-cyan-50 transition hover:border-cyan-200/50 hover:bg-cyan-300/[0.16] focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
          >
            {copy.console}
          </Link>
        </div>

        {settingsOpen && (
          <div className="guardian-dropdown absolute right-0 top-[calc(100%+0.55rem)] z-[100] w-[min(22rem,calc(100vw-2rem))] rounded-md border border-slate-600/80 bg-slate-950 p-3 shadow-[0_24px_64px_rgba(2,6,23,0.78)] ring-1 ring-cyan-300/10" role="menu">
            <div className="mb-3 border-b border-white/10 pb-2 text-[11px] font-black uppercase tracking-[0.18em] text-slate-400">
              {copy.settingsTitle}
            </div>
            <div className="flex flex-col gap-3">
              {renderControlPanel()}
            </div>
          </div>
        )}
      </div>
    </header>
  )
}
