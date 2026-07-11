"use client"

import React, {useEffect, useState} from 'react'
import Link from 'next/link'
import {usePathname} from 'next/navigation'
import {Menu, X} from 'lucide-react'
import {Locale, useGuardianLocale} from '@/lib/i18n'
import {getAuthMe} from '@/lib/api'
import {AuthUser} from '@/lib/types'

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
    console:'Acessar Console',
    admin:'Admin',
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
    console:'Access Console',
    admin:'Admin',
  },
} satisfies Record<Locale, {
  nav:Array<{href:string; label:string}>
  navLabel:string
  console:string
  admin:string
}>

function ShieldMark(){
  return (
    <svg
      width="22"
      height="22"
      viewBox="0 0 24 24"
      fill="none"
      xmlns="http://www.w3.org/2000/svg"
      aria-hidden="true"
    >
      <path
        d="M12 2.5 4.5 5.4v5.2c0 4.6 3.2 8.9 7.5 10.4 4.3-1.5 7.5-5.8 7.5-10.4V5.4L12 2.5Z"
        stroke="#2dd4bf"
        strokeWidth="1.6"
        strokeLinejoin="round"
      />
      <path
        d="m8.8 11.8 2.2 2.2 4.2-4.4"
        stroke="#2dd4bf"
        strokeWidth="1.6"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
    </svg>
  )
}

export default function Header(){
  const [locale]=useGuardianLocale()
  const [menuOpen,setMenuOpen]=useState(false)
  const [user,setUser] = useState<AuthUser | null>(null)
  const pathname = usePathname()
  const copy = headerCopy[locale]

  // Auth-aware: check session on mount so we can show/hide the Admin link.
  useEffect(()=>{
    let active = true
    getAuthMe()
      .then(s => { if(active) setUser(s.user || null) })
      .catch(() => { if(active) setUser(null) })
    return ()=>{ active = false }
  },[])

  useEffect(()=>{
    setMenuOpen(false)
  },[pathname])

  const isAdmin = user?.role === 'admin' && user?.is_admin
  // When authenticated go straight to the console; otherwise redirect via login.
  const consoleHref = user ? '/family-console' : '/login?redirect=/family-console'

  return (
    <header className="guardian-header">
      <div className="guardian-header-inner">
        <div className="guardian-brand-row">
          <Link href="/" className="guardian-brand">
            <ShieldMark />
            <span className="guardian-brand-name">CyberAlerta</span>
            <span className="guardian-brand-badge">Guardian</span>
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
            <Link key={item.href} href={item.href} className="guardian-nav-link" onClick={()=>setMenuOpen(false)}>
              {item.label}
            </Link>
          ))}
          {isAdmin && (
            <Link href="/admin" className="guardian-nav-link guardian-nav-mobile-only" onClick={()=>setMenuOpen(false)}>
              {copy.admin}
            </Link>
          )}
          <Link href={consoleHref} className="guardian-mobile-console" onClick={()=>setMenuOpen(false)}>
            {copy.console}
          </Link>
        </nav>

        <div className="guardian-header-actions">
          {isAdmin && (
            <Link href="/admin" className="guardian-ghost-link">
              {copy.admin}
            </Link>
          )}
          <Link href={consoleHref} className="guardian-console-link">
            {copy.console}
          </Link>
        </div>
      </div>
    </header>
  )
}
