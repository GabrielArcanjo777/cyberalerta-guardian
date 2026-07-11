"use client"

import Link from 'next/link'
import React, {useCallback, useEffect, useRef, useState} from 'react'
import Button from '@/components/Button'
import ProtectedRoute from '@/components/ProtectedRoute'
import {getEvolutionStatus, getEvolutionQr, postEvolutionReconnect, getTrustedContactSettings, putTrustedContactSettings, type TrustedContactSettings} from '@/lib/api'
import {EvolutionConnectionState} from '@/lib/types'

const STATE_LABEL: Record<string, string> = {
  not_configured: 'Não configurado',
  unreachable: 'Evolution offline',
  close: 'Desconectado',
  connecting: 'Aguardando pareamento',
  open: 'Conectado',
  unknown: 'Desconhecido',
}

const STATE_COLOR: Record<string, string> = {
  not_configured: '#9aa0a6',
  unreachable: '#c9791f',
  close: '#c23b34',
  connecting: '#2f8f8a',
  open: '#2e9e5b',
  unknown: '#9aa0a6',
}

const PHONE_RE = /^\+?\d{10,15}$/

function PhoneField({label, hint, placeholder, value, onChange}:{
  label:string, hint:string, placeholder:string, value:string, onChange:(v:string)=>void,
}){
  return (
    <div style={{flex:1, minWidth:220}}>
      <label style={{display:'block', fontSize:13, fontWeight:600, margin:'0 0 4px'}}>{label}</label>
      <input
        type="tel"
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
        style={{
          width:'100%', height:42, borderRadius:8,
          border:'1px solid #d2d6cf', padding:'0 12px',
          fontSize:15, fontFamily:'monospace',
        }}
      />
      <p style={{fontSize:12, color:'#8b96a3', margin:'4px 0 0'}}>{hint}</p>
    </div>
  )
}

