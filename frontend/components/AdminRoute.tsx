"use client"

import Link from 'next/link'
import React from 'react'
import ProtectedRoute from '@/components/ProtectedRoute'
import {AuthUser} from '@/lib/types'

type AdminRouteProps = {
  children: React.ReactNode | ((user: AuthUser)=>React.ReactNode)
}

export default function AdminRoute({children}:AdminRouteProps){
  return (
    <ProtectedRoute>
      {(user)=> {
        if(user.role !== 'admin' || !user.is_admin){
          return (
            <div className="rounded-md border border-red-300/20 bg-red-400/[0.08] p-5 text-sm text-red-100">
              Esta area exige permissao de administrador.
            </div>
          )
        }

        if(!user.mfa_enabled){
          return (
            <div className="rounded-md border border-amber-300/20 bg-amber-300/[0.08] p-5 text-sm text-amber-100">
              <p>MFA e obrigatorio para administradores antes de acessar dados sensiveis.</p>
              <Link href="/mfa" className="mt-4 inline-flex min-h-10 items-center rounded-md border border-amber-200/40 bg-amber-200/[0.14] px-4 text-sm font-bold text-amber-50">
                Configurar MFA
              </Link>
            </div>
          )
        }

        return <>{typeof children === 'function' ? children(user) : children}</>
      }}
    </ProtectedRoute>
  )
}
