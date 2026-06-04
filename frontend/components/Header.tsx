"use client"

import React, {useEffect, useRef, useState} from 'react'
import Link from 'next/link'
import {usePathname} from 'next/navigation'
import {defaultLocale, Locale, supportedLocales} from '@/lib/i18n'

const navGroups = [
  {
    label:'Plataforma',
    items:[
      {href:'/family-console', label:'Guardian Console'},
      {href:'/dashboard', label:'Painel de impacto'},
      {href:'/global', label:'Visão global'},
    ],
  },
  {
    label:'Soluções',
    items:[
      {href:'/before-pix', label:'Before Pix'},
      {href:'/assisted-demo', label:'Demo assistida'},
      {href:'/chatbot-demo', label:'Canal simples'},
    ],
  },
  {
    label:'Recursos',
    items:[
      {href:'/trust-center', label:'Trust Center'},
      {href:'/ml-lab', label:'ML Lab'},
      {href:'/report', label:'Relatório'},
    ],
  },
  {
    label:'Empresa',
    items:[
      {href:'/pilot', label:'Prontidão do piloto'},
      {href:'/help-network', label:'Rede de ajuda'},
      {href:'/integrations', label:'Integrações'},
    ],
  },
]

function ShieldLogo(){
  return (
    <svg viewBox="0 0 24 24" aria-hidden="true">
      <path d="M12 3.2 5.2 5.8v5.4c0 4.5 2.8 8.1 6.8 9.7 4-1.6 6.8-5.2 6.8-9.7V5.8L12 3.2Z" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinejoin="round" />
      <path d="M12 7.2v9.5M8.8 11.5l3.2 3.2 5.1-5.5" fill="none" stroke="currentColor" strokeWidth="1.7" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

function Chevron(){
  return (
    <svg viewBox="0 0 16 16" aria-hidden="true">
      <path d="m4.5 6 3.5 3.5L11.5 6" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
    </svg>
  )
}

export default function Header(){
  const [locale,setLocale]=useState<Locale>(defaultLocale)
  const [openMenu,setOpenMenu]=useState<string | null>(null)
  const [scrolled,setScrolled]=useState(false)
  const headerRef = useRef<HTMLElement | null>(null)
  const pathname = usePathname()
  const isHome = pathname === '/'

  useEffect(()=>{
    const stored = window.localStorage.getItem('cyberalerta:locale') as Locale | null
    if(stored && supportedLocales.includes(stored)){
      setLocale(stored)
    }
  },[])

  useEffect(()=>{
    setOpenMenu(null)
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
    if(!openMenu) return

    function onPointerDown(event:PointerEvent){
      const target = event.target as Node | null
      if(target && !headerRef.current?.contains(target)){
        setOpenMenu(null)
      }
    }

    function onKeyDown(event:KeyboardEvent){
      if(event.key === 'Escape') setOpenMenu(null)
    }

    document.addEventListener('pointerdown', onPointerDown)
    document.addEventListener('keydown', onKeyDown)
    return ()=>{
      document.removeEventListener('pointerdown', onPointerDown)
      document.removeEventListener('keydown', onKeyDown)
    }
  },[openMenu])

  function toggleLocale(){
    const nextLocale: Locale = locale === 'pt-BR' ? 'en-US' : 'pt-BR'
    setLocale(nextLocale)
    window.localStorage.setItem('cyberalerta:locale', nextLocale)
  }

  return (
    <header ref={headerRef} className={`guardian-header ${isHome ? 'guardian-header-home' : ''} ${scrolled ? 'is-scrolled' : ''}`}>
      <div className="guardian-header-inner">
        <Link href="/" className="guardian-brand" onClick={()=>setOpenMenu(null)}>
          <span className="guardian-brand-mark">
            <ShieldLogo />
          </span>
          <span className="guardian-brand-text">
            <span>CyberAlerta</span>
            <span>Guardian</span>
          </span>
        </Link>

        <nav className="guardian-main-nav" aria-label="Navegação principal">
          {navGroups.map((group)=> (
            <div key={group.label} className="guardian-nav-group">
              <button
                type="button"
                className="guardian-nav-link"
                aria-haspopup="menu"
                aria-expanded={openMenu === group.label}
                onClick={()=>setOpenMenu(current=> current === group.label ? null : group.label)}
              >
                {group.label}
                <Chevron />
              </button>
              {openMenu === group.label && (
                <div className="guardian-nav-dropdown" role="menu">
                  {group.items.map((item)=> (
                    <Link
                      key={item.href}
                      href={item.href}
                      role="menuitem"
                      onClick={()=>setOpenMenu(null)}
                    >
                      {item.label}
                    </Link>
                  ))}
                </div>
              )}
            </div>
          ))}
          <Link href="/pilot" className="guardian-nav-link" onClick={()=>setOpenMenu(null)}>
            Contato
          </Link>
        </nav>

        <div className="guardian-header-actions">
          <button type="button" className="guardian-language-button" onClick={toggleLocale} aria-label="Alternar idioma">
            {locale === 'pt-BR' ? 'PT' : 'EN'}
            <Chevron />
          </button>
          <Link href="/family-console" className="guardian-console-button" onClick={()=>setOpenMenu(null)}>
            <ShieldLogo />
            Acessar Console
          </Link>
        </div>
      </div>
    </header>
  )
}