function TrustedContactSection(){
  const [settings, setSettings] = useState<TrustedContactSettings | null>(null)
  const [protectedInput, setProtectedInput] = useState('')
  const [trustedInput, setTrustedInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [msg, setMsg] = useState<{text:string, ok:boolean} | null>(null)

  useEffect(()=>{
    getTrustedContactSettings()
      .then(s => {
        setSettings(s)
        setProtectedInput(s.protected_number)
        setTrustedInput(s.trusted_contact)
      })
      .catch(()=>{})
  },[])

  async function save(){
    const p = protectedInput.trim()
    const t = trustedInput.trim()
    if(p && !PHONE_RE.test(p)){
      setMsg({text:'Número da pessoa protegida inválido. Use +DDI + 10-15 dígitos.', ok:false}); return
    }
    if(t && !PHONE_RE.test(t)){
      setMsg({text:'Contato de confiança inválido. Use +DDI + 10-15 dígitos.', ok:false}); return
    }
    setSaving(true)
    setMsg(null)
    try{
      const next = await putTrustedContactSettings({protected_number: p, trusted_contact: t})
      setSettings(next)
      setProtectedInput(next.protected_number)
      setTrustedInput(next.trusted_contact)
      setMsg({text:'Configuração salva.', ok:true})
    }catch(e){
      setMsg({text: e instanceof Error ? e.message : 'Erro ao salvar.', ok: false})
    }finally{
      setSaving(false)
    }
  }

  const hasContact = !!(settings?.trusted_contact)
  const isDryRun = settings?.dry_run ?? true
  const isRealSendEnabled = settings?.beta_real_send_enabled ?? false
  const changed =
    protectedInput.trim() !== (settings?.protected_number ?? '') ||
    trustedInput.trim() !== (settings?.trusted_contact ?? '')

  return (
    <section style={{marginTop:32, borderTop:'1px solid #d2d6cf', paddingTop:24}}>
      <p style={{fontSize:12, letterSpacing:'0.08em', textTransform:'uppercase', color:'#8b96a3', margin:'0 0 8px'}}>
        Pessoa protegida e contato de confiança
      </p>
      <h2 style={{fontSize:22, margin:'0 0 4px'}}>Quem é protegido e quem o bot deve alertar?</h2>
      <p style={{color:'#8b96a3', maxWidth:560, margin:'0 0 16px'}}>
        Cadastre o número da pessoa protegida (cujas mensagens são analisadas) e o número do contato
        de confiança que recebe o alerta. O bot nunca responde ao remetente e nunca escreve para a
        pessoa protegida — só envia o alerta para o contato de confiança, e apenas em golpe explícito.
      </p>

      <div style={{display:'flex', gap:12, flexWrap:'wrap', alignItems:'flex-end'}}>
        <PhoneField
          label="Número da pessoa protegida (vítima)"
          hint="Número monitorado. Ex: +5511977776666"
          placeholder="+5511977776666"
          value={protectedInput}
          onChange={v => { setProtectedInput(v); setMsg(null) }}
        />
        <PhoneField
          label="Contato de confiança (recebe o alerta)"
          hint="Único destino dos alertas. Ex: +5511999990001"
          placeholder="+5511999990001"
          value={trustedInput}
          onChange={v => { setTrustedInput(v); setMsg(null) }}
        />
        <Button onClick={save} disabled={saving || !changed}>
          {saving ? 'Salvando…' : 'Salvar'}
        </Button>
      </div>

      {msg && (
        <p style={{
          margin:'10px 0 0', padding:'8px 12px', borderRadius:8, fontSize:14,
          background: msg.ok ? '#eef7f1' : '#fbe9e7',
          color: msg.ok ? '#2e7d4f' : '#c23b34',
        }}>{msg.text}</p>
      )}

      <div style={{
        marginTop:16, padding:14, borderRadius:10,
        border: `1px solid ${hasContact ? '#cfe8d8' : '#e8dcc9'}`,
        background: hasContact ? '#f5faf7' : '#fdf8f0',
      }}>
        <p style={{margin:0, fontSize:14}}>
          <strong>Status do envio:</strong>{' '}
          {!hasContact && 'Nenhum contato de confiança configurado — alertas simulados.'}
          {hasContact && isDryRun && 'Contato configurado, mas DRY_RUN está ativo — alertas simulados.'}
          {hasContact && !isDryRun && !isRealSendEnabled && 'Contato configurado, mas BETA_REAL_SEND_ENABLED está desligado — alertas simulados.'}
          {hasContact && !isDryRun && isRealSendEnabled && 'Envio real ativo. Alertas serão enviados via WhatsApp.'}
        </p>
        {hasContact && isDryRun && (
          <p style={{margin:'6px 0 0', fontSize:13, color:'#8b96a3'}}>
            Para ativar envio real: defina <code>DRY_RUN=false</code> e <code>BETA_REAL_SEND_ENABLED=true</code> no <code>.env</code> do backend.
            Adicione o número em <code>BETA_ALLOWED_RECIPIENTS</code> se <code>BETA_REQUIRE_ALLOWED_RECIPIENT=true</code>.
          </p>
        )}
      </div>
    </section>
  )
}

export default function WhatsAppSetupPage(){
  const [status,setStatus] = useState<EvolutionConnectionState | null>(null)
  const [loading,setLoading] = useState(false)
  const [error,setError] = useState<string | null>(null)
  const timer = useRef<ReturnType<typeof setInterval> | null>(null)

  const refresh = useCallback(async (withQr:boolean)=>{
    try{
      const next = withQr ? await getEvolutionQr() : await getEvolutionStatus()
      setStatus(next)
      setError(null)
      return next
    }catch{
      setError('Não foi possível falar com o backend. Faça login novamente e confirme se a API está no ar.')
      return null
    }
  },[])

  useEffect(()=>{
    let active = true
    const tick = async ()=>{
      const current = await refresh(true)
      if(!active) return
      if(current && current.connected && timer.current){
        clearInterval(timer.current)
        timer.current = null
      }
    }
    tick()
    timer.current = setInterval(tick, 4000)
    return ()=>{ active = false; if(timer.current) clearInterval(timer.current) }
  },[refresh])

  async function reconnect(){
    setLoading(true)
    setError(null)
    try{
      setStatus(await postEvolutionReconnect())
    }catch{
      setError('Falha ao reconectar. Confirme se a Evolution API está rodando.')
    }finally{
      setLoading(false)
    }
  }

  const state = status?.state ?? 'unknown'
  const label = STATE_LABEL[state] ?? state
  const color = STATE_COLOR[state] ?? '#9aa0a6'

  return (
    <ProtectedRoute>
      <main style={{maxWidth:720, margin:'0 auto', padding:'40px 20px'}}>
        <p style={{fontSize:12, letterSpacing:'0.08em', textTransform:'uppercase', color:'#8b96a3'}}>
          Canal WhatsApp · Evolution API
        </p>
        <h1 style={{fontSize:28, margin:'8px 0 4px'}}>Conectar WhatsApp</h1>
        <p style={{color:'#8b96a3', maxWidth:560}}>
          Pareie um número de WhatsApp escaneando o QR code, igual ao WhatsApp Web.
          O CyberAlerta usa esse número para receber mensagens suspeitas e alertar o responsável.
        </p>

        <div style={{display:'flex', alignItems:'center', gap:10, margin:'20px 0'}}>
          <span aria-hidden style={{width:10, height:10, borderRadius:'50%', background:color, display:'inline-block'}} />
          <strong>{label}</strong>
          {status?.instance && <span style={{color:'#8b96a3'}}>· instância {status.instance}</span>}
        </div>

        {error && (
          <p role="alert" style={{background:'#fbe9e7', color:'#c23b34', padding:'10px 14px', borderRadius:8}}>{error}</p>
        )}

        {status?.state === 'not_configured' && (
          <div style={{border:'1px solid #d2d6cf', borderRadius:10, padding:16}}>
            <p style={{margin:0}}>
              Configure <code>EVOLUTION_API_URL</code>, <code>EVOLUTION_API_KEY</code> e{' '}
              <code>EVOLUTION_INSTANCE_NAME</code> no <code>.env</code> do backend e suba a Evolution API
              (Docker) para habilitar o pareamento.
            </p>
          </div>
        )}

        {status?.connected && (
          <div style={{border:'1px solid #cfe8d8', background:'#eef7f1', borderRadius:10, padding:16}}>
            <strong style={{color:'#2e7d4f'}}>WhatsApp conectado.</strong>
            <p style={{margin:'6px 0 0', color:'#3a4450'}}>
              O número está pareado e pronto para receber mensagens. Você pode fechar esta página.
            </p>
          </div>
        )}

        {status && !status.connected && status.qr_base64 && (
          <div style={{display:'flex', flexDirection:'column', alignItems:'center', gap:12, border:'1px solid #d2d6cf', borderRadius:12, padding:20}}>
            {/* eslint-disable-next-line @next/next/no-img-element */}
            <img src={status.qr_base64} alt="QR code para parear o WhatsApp" width={260} height={260} style={{display:'block'}} />
            <p style={{margin:0, textAlign:'center', color:'#3a4450'}}>
              {status.detail ?? 'Abra o WhatsApp > Aparelhos conectados > Conectar aparelho e escaneie.'}
            </p>
            {status.pairing_code && (
              <p style={{margin:0}}>Código de pareamento: <code>{status.pairing_code}</code></p>
            )}
          </div>
        )}

        {status && !status.connected && !status.qr_base64 && status.state !== 'not_configured' && (
          <div style={{border:'1px solid #d2d6cf', borderRadius:10, padding:16}}>
            <p style={{margin:0}}>{status.detail ?? 'Sessão indisponível. Tente reconectar.'}</p>
          </div>
        )}

        <div style={{display:'flex', gap:10, marginTop:20}}>
          <Button onClick={()=>refresh(true)} disabled={loading}>Atualizar</Button>
          <Button onClick={reconnect} disabled={loading || status?.state === 'not_configured'}>
            {loading ? 'Reconectando…' : 'Reconectar'}
          </Button>
        </div>

        <TrustedContactSection />

        <p style={{marginTop:24, fontSize:13, color:'#8b96a3', borderTop:'1px dashed #d2d6cf', paddingTop:16}}>
          Canal não-oficial (WhatsApp Web/Baileys): risco de bloqueio do número e de queda de sessão. Uso de portfólio/demo, não produção.
        </p>

        <p style={{marginTop:8}}>
          <Link href="/admin" style={{color:'#1f5f5b'}}>← Voltar ao painel</Link>
        </p>
      </main>
    </ProtectedRoute>
  )
}
