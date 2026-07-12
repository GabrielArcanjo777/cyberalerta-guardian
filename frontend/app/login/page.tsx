"use client"

import Link from 'next/link'
import {useRouter} from 'next/navigation'
import React, {FormEvent, useEffect, useState} from 'react'
import Button from '@/components/Button'
import {
  getAuthMe,
  getGoogleLoginUrl,
  postLogin,
  postMfaVerify,
  postRegister,
} from '@/lib/api'
import {LoginResponse} from '@/lib/types'
import {sanitizeAuthRedirect, DEFAULT_REDIRECT} from '@/lib/sanitize'

type AuthMode = 'login' | 'register'

function nextRouteFor(result: LoginResponse, redirect?: string | null){
  if(result.mfa_setup_required) return '/mfa'
  const safe = sanitizeAuthRedirect(redirect)
  if(safe) return safe
  return DEFAULT_REDIRECT
}

function authErrorMessage(error: unknown, fallback: string){
  if(error instanceof Error && error.message) return error.message
  return fallback
}

const googleFailureMessages: Record<string, string> = {
  config: 'Google OAuth nao esta configurado corretamente no backend.',
  state: 'Sessao de autenticacao expirada. Tente novamente.',
  token: 'Falha ao validar resposta do Google.',
  user: 'Conta Google nao autorizada para este ambiente.',
  unknown: 'Nao foi possivel concluir o login com Google. Tente novamente.',
}

