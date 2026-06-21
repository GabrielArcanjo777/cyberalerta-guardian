"use client"

import Link from 'next/link'
import {useRouter} from 'next/navigation'
import React, {FormEvent, useState} from 'react'
import Button from '@/components/Button'
import Header from '@/components/Header'
import {getGoogleLoginUrl, postLogin, postMfaVerify} from '@/lib/api'
import {LoginResponse} from '@/lib/types'

export default function LoginPage(){
  const router = useRouter()
  const [email,setEmail] = useState('')
  const [password,setPassword] = useState('')
  const [mfaCode,setMfaCode] = useState('')
  const [pendingMfa,setPendingMfa] = useState<LoginResponse | null>(null)
  const [loading,setLoading] = useState(false)
  const [error,setError] = useState<string | null>(null)

  async function onSubmit(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    setLoading(true)
    setError(null)
    try{
      const result = await postLogin({email, password})
      if(result.mfa_required){
        setPendingMfa(result)
        return
      }
      router.push(result.user?.role === 'admin' ? '/admin' : '/family-console')
    }catch{
      setError('Credenciais invalidas.')
    }finally{
      setLoading(false)
    }
  }

  async function onMfaSubmit(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    if(!pendingMfa?.temporary_token) return
    setLoading(true)
    setError(null)
    try{
      const result = await postMfaVerify(pendingMfa.temporary_token, mfaCode)
      router.push(result.user?.role === 'admin' ? '/admin' : '/family-console')
    }catch{
      setError('Codigo MFA invalido.')
    }finally{
      setLoading(false)
    }
  }

  function startGoogleLogin(){
    window.location.href = getGoogleLoginUrl()
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <Header />
      <section className="mx-auto flex min-h-[calc(100vh-5rem)] w-full max-w-5xl items-center px-4 py-10">
        <div className="grid w-full gap-6 lg:grid-cols-[1fr_0.85fr] lg:items-start">
          <div className="space-y-4">
            <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-200">Acesso seguro</p>
            <h1 className="text-3xl font-black text-white sm:text-4xl">Entrar no CyberAlerta Guardian</h1>
            <p className="max-w-2xl text-sm leading-6 text-slate-300">
              Use sua conta local ou Google OAuth configurado no backend. A sessao fica em cookie HttpOnly e tokens nao sao salvos no navegador.
            </p>
            <div className="rounded-md border border-white/10 bg-white/[0.04] p-4 text-sm text-slate-300">
              Administradores precisam habilitar MFA antes de acessar APIs administrativas.
            </div>
          </div>

          <div className="rounded-md border border-white/10 bg-slate-900/70 p-5 shadow-[0_24px_72px_rgba(2,6,23,0.42)]">
            {!pendingMfa ? (
              <form className="space-y-4" onSubmit={onSubmit}>
                <label className="block text-sm font-semibold text-slate-200">
                  Email
                  <input
                    type="email"
                    value={email}
                    onChange={event=>setEmail(event.target.value)}
                    className="mt-2 h-11 w-full rounded-md border border-white/10 bg-slate-950 px-3 text-sm text-white outline-none focus:border-teal-300/60"
                    autoComplete="email"
                    required
                  />
                </label>
                <label className="block text-sm font-semibold text-slate-200">
                  Senha
                  <input
                    type="password"
                    value={password}
                    onChange={event=>setPassword(event.target.value)}
                    className="mt-2 h-11 w-full rounded-md border border-white/10 bg-slate-950 px-3 text-sm text-white outline-none focus:border-teal-300/60"
                    autoComplete="current-password"
                    required
                  />
                </label>

                {error && <p className="rounded-md border border-red-300/20 bg-red-400/[0.08] p-3 text-sm text-red-100">{error}</p>}

                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Entrando...' : 'Entrar'}
                </Button>

                <button
                  type="button"
                  onClick={startGoogleLogin}
                  className="inline-flex min-h-11 w-full items-center justify-center rounded-md border border-white/12 bg-white/[0.04] px-4 text-sm font-bold text-slate-100 transition hover:border-teal-300/40 hover:bg-white/[0.07]"
                >
                  Entrar com Google
                </button>
              </form>
            ) : (
              <form className="space-y-4" onSubmit={onMfaSubmit}>
                <div>
                  <p className="text-sm font-bold text-white">Verificacao MFA</p>
                  <p className="mt-1 text-sm text-slate-300">Digite o codigo de 6 digitos do seu autenticador.</p>
                </div>
                <input
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={6}
                  value={mfaCode}
                  onChange={event=>setMfaCode(event.target.value)}
                  className="h-12 w-full rounded-md border border-white/10 bg-slate-950 px-3 text-center text-lg font-black tracking-[0.25em] text-white outline-none focus:border-teal-300/60"
                  autoComplete="one-time-code"
                  required
                />
                {error && <p className="rounded-md border border-red-300/20 bg-red-400/[0.08] p-3 text-sm text-red-100">{error}</p>}
                <Button type="submit" className="w-full" disabled={loading}>
                  {loading ? 'Verificando...' : 'Verificar'}
                </Button>
                <button type="button" className="text-sm font-bold text-slate-300 hover:text-white" onClick={()=>setPendingMfa(null)}>
                  Voltar para login
                </button>
              </form>
            )}

            <div className="mt-5 border-t border-white/10 pt-4 text-xs text-slate-400">
              Precisa configurar MFA? <Link href="/mfa" className="font-bold text-teal-200">Abrir configuracao</Link>
            </div>
          </div>
        </div>
      </section>
    </main>
  )
}
