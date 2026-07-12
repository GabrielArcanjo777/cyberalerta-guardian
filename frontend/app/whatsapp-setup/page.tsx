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
  unreachable: '#f5c06a',
  close: '#fb7185',
  connecting: '#5eead4',
  open: '#34d399',
  unknown: '#9aa0a6',
}

const PHONE_RE = /^\+?\d{10,15}$/

// Tema escuro explícito (a página não herda .guardian-product-page)
const INK = '#f1f5f9'
const MUTED = '#94a3b8'
const PANEL_BORDER = '1px solid rgba(255,255,255,0.14)'
const PANEL_BG = 'rgba(8,15,30,0.6)'
const INPUT_STYLE: React.CSSProperties = {
  width:'100%', height:42, borderRadius:8,
  border: PANEL_BORDER, padding:'0 12px',
  fontSize:15, fontFamily:'monospace',
  background:'#0b1526', color: INK, caretColor: INK,
}

function PhoneField({label, hint, placeholder, value, onChange}:{
  label:string, hint:string, placeholder:string, value:string, onChange:(v:string)=>void,
}){
  return (
    <div style={{flex:1, minWidth:220}}>
      <label style={{display:'block', fontSize:13, fontWeight:600, margin:'0 0 4px', color: INK}}>{label}</label>
      <input
        type="tel"
        placeholder={placeholder}
        value={value}
        onChange={e => onChange(e.target.value)}
        style={INPUT_STYLE}
      />
      <p style={{fontSize:12, color: MUTED, margin:'4px 0 0'}}>{hint}</p>
    </div>
  )
}

function ToggleRow({label, description, on, danger, disabled, busy, onToggle}:{
  label:string, description:string, on:boolean, danger?:boolean, disabled?:boolean, busy?:boolean,
  onToggle:()=>void,
}){
  const activeColor = danger ? '#fb7185' : '#34d399'
  return (
    <div style={{
      display:'flex', alignItems:'center', justifyContent:'space-between', gap:14,
      padding:'12px 14px', borderRadius:10, border: PANEL_BORDER, background: PANEL_BG,
    }}>
      <div style={{minWidth:0}}>
        <p style={{margin:0, fontSize:14, fontWeight:700, color: INK}}>{label}</p>
        <p style={{margin:'3px 0 0', fontSize:12.5, color: MUTED, lineHeight:1.5}}>{description}</p>
      </div>
      <button
        type="button"
        role="switch"
        aria-checked={on}
        aria-label={label}
        disabled={disabled || busy}
        onClick={onToggle}
        style={{
          flex:'0 0 auto', width:58, height:30, borderRadius:999,
          border:`1px solid ${on ? activeColor : 'rgba(255,255,255,0.25)'}`,
          background: on ? (danger ? 'rgba(251,113,133,0.25)' : 'rgba(52,211,153,0.25)') : 'rgba(255,255,255,0.06)',
          position:'relative', cursor: disabled || busy ? 'not-allowed' : 'pointer',
          opacity: disabled ? 0.45 : 1, transition:'background 160ms ease',
        }}
      >
        <span aria-hidden style={{
          position:'absolute', top:3, left: on ? 30 : 3,
          width:22, height:22, borderRadius:'50%',
          background: on ? activeColor : '#cbd5e1',
          transition:'left 160ms ease',
        }} />
      </button>
    </div>
  )
}