export default function LoginPage(){
  const router = useRouter()
  const [mode,setMode] = useState<AuthMode>('login')
  const [email,setEmail] = useState('')
  const [fullName,setFullName] = useState('')
  const [password,setPassword] = useState('')
  const [passwordConfirm,setPasswordConfirm] = useState('')
  const [mfaCode,setMfaCode] = useState('')
  const [pendingMfa,setPendingMfa] = useState<LoginResponse | null>(null)
  const [loading,setLoading] = useState(false)
  const [error,setError] = useState<string | null>(null)
  const [notice,setNotice] = useState<string | null>(null)

  const redirect = typeof window !== 'undefined'
    ? new URLSearchParams(window.location.search).get('redirect')
    : null

  useEffect(()=>{
    const query = new URLSearchParams(window.location.search)
    const google = query.get('google')
    const reason = query.get('reason')
    const auth = query.get('auth')
    if(auth === 'google'){
      setNotice('Login com Google concluido.')
    }
    if(google === 'disabled'){
      setError('Google OAuth esta desabilitado no backend. Use login local ou configure as variaveis GOOGLE_* no .env.')
    }
    if(google === 'not_configured'){
      setError('Google OAuth esta quase pronto, mas ainda falta GOOGLE_CLIENT_SECRET no .env local. O client ID ja pode ficar salvo com seguranca fora do Git.')
    }
    if(google === 'failed'){
      setError(
        reason && googleFailureMessages[reason]
          ? googleFailureMessages[reason]
          : 'Nao foi possivel concluir o login com Google. Verifique credenciais, redirect URI e dominio permitido.'
      )
    }
    if(google === 'mfa_required'){
      setError('Esta conta Google exige MFA local. Entre com email e senha para concluir a verificacao.')
    }
  },[])

  // If a session is already active, don't show the login form again — send the
  // user straight to their console. This makes the header's "Acessar console"
  // link land on the app instead of looking like it logged them out.
  useEffect(()=>{
    let active = true
    getAuthMe()
      .then((session)=>{
        if(!active || !session.user) return
        const dest = sanitizeAuthRedirect(redirect) || DEFAULT_REDIRECT
        router.replace(dest)
      })
      .catch(()=>{})
    return ()=>{ active = false }
  },[router, redirect])

  async function onSubmit(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    setLoading(true)
    setError(null)
    setNotice(null)
    try{
      const result = await postLogin({email, password})
      if(result.mfa_required){
        setPendingMfa(result)
        return
      }
      router.push(nextRouteFor(result, redirect))
    }catch(error){
      setError(authErrorMessage(error, 'Credenciais invalidas.'))
    }finally{
      setLoading(false)
    }
  }

  async function onRegisterSubmit(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    setLoading(true)
    setError(null)
    setNotice(null)
    try{
      if(password !== passwordConfirm){
        throw new Error('As senhas nao conferem.')
      }
      const result = await postRegister({email, full_name: fullName, password})
      router.push(nextRouteFor(result, redirect))
    }catch(error){
      setError(authErrorMessage(error, 'Nao foi possivel criar a conta.'))
    }finally{
      setLoading(false)
    }
  }

  async function onMfaSubmit(event:FormEvent<HTMLFormElement>){
    event.preventDefault()
    if(!pendingMfa?.temporary_token) return
    setLoading(true)
    setError(null)
    setNotice(null)
    try{
      const result = await postMfaVerify(pendingMfa.temporary_token, mfaCode)
      router.push(nextRouteFor(result, redirect))
    }catch(error){
      setError(authErrorMessage(error, 'Codigo MFA invalido.'))
    }finally{
      setLoading(false)
    }
  }

  function startGoogleLogin(){
    window.location.assign(getGoogleLoginUrl())
  }

  return (
    <div className="guardian-auth-page">
      <div className="guardian-auth-grid" aria-hidden="true" />
      <div className="guardian-auth-glow guardian-auth-glow-a" aria-hidden="true" />
      <div className="guardian-auth-glow guardian-auth-glow-b" aria-hidden="true" />
      <div className="guardian-auth-scanline" aria-hidden="true" />

      <section className="guardian-auth-shell">
        <div className="guardian-auth-left">
          <div className="guardian-auth-brand">
            <span className="guardian-auth-brand-mark">
              <span className="guardian-auth-brand-dot" />
            </span>
            <span className="guardian-auth-brand-name">CYBERALERTA GUARDIAN</span>
          </div>

          <div className="guardian-auth-left-content">
            <span className="guardian-auth-eyebrow">
              <span className="guardian-auth-eyebrow-dot" />
              ACESSO SEGURO
            </span>
            <h1 className="guardian-auth-title">
              Entre no painel do Guardian.
            </h1>
            <p className="guardian-auth-subtitle">
              Acesse para revisar alertas, decisoes de risco e trilhas de auditoria. Toda sessao e protegida em cookie HttpOnly, com MFA disponivel para contas administrativas.
            </p>

            <div className="guardian-auth-trace" aria-hidden="true">
              <div className="guardian-auth-trace-row">
                <span className="guardian-auth-trace-label">SYS_AUTH</span>
                <span className="guardian-auth-trace-value">ready</span>
              </div>
              <div className="guardian-auth-trace-row">
                <span className="guardian-auth-trace-label">TRUST_LOCK</span>
                <span className="guardian-auth-trace-value guardian-auth-trace-value-ok">active</span>
              </div>
              <div className="guardian-auth-trace-row">
                <span className="guardian-auth-trace-label">CHANNEL</span>
                <span className="guardian-auth-trace-value">http_cookie</span>
              </div>
              <div className="guardian-auth-trace-row">
                <span className="guardian-auth-trace-label">OAUTH</span>
                <span className="guardian-auth-trace-value">controlled</span>
              </div>
              <div className="guardian-auth-trace-line" />
              <div className="guardian-auth-trace-prompt">
                <span className="guardian-auth-trace-cursor">$</span>
                <span className="guardian-auth-trace-cursor-blink">_</span>
              </div>
            </div>
          </div>

          <div className="guardian-auth-left-footer">
            <span>Beta Tecnico Local</span>
            <span className="guardian-auth-left-footer-dot" />
            <span>Demo Local</span>
          </div>
        </div>

        <div className="guardian-auth-right">
          <div className="guardian-auth-panel">
            <div className="guardian-auth-tabs">
              <button
                type="button"
                onClick={()=>{
                  setMode('login')
                  setPendingMfa(null)
                  setError(null)
                }}
                className={`guardian-auth-tab ${mode === 'login' && !pendingMfa ? 'is-active' : ''}`}
              >
                Entrar
              </button>
              <button
                type="button"
                onClick={()=>{
                  setMode('register')
                  setPendingMfa(null)
                  setError(null)
                }}
                className={`guardian-auth-tab ${mode === 'register' && !pendingMfa ? 'is-active' : ''}`}
              >
                Criar conta
              </button>
            </div>

            {notice && <div className="guardian-auth-notice guardian-auth-notice-ok">{notice}</div>}
            {error && <div className="guardian-auth-notice guardian-auth-notice-error">{error}</div>}

            {!pendingMfa && mode === 'login' && (
              <form className="guardian-auth-form" onSubmit={onSubmit}>
                <label className="guardian-auth-label">
                  Email
                  <input
                    type="email"
                    value={email}
                    onChange={event=>setEmail(event.target.value)}
                    className="guardian-auth-input"
                    autoComplete="email"
                    required
                  />
                </label>
                <label className="guardian-auth-label">
                  Senha
                  <input
                    type="password"
                    value={password}
                    onChange={event=>setPassword(event.target.value)}
                    className="guardian-auth-input"
                    autoComplete="current-password"
                    required
                  />
                </label>

                <Button type="submit" className="guardian-auth-button-primary" disabled={loading}>
                  {loading ? 'Entrando...' : 'Entrar'}
                </Button>

                <button
                  type="button"
                  onClick={startGoogleLogin}
                  className="guardian-auth-button-google"
                >
                  Entrar com Google
                </button>
              </form>
            )}

            {!pendingMfa && mode === 'register' && (
              <form className="guardian-auth-form" onSubmit={onRegisterSubmit}>
                <label className="guardian-auth-label">
                  Nome
                  <input
                    type="text"
                    value={fullName}
                    onChange={event=>setFullName(event.target.value)}
                    className="guardian-auth-input"
                    autoComplete="name"
                    required
                  />
                </label>
                <label className="guardian-auth-label">
                  Email
                  <input
                    type="email"
                    value={email}
                    onChange={event=>setEmail(event.target.value)}
                    className="guardian-auth-input"
                    autoComplete="email"
                    required
                  />
                </label>
                <label className="guardian-auth-label">
                  Senha
                  <input
                    type="password"
                    value={password}
                    onChange={event=>setPassword(event.target.value)}
                    className="guardian-auth-input"
                    autoComplete="new-password"
                    required
                  />
                </label>
                <label className="guardian-auth-label">
                  Confirmar senha
                  <input
                    type="password"
                    value={passwordConfirm}
                    onChange={event=>setPasswordConfirm(event.target.value)}
                    className="guardian-auth-input"
                    autoComplete="new-password"
                    required
                  />
                </label>

                <Button type="submit" className="guardian-auth-button-primary" disabled={loading}>
                  {loading ? 'Criando conta...' : 'Criar conta segura'}
                </Button>
                <p className="guardian-auth-hint">
                  Cadastros pela interface entram como viewer. Perfis admin devem ser criados por fluxo administrativo.
                </p>
              </form>
            )}

            {pendingMfa && (
              <form className="guardian-auth-form" onSubmit={onMfaSubmit}>
                <div className="guardian-auth-mfa-header">
                  <p className="guardian-auth-mfa-title">Verificacao MFA</p>
                  <p className="guardian-auth-mfa-subtitle">Digite o codigo de 6 digitos do seu autenticador.</p>
                </div>
                <input
                  inputMode="numeric"
                  pattern="[0-9]*"
                  maxLength={6}
                  value={mfaCode}
                  onChange={event=>setMfaCode(event.target.value)}
                  className="guardian-auth-input guardian-auth-input-mfa"
                  autoComplete="one-time-code"
                  required
                />
                <Button type="submit" className="guardian-auth-button-primary" disabled={loading}>
                  {loading ? 'Verificando...' : 'Verificar'}
                </Button>
                <button type="button" className="guardian-auth-back" onClick={()=>setPendingMfa(null)}>
                  Voltar para login
                </button>
              </form>
            )}

            <div className="guardian-auth-panel-footer">
              <span>Sessao protegida por cookie HttpOnly</span>
              <span className="guardian-auth-sep">·</span>
              <span>Google OAuth controlado</span>
              <span className="guardian-auth-sep">·</span>
              <span>MFA para contas administrativas</span>
            </div>

            <div className="guardian-auth-panel-link">
              Precisa configurar MFA? <Link href="/mfa" className="guardian-auth-link">Abrir configuracao</Link>
            </div>
          </div>
        </div>
      </section>
    </div>
  )
}
