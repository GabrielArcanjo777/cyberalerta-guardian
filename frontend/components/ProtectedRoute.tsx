"use client"

import Link from 'next/link'
import {usePathname} from 'next/navigation'
import React, {useEffect, useState} from 'react'
import {getAuthMe} from '@/lib/api'
import {AuthUser} from '@/lib/types'

type ProtectedRouteProps = {
  children: React.ReactNode | ((user: AuthUser)=>React.ReactNode)
}

export default function ProtectedRoute({children}:ProtectedRouteProps){
  const [user,setUser] = useState<AuthUser | null>(null)
  const [loading,setLoading] = useState(true)
  const [error,setError] = useState<string | null>(null)
  const pathname = usePathname()

  useEffect(()=>{
    let mounted = true
    getAuthMe()
      .then((session)=>{
        if(!mounted) return
        setUser(session.user || null)
      })
      .catch(()=>{
        if(!mounted) return
        setError('Nao foi possivel validar a sessao.')
      })
      .finally(()=>{
        if(mounted) setLoading(false)
      })
    return ()=>{ mounted = false }
  },[])

  if(loading){
    return <div className="rounded-md border border-white/10 bg-white/[0.04] p-5 text-sm text-slate-300">Validando sessao...</div>
  }

  if(error){
    return <div className="rounded-md border border-amber-300/20 bg-amber-300/[0.08] p-5 text-sm text-amber-100">{error}</div>
  }

  if(!user){
    const loginHref = `/login?redirect=${encodeURIComponent(pathname)}`
    return (
      <div className="rounded-md border border-white/10 bg-white/[0.04] p-5 text-sm text-slate-300">
        <p>Entre para acessar esta area.</p>
        <Link href={loginHref} className="mt-4 inline-flex min-h-10 items-center rounded-md border border-teal-300/40 bg-teal-300/[0.12] px-4 text-sm font-bold text-teal-50">
          Ir para login
        </Link>
      </div>
    )
  }

  return <>{typeof children === 'function' ? children(user) : children}</>
}