function TrustedContactSection(){
  const [settings, setSettings] = useState<TrustedContactSettings | null>(null)
  const [protectedInput, setProtectedInput] = useState('')
  const [trustedInput, setTrustedInput] = useState('')
  const [saving, setSaving] = useState(false)
  const [toggling, setToggling] = useState(false)
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

  async function toggle(update: {dry_run?: boolean, beta_real_send_enabled?: boolean}){
    setToggling(true)
    setMsg(null)
    try{
      const next = await putTrustedContactSettings(update)
      setSettings(next)
      setMsg({text:'Configuração de envio atualizada.', ok:true})
    }catch(e){
      setMsg({text: e instanceof Error ? e.message : 'Erro ao atualizar.', ok: false})
    }finally{
      setToggling(false)
    }
  }

  const hasContact = !!(settings?.trusted_contact)
  const isDryRun = settings?.dry_run ?? true
  const isRealSendEnabled = settings?.beta_real_send_enabled ?? false
  const realSendActive = hasContact && !isDryRun && isRealSendEnabled
  const changed =
    protectedInput.trim() !== (settings?.protected_number ?? '') ||
    trustedInput.trim() !== (settings?.trusted_contact ?? '')

  return (
    <section style={{marginTop:32, borderTop:'1px solid rgba(255,255,255,0.12)', paddingTop:24}}>
      <p style={{fontSize:12, letterSpacing:'0.08em', textTransform:'uppercase', color: MUTED, margin:'0 0 8px'}}>
        Pessoa protegida e contato de confiança
      </p>
      <h2 style={{fontSize:22, margin:'0 0 4px', color: INK}}>Quem é protegido e quem o bot deve alertar?</h2>
      <p style={{color: MUTED, maxWidth:560, margin:'0 0 16px'}}>
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
          margin:'12px 0 0', padding:'8px 12px', borderRadius:8, fontSize:14,
          border: `1px solid ${msg.ok ? 'rgba(52,211,153,0.4)' : 'rgba(251,113,133,0.4)'}`,
          background: msg.ok ? 'rgba(52,211,153,0.12)' : 'rgba(251,113,133,0.12)',
          color: msg.ok ? '#6ee7b7' : '#fda4af',
        }}>{msg.text}</p>
      )}

      <div style={{display:'grid', gap:10, marginTop:18}}>
        <ToggleRow
          label="Modo simulação (DRY_RUN)"
          description="Ligado: nenhuma mensagem real sai — alertas aparecem só no console. Desligue apenas quando quiser envio real."
          on={isDryRun}
          busy={toggling}
          onToggle={()=>toggle({dry_run: !isDryRun})}
        />
        <ToggleRow
          label="Envio real via WhatsApp (beta)"
          description={hasContact
            ? 'Autoriza o envio do alerta real ao contato de confiança (somente a ele — allowlist automática).'
            : 'Cadastre e salve um contato de confiança antes de ativar o envio real.'}
          on={isRealSendEnabled}
          danger
          disabled={!hasContact}
          busy={toggling}
          onToggle={()=>toggle({beta_real_send_enabled: !isRealSendEnabled})}
        />
      </div>

      <div style={{
        marginTop:14, padding:14, borderRadius:10,
        border: `1px solid ${realSendActive ? 'rgba(251,113,133,0.45)' : 'rgba(255,255,255,0.14)'}`,
        background: realSendActive ? 'rgba(251,113,133,0.1)' : PANEL_BG,
      }}>
        <p style={{margin:0, fontSize:14, color: INK}}>
          <strong style={{color: realSendActive ? '#fda4af' : '#5eead4'}}>Status do envio:</strong>{' '}
          {!hasContact && 'nenhum contato de confiança configurado — alertas apenas simulados.'}
          {hasContact && isDryRun && 'modo simulação ativo — alertas aparecem no console, nada é enviado.'}
          {hasContact && !isDryRun && !isRealSendEnabled && 'simulação desligada, mas envio real ainda não autorizado — nada é enviado.'}
          {realSendActive && 'ENVIO REAL ATIVO — alertas de golpe explícito serão enviados por WhatsApp ao contato de confiança.'}
        </p>
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
  // O provider às vezes devolve a string bruta do QR como "pairing code";
  // só mostramos quando for um código curto digitável.
  const pairingCode = status?.pairing_code && status.pairing_code.length <= 16
    ? status.pairing_code
    : null

  return (
    <ProtectedRoute>
      <main style={{maxWidth:720, margin:'0 auto', padding:'40px 20px'}}>
        <p style={{fontSize:12, letterSpacing:'0.08em', textTransform:'uppercase', color: MUTED}}>
          Canal WhatsApp · Evolution API
        </p>
        <h1 style={{fontSize:28, margin:'8px 0 4px', color: INK}}>Conectar WhatsApp</h1>
        <p style={{color: MUTED, maxWidth:560}}>
          Pareie um número de WhatsApp escaneando o QR code, igual ao WhatsApp Web.
          O CyberAlerta usa esse número para receber mensagens suspeitas e alertar o responsável.
        </p>

        <div style={{display:'flex', alignItems:'center', gap:10, margin:'20px 0'}}>
          <span aria-hidden style={{width:10, height:10, borderRadius:'50%', background:color, display:'inline-block'}} />
          <strong style={{color: INK}}>{label}</strong>
          {status?.instance && <span style={{color: MUTED}}>· instância {status.instance}</span>}
        </div>

        {error && (
          <p role="alert" style={{
            background:'rgba(251,113,133,0.12)', border:'1px solid rgba(251,113,133,0.4)',
            color:'#fda4af', padding:'10px 14px', borderRadius:8,
          }}>{error}</p>
        )}

        {status?.state === 'not_configured' && (
          <div style={{border: PANEL_BORDER, background: PANEL_BG, borderRadius:10, padding:16, color: INK}}>
            <p style={{margin:0}}>
              Configure <code>EVOLUTION_API_URL</code>, <code>EVOLUTION_API_KEY</code> e{' '}
              <code>EVOLUTION_INSTANCE_NAME</code> no <code>.env</code> do backend e suba a Evolution API
              (Docker) para habilitar o pareamento.
            </p>
          </div>
        )}

        {status?.connected && (
          <div style={{border:'1px solid rgba(52,211,153,0.45)', background:'rgba(52,211,153,0.1)', borderRadius:10, padding:16}}>
            <strong style={{color:'#6ee7b7'}}>WhatsApp conectado.</strong>
            <p style={{margin:'6px 0 0', color: INK}}>
              O número está pareado e pronto para receber mensagens. Você pode fechar esta página.
            </p>
          </div>
        )}

        {status && !status.connected && status.qr_base64 && (
          <div style={{
            display:'flex', flexDirection:'column', alignItems:'center', gap:12,
            border: PANEL_BORDER, background: PANEL_BG, borderRadius:12, padding:20,
            overflow:'hidden',
          }}>
            <div style={{background:'#ffffff', padding:12, borderRadius:10, lineHeight:0}}>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img src={status.qr_base64} alt="QR code para parear o WhatsApp" width={240} height={240} style={{display:'block'}} />
            </div>
            <p style={{margin:0, textAlign:'center', color: INK}}>
              {status.detail ?? 'Abra o WhatsApp > Aparelhos conectados > Conectar aparelho e escaneie.'}
            </p>
            {pairingCode && (
              <p style={{margin:0, color: INK, wordBreak:'break-all'}}>
                Código de pareamento: <code style={{color:'#5eead4'}}>{pairingCode}</code>
              </p>
            )}
          </div>
        )}

        {status && !status.connected && !status.qr_base64 && status.state !== 'not_configured' && (
          <div style={{border: PANEL_BORDER, background: PANEL_BG, borderRadius:10, padding:16, color: INK}}>
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

        <p style={{marginTop:24, fontSize:13, color: MUTED, borderTop:'1px dashed rgba(255,255,255,0.16)', paddingTop:16}}>
          Canal não-oficial (WhatsApp Web/Baileys): risco de bloqueio do número e de queda de sessão. Uso de portfólio/demo, não produção.
        </p>

        <p style={{marginTop:8}}>
          <Link href="/admin" style={{color:'#5eead4'}}>← Voltar ao painel</Link>
        </p>
      </main>
    </ProtectedRoute>
  )
}
