"use client"

import Link from 'next/link'
import Image from 'next/image'
import {useRouter} from 'next/navigation'
import React, {FormEvent, useState} from 'react'
import Button from '@/components/Button'
import Header from '@/components/Header'
import ProtectedRoute from '@/components/ProtectedRoute'
import {postMfaEnable, postMfaSetup, postMfaVerify} from '@/lib/api'
import {MFASetupResponse} from '@/lib/types'

export default function MFAPage(){
  const router = useRouter()
  const [setup,setSetup] = useState<MFASetupResponse | null>(null)
  const [enableCode,setEnableCode] = useState('')
  const [temporaryToken,setTemporaryToken] = useState('')
  const [verifyCode,setVerifyCode] = useState('')
  const [message,setMessage] = useState<string | null>(null)
  const [error,setError] = useState<string | null>(null)
  const [loading,setLoading] = useState(false)

  async function startSetup(){
    setLoading(true)
    setError(null)
    setMessage(null)
    try{
      setSetup(await postMfaSetup())
    }catch{
      setError('Nao foi possivel iniciar o MFA. Entre novamente e tente de novo.')
    }finally{
      setLoading(false)
    }
  }

  async function enableMfa(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    setLoading(true)
    setError(null)
    try{
      await postMfaEnable(enableCode)
      setMessage('MFA habilitado com sucesso.')
      setSetup(null)
      setEnableCode('')
    }catch{
      setError('Codigo MFA invalido.')
    }finally{
      setLoading(false)
    }
  }

  async function verifyMfa(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    setLoading(true)
    setError(null)
    try{
      const result = await postMfaVerify(temporaryToken, verifyCode)
      router.push(result.user?.role === 'admin' ? '/admin' : '/family-console')
    }catch{
      setError('Token temporario ou codigo MFA invalido.')
    }finally{
      setLoading(false)
    }
  }

  return (
    <main className="min-h-screen bg-slate-950 text-slate-50">
      <Header />
      <section className="mx-auto w-full max-w-5xl px-4 py-10">
        <div className="mb-8">
          <p className="text-xs font-black uppercase tracking-[0.18em] text-teal-200">MFA/TOTP</p>
          <h1 className="mt-3 text-3xl font-black text-white sm:text-4xl">Autenticacao em dois fatores</h1>
          <p className="mt-3 max-w-2xl text-sm leading-6 text-slate-300">
            Configure um autenticador TOTP para proteger acessos administrativos. O app nao registra codigos MFA em log.
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-2">
          <ProtectedRoute>
            {(user)=>(
              <div className="rounded-md border border-white/10 bg-slate-900/70 p-5">
                <div className="flex items-start justify-between gap-4">
                  <div>
                    <h2 className="text-lg font-black text-white">Configurar MFA</h2>
                    <p className="mt-1 text-sm text-slate-300">{user.email}</p>
                  </div>
                  <span className={`rounded-md border px-2.5 py-1 text-xs font-bold ${user.mfa_enabled ? 'border-teal-300/30 bg-teal-300/[0.12] text-teal-100' : 'border-amber-300/30 bg-amber-300/[0.12] text-amber-100'}`}>
                    {user.mfa_enabled ? 'Ativo' : 'Inativo'}
                  </span>
                </div>

                <Button type="button" className="mt-5 w-full" onClick={startSetup} disabled={loading}>
                  {loading ? 'Preparando...' : 'Gerar chave MFA'}
                </Button>

                {setup && (
                  <form className="mt-5 space-y-4" onSubmit={enableMfa}>
                    <div className="grid gap-4 sm:grid-cols-[160px_1fr] sm:items-start">
                      <Image
                        src={`data:image/svg+xml;base64,${setup.qr_code_base64}`}
                        alt="QR Code MFA"
                        width={160}
                        height={160}
                        unoptimized
                        className="h-40 w-40 rounded-md border border-white/10 bg-white p-2"
                      />
                      <div className="rounded-md border border-white/10 bg-slate-950 p-3">
                        <p className="text-xs font-bold uppercase text-slate-400">Chave manual</p>
                        <p className="mt-2 break-all font-mono text-sm text-teal-100">{setup.manual_secret}</p>
                      </div>
                    </div>
                    <label className="block text-sm font-semibold text-slate-200">
                      Codigo de 6 digitos
                      <input
                        inputMode="numeric"
                        value={enableCode}
                        onChange={event=>setEnableCode(event.target.value)}
                        className="mt-2 h-11 w-full rounded-md border border-white/10 bg-slate-950 px-3 text-sm text-white outline-none focus:border-teal-300/60"
                        required
                      />
                    </label>
                    <Button type="submit" className="w-full" disabled={loading}>Habilitar MFA</Button>
                  </form>
                )}
              </div>
            )}
          </ProtectedRoute>

          <div className="rounded-md border border-white/10 bg-slate-900/70 p-5">
            <h2 className="text-lg font-black text-white">Verificar login pendente</h2>
            <p className="mt-1 text-sm text-slate-300">
              Use esta opcao se voce recebeu um token temporario no fluxo de login MFA.
            </p>
            <form className="mt-5 space-y-4" onSubmit={verifyMfa}>
              <label className="block text-sm font-semibold text-slate-200">
                Temporary token
                <input
                  value={temporaryToken}
                  onChange={event=>setTemporaryToken(event.target.value)}
                  className="mt-2 h-11 w-full rounded-md border border-white/10 bg-slate-950 px-3 text-sm text-white outline-none focus:border-teal-300/60"
                  required
                />
              </label>
              <label className="block text-sm font-semibold text-slate-200">
                Codigo MFA
                <input
                  inputMode="numeric"
                  value={verifyCode}
                  onChange={event=>setVerifyCode(event.target.value)}
                  className="mt-2 h-11 w-full rounded-md border border-white/10 bg-slate-950 px-3 text-sm text-white outline-none focus:border-teal-300/60"
                  required
                />
              </label>
              <Button type="submit" className="w-full" disabled={loading}>Verificar</Button>
            </form>
          </div>
        </div>

        {message && <p className="mt-5 rounded-md border border-teal-300/20 bg-teal-300/[0.08] p-4 text-sm text-teal-100">{message}</p>}
        {error && <p className="mt-5 rounded-md border border-red-300/20 bg-red-400/[0.08] p-4 text-sm text-red-100">{error}</p>}

        <Link href="/admin" className="mt-6 inline-flex text-sm font-bold text-teal-200 hover:text-teal-100">
          Voltar para admin
        </Link>
      </section>
    </main>
  )
}
