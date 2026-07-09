"use client"

import {useRouter} from 'next/navigation'
import React, {useEffect, useState} from 'react'
import AdminRoute from '@/components/AdminRoute'
import Button from '@/components/Button'
import {
  getAdminAuditLogs,
  getAdminUsers,
  getBackendHealth,
  getN8nHealth,
  postLogout,
} from '@/lib/api'
import {AdminAuditLogsResponse, AdminUsersResponse, AuthUser} from '@/lib/types'

type HealthState = {
  backend?: string
  n8n?: string
}

function AdminPanel({user}: {user: AuthUser}){
  const router = useRouter()
  const [users,setUsers] = useState<AdminUsersResponse | null>(null)
  const [audit,setAudit] = useState<AdminAuditLogsResponse | null>(null)
  const [health,setHealth] = useState<HealthState>({})
  const [loading,setLoading] = useState(true)
  const [error,setError] = useState<string | null>(null)

  async function load(){
    setLoading(true)
    setError(null)
    try{
      const [usersResult, auditResult, backendResult, n8nResult] = await Promise.allSettled([
        getAdminUsers(),
        getAdminAuditLogs(),
        getBackendHealth(),
        getN8nHealth(),
      ])

      if(usersResult.status === 'fulfilled') setUsers(usersResult.value)
      if(auditResult.status === 'fulfilled') setAudit(auditResult.value)
      setHealth({
        backend: backendResult.status === 'fulfilled' ? backendResult.value.status : 'erro',
        n8n: n8nResult.status === 'fulfilled' ? String(n8nResult.value.status || 'ok') : 'indisponivel',
      })

      if(usersResult.status === 'rejected' || auditResult.status === 'rejected'){
        setError('Nao foi possivel carregar todos os dados administrativos.')
      }
    }finally{
      setLoading(false)
    }
  }

  useEffect(()=>{
    load()
  },[])

  async function logout(){
    await postLogout().catch(()=>null)
    router.push('/login')
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col gap-4 rounded-md border border-slate-200 bg-white p-5 sm:flex-row sm:items-center sm:justify-between">
        <div>
          <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-700">Admin</p>
          <h1 className="mt-2 text-2xl font-black text-slate-800">{user.full_name}</h1>
          <p className="mt-1 text-sm text-slate-600">{user.email} · {user.role} · MFA ativo</p>
        </div>
        <div className="flex flex-wrap gap-2">
          <Button type="button" variant="ghost" onClick={load} disabled={loading}>Atualizar</Button>
          <Button type="button" variant="ghost" onClick={logout}>Sair</Button>
        </div>
      </div>

      <div className="grid gap-4 md:grid-cols-3">
        <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase text-slate-500">Backend</p>
          <p className="mt-2 text-xl font-black text-slate-800">{health.backend || 'carregando'}</p>
        </div>
        <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase text-slate-500">n8n</p>
          <p className="mt-2 text-xl font-black text-slate-800">{health.n8n || 'carregando'}</p>
        </div>
        <div className="rounded-md border border-slate-200 bg-slate-50 p-4">
          <p className="text-xs font-bold uppercase text-slate-500">Usuarios</p>
          <p className="mt-2 text-xl font-black text-slate-800">{users?.users.length ?? '...'}</p>
        </div>
      </div>

      {error && <p className="rounded-md border border-amber-200 bg-amber-50 p-4 text-sm text-amber-800">{error}</p>}

      <section className="rounded-md border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-black text-slate-800">Usuarios</h2>
        <div className="mt-4 overflow-x-auto">
          <table className="w-full min-w-[620px] text-left text-sm text-slate-700">
            <thead className="text-xs uppercase text-slate-500">
              <tr>
                <th className="border-b border-slate-200 py-2 pr-4">Email</th>
                <th className="border-b border-slate-200 py-2 pr-4">Nome</th>
                <th className="border-b border-slate-200 py-2 pr-4">Role</th>
                <th className="border-b border-slate-200 py-2 pr-4">MFA</th>
                <th className="border-b border-slate-200 py-2 pr-4">Ativo</th>
              </tr>
            </thead>
            <tbody className="text-slate-700">
              {(users?.users || []).map(item=>(
                <tr key={item.id}>
                  <td className="border-b border-slate-100 py-3 pr-4">{item.email}</td>
                  <td className="border-b border-slate-100 py-3 pr-4">{item.full_name}</td>
                  <td className="border-b border-slate-100 py-3 pr-4">{item.role}</td>
                  <td className="border-b border-slate-100 py-3 pr-4">{item.mfa_enabled ? 'ativo' : 'inativo'}</td>
                  <td className="border-b border-slate-100 py-3 pr-4">{item.is_active ? 'sim' : 'nao'}</td>
                </tr>
              ))}
              {!loading && !users?.users.length && (
                <tr><td className="py-4 text-slate-500" colSpan={5}>Nenhum usuario encontrado.</td></tr>
              )}
            </tbody>
          </table>
        </div>
      </section>

      <section className="rounded-md border border-slate-200 bg-white p-5">
        <h2 className="text-lg font-black text-slate-800">Auditoria de autenticacao</h2>
        <div className="mt-4 space-y-3">
          {(audit?.logs || []).slice(0, 12).map(item=>(
            <div key={item.id} className="rounded-md border border-slate-200 bg-slate-50 p-3">
              <div className="flex flex-wrap items-center justify-between gap-2">
                <p className="text-sm font-bold text-slate-800">{item.event_type}</p>
                <span className={`rounded-md border px-2 py-1 text-xs font-bold ${item.success ? 'border-teal-300 text-teal-700' : 'border-red-300 text-red-700'}`}>
                  {item.success ? 'sucesso' : 'falha'}
                </span>
              </div>
              <p className="mt-1 text-xs text-slate-400">{item.email || 'sem email'} · {new Date(item.created_at).toLocaleString('pt-BR')}</p>
              {item.reason && <p className="mt-1 text-xs text-slate-400">Motivo: {item.reason}</p>}
            </div>
          ))}
          {!loading && !audit?.logs.length && <p className="text-sm text-slate-400">Nenhum evento de autenticacao registrado.</p>}
        </div>
      </section>
    </div>
  )
}

export default function AdminPage(){
  return (
    <div className="min-h-screen bg-white">
      <section className="mx-auto w-full max-w-6xl px-4 py-10">
        <AdminRoute>
          {(user)=><AdminPanel user={user} />}
        </AdminRoute>
      </section>
    </div>
  )
}
