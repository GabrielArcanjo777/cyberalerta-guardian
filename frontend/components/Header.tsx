"use client"

import React, {useEffect, useState} from 'react'
import Link from 'next/link'
import AccessibilityControls from '@/components/AccessibilityControls'
import {defaultLocale, getMessages, Locale, supportedLocales} from '@/lib/i18n'

const primaryNav = [
  {href:'/before-pix', label:'Analisar'},
  {href:'/global', label:'Radar'},
  {href:'/simulator', label:'Casos'},
  {href:'/integrations', label:'Integracoes'},
  {href:'/trust-center', label:'Trust Center'},
]

const platformNav = [
  {href:'/dashboard', label:'Impact Dashboard'},
  {href:'/intake', label:'Intake seguro'},
  {href:'/ml-lab', label:'ML Lab'},
  {href:'/help-network', label:'Help Network'},
  {href:'/family-console', label:'Family Console'},
  {href:'/pilot', label:'Pilot Readiness'},
  {href:'/recovery', label:'Recovery Mode'},
]

export default function Header(){
  const [locale,setLocale]=useState<Locale>(defaultLocale)
  const t = getMessages(locale)

  useEffect(()=>{
    const stored = window.localStorage.getItem('cyberalerta:locale') as Locale | null
    if(stored && supportedLocales.includes(stored)){
      setLocale(stored)
    }
  },[])

  function onLocaleChange(nextLocale:Locale){
    setLocale(nextLocale)
    window.localStorage.setItem('cyberalerta:locale', nextLocale)
  }

  const navLinkClass = 'inline-flex min-h-10 items-center justify-center rounded-md border border-white/10 bg-white/[0.05] px-3.5 py-2 text-sm font-bold text-slate-200 transition hover:border-cyan-300/35 hover:bg-white/[0.1] hover:text-white focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300'

  return (
    <header className="sticky top-3 z-30 mt-3 rounded-md border border-white/10 bg-slate-950/82 px-4 py-4 text-white shadow-[0_14px_42px_rgba(2,6,23,0.28)] backdrop-blur-xl">
      <div className="grid gap-4 xl:grid-cols-[minmax(260px,0.9fr)_auto_minmax(260px,0.9fr)] xl:items-center">
        <div>
          <Link href="/" className="group inline-flex items-center gap-3">
            <span className="flex h-10 w-10 items-center justify-center rounded-md border border-cyan-300/30 bg-white/[0.08] text-sm font-black text-cyan-100 shadow-inner">
              CG
            </span>
            <span>
              <span className="block text-xl font-black text-white group-hover:text-cyan-100">CyberAlerta Guardian</span>
              <span className="block text-sm font-semibold text-slate-400">{t.tagline}</span>
            </span>
          </Link>
        </div>

        <nav className="flex flex-wrap gap-2 xl:justify-center" aria-label="Navegacao principal">
          {primaryNav.map((item)=> (
            <Link key={item.href} href={item.href} className={navLinkClass}>
              {item.label}
            </Link>
          ))}

          <details className="group relative">
            <summary className={`${navLinkClass} cursor-pointer list-none`}>
              Plataforma
            </summary>
            <div className="absolute right-0 z-40 mt-2 w-64 rounded-md border border-white/10 bg-slate-950/96 p-2 shadow-[0_18px_48px_rgba(2,6,23,0.42)] backdrop-blur-xl group-open:block">
              {platformNav.map((item)=> (
                <Link
                  key={item.href}
                  href={item.href}
                  className="block rounded-md border border-transparent px-3 py-2 text-sm font-bold text-slate-300 transition hover:border-white/10 hover:bg-white/[0.07] hover:text-white"
                >
                  {item.label}
                </Link>
              ))}
            </div>
          </details>
        </nav>

        <div className="flex flex-col gap-3 xl:items-end">
          <label className="flex items-center gap-2 text-xs font-bold uppercase text-slate-400">
            Idioma
            <select
              value={locale}
              onChange={event=>onLocaleChange(event.target.value as Locale)}
              className="min-h-10 rounded-md border border-white/10 bg-slate-900 px-3 text-xs font-bold normal-case text-slate-100 shadow-sm"
              aria-label="Selecionar idioma"
            >
              <option value="pt-BR">Portugues</option>
              <option value="en-US">English</option>
            </select>
          </label>
          <AccessibilityControls />
        </div>
      </div>
    </header>
  )
}
