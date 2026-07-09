"use client"

import React, {useEffect, useState} from 'react'
import Image from 'next/image'
import Link from 'next/link'
import {usePathname} from 'next/navigation'
import {Menu, X} from 'lucide-react'
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
    selectLanguage:'Selecionar idioma',
    console:'Acessar console',
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
    selectLanguage:'Select language',
    console:'Access console',
    portuguese:'Português',
    english:'English',
  },
} satisfies Record<Locale, {
  nav:Array<{href:string; label:string}>
  navLabel:string
  selectLanguage:string
  console:string
  portuguese:string
  english:string
}>

export default function Header(){
  const [locale]=useGuardianLocale()
  const [scrolled,setScrolled]=useState(false)
  const [menuOpen,setMenuOpen]=useState(false)
  const pathname = usePathname()
  const isHome = pathname === '/'
  const copy = headerCopy[locale]

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
    setMenuOpen(false)
  },[pathname])

  const headerClass = [
    'guardian-header',
    isHome && !scrolled
      ? 'guardian-header-top'
      : 'guardian-header-scrolled',
  ].join(' ')
  const navLinkClass = 'guardian-nav-link'

  return (
    <header className={headerClass}>
      <div className="guardian-header-inner">
        <div className="guardian-brand-row">
          <Link
            href="/"
            className="guardian-brand"
          >
            <Image
              src="/cyberalerta-guardian-logo-banner.png"
              alt="CyberAlerta Guardian"
              width={238}
              height={84}
              className="guardian-brand-image"
              priority
            />
          </Link>
          <button
            type="button"
            className="guardian-mobile-toggle"
            aria-expanded={menuOpen}
            aria-controls="guardian-primary-navigation"
            aria-label={menuOpen ? 'Fechar navegação' : 'Abrir navegação'}
            onClick={()=>setMenuOpen(current=>!current)}
          >
            {menuOpen ? <X aria-hidden="true" /> : <Menu aria-hidden="true" />}
          </button>
        </div>

        <nav
          id="guardian-primary-navigation"
          className={`guardian-header-nav ${menuOpen ? 'is-open' : ''}`}
          aria-label={copy.navLabel}
        >
          {copy.nav.map((item)=> (
            <Link key={item.href} href={item.href} className={navLinkClass} onClick={()=>setMenuOpen(false)}>
              {item.label}
            </Link>
          ))}
          <Link href="/login" className="guardian-mobile-console" onClick={()=>setMenuOpen(false)}>
            {copy.console}
          </Link>
        </nav>

        <div className="guardian-header-actions">
          <Link
            href="/login"
            className="guardian-console-link"
          >
            {copy.console}
          </Link>
        </div>
      </div>
    </header>
  )
}
