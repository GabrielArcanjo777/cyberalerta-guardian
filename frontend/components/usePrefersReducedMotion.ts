"use client"

import {useEffect, useSyncExternalStore} from 'react'

const reducedMotionStorageKey = 'cyberalerta:a11y:reduced-motion'
const reducedMotionChangeEvent = 'cyberalerta:reduced-motion-change'
const reducedMotionClass = 'guardian-reduced-motion'

function subscribe(onStoreChange:()=>void){
  const onStorage = (event:StorageEvent) => {
    if(event.key === reducedMotionStorageKey) onStoreChange()
  }

  window.addEventListener(reducedMotionChangeEvent, onStoreChange)
  window.addEventListener('storage', onStorage)
  return () => {
    window.removeEventListener(reducedMotionChangeEvent, onStoreChange)
    window.removeEventListener('storage', onStorage)
  }
}

function getSnapshot(){
  return window.localStorage.getItem(reducedMotionStorageKey) === 'true'
}

function getServerSnapshot(){
  return false
}

function syncReducedMotionClass(reducedMotion:boolean){
  document.documentElement.classList.toggle(reducedMotionClass, reducedMotion)
}

export function setReducedMotionPreference(reducedMotion:boolean){
  window.localStorage.setItem(reducedMotionStorageKey, String(reducedMotion))
  syncReducedMotionClass(reducedMotion)
  window.dispatchEvent(new Event(reducedMotionChangeEvent))
}

export function usePrefersReducedMotion(){
  const reducedMotion = useSyncExternalStore(subscribe, getSnapshot, getServerSnapshot)

  useEffect(()=>{
    syncReducedMotionClass(reducedMotion)
  },[reducedMotion])

  return reducedMotion
}
