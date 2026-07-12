"use client"

import {useEffect, useSyncExternalStore} from 'react'

const STORAGE_KEY = 'cyberalerta-motion-preference'
const mediaQuery = '(prefers-reduced-motion: reduce)'

function subscribe(onStoreChange:()=>void){
  window.addEventListener('cyberalerta:motion-change', onStoreChange)
  window.addEventListener('storage', (e:StorageEvent) => {
    if(e.key === STORAGE_KEY) onStoreChange()
  })
  return () => {
    window.removeEventListener('cyberalerta:motion-change', onStoreChange)
    window.removeEventListener('storage', () => {})
  }
}

function getSnapshot(){
  return window.localStorage.getItem(STORAGE_KEY) || 'enabled'
}

function getServerSnapshot(){ return 'enabled' }

export function setReducedMotionPreference(reduced:boolean){
  window.localStorage.setItem(STORAGE_KEY, reduced ? 'reduced' : 'enabled')
  window.dispatchEvent(new Event('cyberalerta:motion-change'))
}

/**
 * Legacy hook. Returns true when motion should be reduced.
 * Prefer useMotionPreference() from lib/motion.ts for new code.
 */
export function usePrefersReducedMotion(){
  const pref = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)

  useEffect(() => {
    document.documentElement.setAttribute('data-motion', pref)
  }, [pref])

  return pref !== 'enabled' && (
    pref === 'reduced' || window.matchMedia(mediaQuery).matches
  )
}
