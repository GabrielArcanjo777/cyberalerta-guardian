"use client"

import React, {useEffect, useRef, useState} from 'react'
import Link from 'next/link'
import {usePathname} from 'next/navigation'
import AccessibilityControls from '@/components/AccessibilityControls'
import {defaultLocale, getMessages, Locale, supportedLocales} from '@/lib/i18n'

const primaryNav = [
  {href:'/assisted-demo', label:'Demo guiada'},
  {href:'/before-pix', label:'Analisar'},
  {href:'/global', label:'Radar'},
  {href:'/simulator', label:'Casos'},
  {href:'/integrations', label:'Integrações'},
  {href:'/trust-center', label:'Trust Center'},
]

const platformNav = [
  {href:'/dashboard', label:'Painel de impacto'},
  {href:'/chatbot-demo', label:'Canal simples'},
  {href:'/intake', label:'Intake seguro'},
  {href:'/ml-lab', label:'ML Lab'},
  {href:'/help-network', label:'Rede de ajuda'},
  {href:'/family-console', label:'Guardian Console'},
  {href:'/pilot', label:'Prontidão do piloto'},
  {href:'/recovery', label:'Modo recuperação'},
]

export default function Header(){
  const [locale,setLocale]=useState<Locale>(defaultLocale)
  const [platformOpen,setPlatformOpen]=useState(false)
  const [settingsOpen,setSettingsOpen]=useState(false)
  const headerRef = useRef<HTMLElement | null>(null)
  const pathname = usePathname()
  const t = getMessages(locale)

  useEffect(()=>{
    const stored = window.localStorage.getItem('cyberalerta:locale') as Locale | null
    if(stored && supportedLocales.includes(stored)){
      setLocale(stored)
    }
  },[])

  useEffect(()=>{
    setPlatformOpen(false)
    setSettingsOpen(false)
  },[pathname])

  useEffect(()=>{
    if(!platformOpen && !settingsOpen) return

    function onPointerDown(event:PointerEvent){
      const target = event.target as Node | null
      if(target && !headerRef.current?.contains(target)){
        setPlatformOpen(false)
        setSettingsOpen(false)
      }
    }

    function onKeyDown(event:KeyboardEvent){
      if(event.key === 'Escape'){
        setPlatformOpen(false)
        setSettingsOpen(false)
      }
    }

    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return ()=>{
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  },[platformOpen, settingsOpen])

  function onLocaleChange(nextLocale:Locale){
    setLocale(nextLocale)
    window.localStorage.setItem('cyberalerta:locale', nextLocale)
  }

  const navLinkClass = 'inline-flex min-h-9 shrink-0 items-center justify-center whitespace-nowrap rounded-md border border-transparent bg-transparent px-3 py-1.5 text-sm font-semibold leading-tight text-slate-300 transition hover:border-cyan-300/20 hover:bg-white/[0.055] hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300'
  const renderControlPanel = () => (
    <>
      <label className="flex min-h-10 shrink-0 items-center gap-2 rounded-md border border-white/10 bg-white/[0.045] px-2.5 text-xs font-bold uppercase text-slate-400">
        <span className="hidden sm:inline">Idioma</span>
        <select
          value={locale}
          onChange={event=>onLocaleChange(event.target.value as Locale)}
          className="h-8 rounded-md border border-white/10 bg-slate-900 px-2 text-xs font-bold normal-case text-slate-100 shadow-sm"
          aria-label="Selecionar idioma"
        >
          <option value="pt-BR">Português</option>
          <option value="en-US">English</option>
        </select>
      </label>
      <AccessibilityControls />
    </>
  )

  return (
    <header ref={headerRef} className="guardian-header sticky top-0 z-[80] mt-0 rounded-none border-b border-white/10 bg-slate-950 px-3 py-2.5 text-white shadow-[0_14px_34px_rgba(2,6,23,0.34)] sm:top-3 sm:mt-3 sm:rounded-md sm:border sm:px-4">
      {(platformOpen || settingsOpen) && (
        <button
          type="button"
          aria-label="Fechar menus"
          className="guardian-menu-shield fixed inset-0 z-[70] cursor-default bg-slate-950/62"
          onClick={()=>{
            setPlatformOpen(false)
            setSettingsOpen(false)
          }}
        />
      )}

      <div className="relative z-[81] flex flex-col gap-2 xl:grid xl:grid-cols-[minmax(200px,auto)_minmax(0,1fr)_auto] xl:items-center xl:gap-3">
        <div className="flex min-w-0 items-center justify-between gap-3">
          <Link
            href="/"
            className="group inline-flex min-w-0 items-center gap-3"
            onClick={()=>{
              setPlatformOpen(false)
              setSettingsOpen(false)
            }}
          >
            <span className="flex h-9 w-9 shrink-0 items-center justify-center rounded-md border border-cyan-300/25 bg-cyan-300/[0.08] text-xs font-semibold text-cyan-100 shadow-inner">
              CG
            </span>
            <span className="min-w-0">
              <span className="block truncate text-lg font-semibold leading-tight text-white group-hover:text-cyan-100">CyberAlerta Guardian</span>
              <span className="hidden truncate text-xs font-semibold leading-5 text-slate-400 md:block">{t.tagline}</span>
            </span>
          </Link>

          <button
            type="button"
            className={`${navLinkClass} xl:hidden ${settingsOpen ? 'border-cyan-300/45 bg-cyan-300/[0.12] text-white' : 'border-white/10 bg-white/[0.04]'}`}
            aria-expanded={settingsOpen}
            aria-haspopup="menu"
            aria-label="Abrir configurações"
            onClick={()=>{
              setSettingsOpen(open=>!open)
              setPlatformOpen(false)
            }}
          >
            Ajustes
          </button>
        </div>

        <nav className="guardian-nav-scroll -mx-1 flex min-w-0 flex-nowrap items-center gap-1 overflow-x-auto px-1 pb-1 xl:mx-0 xl:justify-center xl:overflow-visible xl:pb-0" aria-label="Navegação principal">
          {primaryNav.map((item)=> (
            <Link
              key={item.href}
              href={item.href}
              className={navLinkClass}
              onClick={()=>{
                setPlatformOpen(false)
                setSettingsOpen(false)
              }}
            >
              {item.label}
            </Link>
          ))}

          <div className="guardian-platform-menu-root relative shrink-0">
            <button
              type="button"
              className={`${navLinkClass} gap-1 ${platformOpen ? 'border-cyan-300/45 bg-cyan-300/[0.12] text-white' : ''}`}
              aria-expanded={platformOpen}
              aria-haspopup="menu"
              onClick={()=>{
                setPlatformOpen(open=>!open)
                setSettingsOpen(false)
              }}
            >
              <span>Plataforma</span>
              <span className="text-[10px] opacity-80" aria-hidden="true">▾</span>
            </button>

            {platformOpen && (
              <div
                className="guardian-dropdown absolute left-1/2 top-[calc(100%+0.45rem)] z-[100] w-[min(18rem,calc(100vw-2rem))] -translate-x-1/2 rounded-md border border-slate-600/80 bg-slate-950 p-2 shadow-[0_24px_64px_rgba(2,6,23,0.78)] ring-1 ring-cyan-300/10 xl:left-auto xl:right-0 xl:translate-x-0"
                role="menu"
              >
                <div className="mb-1 border-b border-white/10 px-3 py-2 text-[11px] font-black uppercase tracking-[0.18em] text-slate-400">
                  Plataforma Guardian
                </div>
                {platformNav.map((item)=> (
                  <Link
                    key={item.href}
                    href={item.href}
                    role="menuitem"
                    onClick={()=>{
                      setPlatformOpen(false)
                      setSettingsOpen(false)
                    }}
                    className="block min-h-11 rounded-md border border-transparent px-3 py-2.5 text-sm font-semibold leading-5 text-slate-200 transition hover:border-cyan-300/25 hover:bg-white/[0.08] hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300"
                  >
                    {item.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </nav>

        <div className="hidden shrink-0 flex-wrap items-center gap-2 xl:flex xl:justify-end">
          {renderControlPanel()}
        </div>

        {settingsOpen && (
          <div className="guardian-dropdown absolute right-0 top-[calc(100%+0.55rem)] z-[100] w-[min(22rem,calc(100vw-2rem))] rounded-md border border-slate-600/80 bg-slate-950 p-3 shadow-[0_24px_64px_rgba(2,6,23,0.78)] ring-1 ring-cyan-300/10 xl:hidden" role="menu">
            <div className="mb-3 border-b border-white/10 pb-2 text-[11px] font-black uppercase tracking-[0.18em] text-slate-400">
              Configurações
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
