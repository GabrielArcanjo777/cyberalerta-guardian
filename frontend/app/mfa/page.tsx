"use client"

import Link from 'next/link'
import {useRouter} from 'next/navigation'
import React, {FormEvent, useState} from 'react'
import Button from '@/components/Button'
import ProtectedRoute from '@/components/ProtectedRoute'
import {postMfaEnable, postMfaSetup, postMfaVerify, postMfaRegenerateRecoveryCodes} from '@/lib/api'
import {MFASetupResponse, RecoveryCodesResponse} from '@/lib/types'

export default function MFAPage(){
  const router = useRouter()
  const [setup,setSetup] = useState<MFASetupResponse | null>(null)
  const [enableCode,setEnableCode] = useState('')
  const [temporaryToken,setTemporaryToken] = useState('')
  const [verifyCode,setVerifyCode] = useState('')
  const [message,setMessage] = useState<string | null>(null)
  const [error,setError] = useState<string | null>(null)
  const [loading,setLoading] = useState(false)
  const [recoveryCodes,setRecoveryCodes] = useState<string[] | null>(null)
  const [codesSaved,setCodesSaved] = useState(false)

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
      const result: RecoveryCodesResponse = await postMfaEnable(enableCode)
      setMessage('MFA habilitado com sucesso. Salve os codigos de recuperacao abaixo.')
      setRecoveryCodes(result.recovery_codes)
      setCodesSaved(false)
      setSetup(null)
      setEnableCode('')
    }catch{
      setError('Codigo MFA invalido.')
    }finally{
      setLoading(false)
    }
  }

  async function regenerateCodes(){
    setLoading(true)
    setError(null)
    try{
      const result: RecoveryCodesResponse = await postMfaRegenerateRecoveryCodes()
      setMessage('Novos codigos de recuperacao gerados. Os anteriores foram invalidados.')
      setRecoveryCodes(result.recovery_codes)
      setCodesSaved(false)
    }catch{
      setError('Nao foi possivel gerar novos codigos.')
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
      setError('Token temporario, codigo MFA ou codigo de recuperacao invalido.')
    }finally{
      setLoading(false)
    }
  }

  return (
    <div className="guardian-mfa-page">
      <div className="guardian-mfa-grid" aria-hidden="true" />
      <div className="guardian-mfa-glow guardian-mfa-glow-a" aria-hidden="true" />
      <div className="guardian-mfa-glow guardian-mfa-glow-b" aria-hidden="true" />

      <section className="guardian-mfa-shell">
        <div className="guardian-mfa-header">
        <div className="guardian-mfa-brand">
            <span className="guardian-mfa-brand-mark">
              <span className="guardian-mfa-brand-dot" />
            </span>
            <span className="guardian-mfa-brand-name">CYBERALERTA GUARDIAN</span>
          </div>
          <span className="guardian-mfa-eyebrow">
            <span className="guardian-mfa-eyebrow-dot" />
            MFA / TOTP
          </span>
          <h1 className="guardian-mfa-title">Verificacao adicional para acesso privilegiado</h1>
          <p className="guardian-mfa-subtitle">
            Configure um autenticador TOTP para proteger acessos administrativos. O app nao registra codigos MFA em log.
          </p>
        </div>

        {recoveryCodes && (
          <div className="guardian-mfa-recovery">
            <h2 className="guardian-mfa-recovery-title">Codigos de Recuperacao</h2>
            <p className="guardian-mfa-recovery-subtitle">
              Salve estes codigos em um local seguro. Eles so aparecem uma vez e podem ser usados para acessar sua conta se perder o autenticador.
            </p>
            <div className="guardian-mfa-recovery-grid">
              {recoveryCodes.map((code, i) => (
                <div key={i} className="guardian-mfa-recovery-code">
                  {code}
                </div>
              ))}
            </div>
            <div className="guardian-mfa-recovery-actions">
              <Button type="button" variant="ghost" onClick={()=>{
                navigator.clipboard.writeText(recoveryCodes.join('\n'))
                setCodesSaved(true)
              }}>
                {codesSaved ? 'Copiado!' : 'Copiar codigos'}
              </Button>
              <span className="guardian-mfa-recovery-hint">
                {codesSaved ? 'Codigos copiados. Guarde em local seguro.' : 'Guarde antes de sair desta pagina.'}
              </span>
            </div>
          </div>
        )}

        <div className="guardian-mfa-grid-panels">
          <ProtectedRoute>
            {(user)=>(
              <div className="guardian-mfa-panel">
                <div className="guardian-mfa-panel-header">
                  <div>
                    <h2 className="guardian-mfa-panel-title">Configurar MFA</h2>
                    <p className="guardian-mfa-panel-email">{user.email}</p>
                  </div>
                  <span className={`guardian-mfa-badge ${user.mfa_enabled ? 'is-active' : 'is-inactive'}`}>
                    {user.mfa_enabled ? 'Ativo' : 'Inativo'}
                  </span>
                </div>

                {user.mfa_enabled && (
                  <div className="guardian-mfa-regen">
                    <Button type="button" variant="ghost" onClick={regenerateCodes} disabled={loading}>
                      {loading ? 'Gerando...' : 'Regenerar codigos de recuperacao'}
                    </Button>
                  </div>
                )}

                <Button type="button" className="guardian-mfa-button-primary" onClick={startSetup} disabled={loading}>
                  {loading ? 'Preparando...' : 'Gerar chave MFA'}
                </Button>

                {setup && (
                  <form className="guardian-mfa-form" onSubmit={enableMfa}>
                    <div className="guardian-mfa-qr-block">
                      {/* eslint-disable-next-line @next/next/no-img-element */}
                      <img
                        src={`data:image/svg+xml;base64,${setup.qr_code_base64}`}
                        alt="QR Code MFA"
                        width={160}
                        height={160}
                        className="guardian-mfa-qr"
                      />
                      <div className="guardian-mfa-manual">
                        <p className="guardian-mfa-manual-label">Chave manual</p>
                        <p className="guardian-mfa-manual-key">{setup.manual_secret}</p>
                      </div>
                    </div>
                    <label className="guardian-mfa-label">
                      Codigo de 6 digitos
                      <input
                        inputMode="numeric"
                        value={enableCode}
                        onChange={event=>setEnableCode(event.target.value)}
                        className="guardian-mfa-input"
                        required
                      />
                    </label>
                    <Button type="submit" className="guardian-mfa-button-primary" disabled={loading}>Habilitar MFA</Button>
                  </form>
                )}
              </div>
            )}
          </ProtectedRoute>

          <div className="guardian-mfa-panel">
            <h2 className="guardian-mfa-panel-title">Verificar login pendente</h2>
            <p className="guardian-mfa-panel-subtitle">
              Use esta opcao se voce recebeu um token temporario no fluxo de login MFA. Aceita codigo TOTP ou codigo de recuperacao.
            </p>
            <form className="guardian-mfa-form" onSubmit={verifyMfa}>
              <label className="guardian-mfa-label">
                Token temporario
                <input
                  value={temporaryToken}
                  onChange={event=>setTemporaryToken(event.target.value)}
                  className="guardian-mfa-input"
                  required
                />
              </label>
              <label className="guardian-mfa-label">
                Codigo MFA ou Recuperacao
                <input
                  inputMode="text"
                  value={verifyCode}
                  onChange={event=>setVerifyCode(event.target.value)}
                  className="guardian-mfa-input"
                  placeholder="123456 ou XXXX-XXXX"
                  required
                />
              </label>
              <Button type="submit" className="guardian-mfa-button-primary" disabled={loading}>Verificar</Button>
            </form>
          </div>
        </div>

        {message && <div className="guardian-mfa-message guardian-mfa-message-ok">{message}</div>}
        {error && <div className="guardian-mfa-message guardian-mfa-message-error">{error}</div>}

        <div className="guardian-mfa-footer-link">
          <Link href="/admin" className="guardian-mfa-link">Voltar para admin</Link>
        </div>
      </section>
    </div>
  )
}
