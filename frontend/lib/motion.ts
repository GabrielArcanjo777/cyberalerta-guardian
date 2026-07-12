"use client"

import {useEffect} from 'react'

const STORAGE_KEY = 'cyberalerta-motion-preference'

export type MotionPreference = 'system' | 'enabled' | 'reduced'

/**
 * Resolve the effective boolean: should animations run?
 *
 * enabled      → true  (always animate)
 * reduced      → false (never animate)
 * system       → defer to OS (prefers-reduced-motion: no-preference)
 */
export function resolveMotion(pref: MotionPreference): boolean {
  if (pref === 'enabled') return true
  if (pref === 'reduced') return false
  return !window.matchMedia('(prefers-reduced-motion: reduce)').matches
}

export function getStoredPreference(): MotionPreference {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (raw === 'enabled' || raw === 'reduced' || raw === 'system') return raw
  } catch { /* localStorage unavailable */ }
  return 'system'
}

export function setStoredPreference(pref: MotionPreference): void {
  window.localStorage.setItem(STORAGE_KEY, pref)
  applyMotionAttribute(pref)
}

function applyMotionAttribute(pref: MotionPreference): void {
  const root = document.documentElement
  root.setAttribute('data-motion', pref)
  // Remove any stale legacy class
  root.classList.toggle('guardian-reduced-motion', pref === 'reduced')
}

/**
 * Hook that returns the current motion preference and a setter.
 * Also syncs data-motion on <html>.
 */
export function useMotionPreference() {
  // Read from localStorage on mount (client-only)
  const pref = typeof window !== 'undefined' ? getStoredPreference() : 'system'

  useEffect(() => {
    applyMotionAttribute(pref)
  }, [pref])

  return {
    preference: pref,
    enabled: resolveMotion(pref),
    setPreference: (p: MotionPreference) => setStoredPreference(p),
  }
}
