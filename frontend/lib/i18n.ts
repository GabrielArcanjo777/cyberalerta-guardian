"use client"

import {useCallback, useEffect, useState} from 'react'

export const supportedLocales = ['pt-BR', 'en-US'] as const

export type Locale = typeof supportedLocales[number]

export const defaultLocale:Locale = 'pt-BR'

const localeStorageKey = 'cyberalerta:locale'
const localeChangeEvent = 'cyberalerta:locale-change'

export const messages = {
  'pt-BR': {
    tagline: 'Antes do Pix. Antes do clique. Antes do prejuízo.',
    protectivePause: 'O Guardian cria uma pausa protetiva antes de decisões digitais perigosas.',
    submitSuspiciousMessage: 'Enviar mensagem suspeita',
    trustLockActivated: 'Trust Lock ativado',
    familyConsole: 'Family Console',
    recoveryMode: 'Recovery Mode',
    trustCenter: 'Trust Center',
    impactDashboard: 'Impact Dashboard',
    pilotReadiness: 'Pilot Readiness',
    beforePix: 'Antes do Pix',
    integrations: 'Integrações',
    simulator: 'Simulador',
    globalApplicability: 'Aplicabilidade global',
    helpNetwork: 'Rede de Ajuda',
  },
  'en-US': {
    tagline: 'Before payments. Before clicks. Before loss.',
    protectivePause: 'Guardian creates a protective pause before dangerous digital decisions.',
    submitSuspiciousMessage: 'Submit suspicious message',
    trustLockActivated: 'Trust Lock activated',
    familyConsole: 'Family Console',
    recoveryMode: 'Recovery Mode',
    trustCenter: 'Trust Center',
    impactDashboard: 'Impact Dashboard',
    pilotReadiness: 'Pilot Readiness',
    beforePix: 'Before Pix',
    integrations: 'Integrations',
    simulator: 'Simulator',
    globalApplicability: 'Global Applicability',
    helpNetwork: 'Help Network',
  },
} satisfies Record<Locale, Record<string, string>>

export function isSupportedLocale(value:string | null | undefined):value is Locale{
  return supportedLocales.includes(value as Locale)
}

export function getMessages(locale:Locale){
  return messages[locale] || messages[defaultLocale]
}

function readBrowserLocale():Locale{
  if(typeof window === 'undefined') return defaultLocale

  const stored = window.localStorage.getItem(localeStorageKey)
  return isSupportedLocale(stored) ? stored : defaultLocale
}

function syncDocumentLanguage(locale:Locale){
  if(typeof document !== 'undefined'){
    document.documentElement.lang = locale
  }
}

export function persistLocale(locale:Locale){
  if(typeof window === 'undefined') return

  window.localStorage.setItem(localeStorageKey, locale)
  syncDocumentLanguage(locale)
  window.dispatchEvent(new CustomEvent<Locale>(localeChangeEvent, {detail: locale}))
}

export function useGuardianLocale(){
  const [locale,setLocaleState] = useState<Locale>(defaultLocale)

  useEffect(()=>{
    const storedLocale = readBrowserLocale()
    setLocaleState(storedLocale)
    syncDocumentLanguage(storedLocale)

    function onLocaleChange(event:Event){
      const nextLocale = event instanceof CustomEvent ? event.detail : null
      if(isSupportedLocale(nextLocale)){
        setLocaleState(nextLocale)
        syncDocumentLanguage(nextLocale)
      }
    }

    function onStorage(event:StorageEvent){
      if(event.key === localeStorageKey && isSupportedLocale(event.newValue)){
        setLocaleState(event.newValue)
        syncDocumentLanguage(event.newValue)
      }
    }

    window.addEventListener(localeChangeEvent, onLocaleChange)
    window.addEventListener('storage', onStorage)
    return ()=>{
      window.removeEventListener(localeChangeEvent, onLocaleChange)
      window.removeEventListener('storage', onStorage)
    }
  },[])

  const setLocale = useCallback((nextLocale:Locale)=>{
    setLocaleState(nextLocale)
    persistLocale(nextLocale)
  },[])

  return [locale,setLocale] as const
}
