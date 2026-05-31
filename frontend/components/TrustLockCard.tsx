import React from 'react'

export default function TrustLockCard({activated,reason,message}:{activated:boolean,reason:string,message:string}){
  return (
    <div className="overflow-hidden rounded-lg border border-slate-800 bg-slate-950 text-white shadow-[0_18px_42px_rgba(15,23,42,0.16)]">
      <div className="flex items-center justify-between border-b border-white/10 px-5 py-4">
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.22em] text-cyan-300">Trust Lock Console</div>
          <div className="mt-1 text-xl font-semibold tracking-tight">{activated ? 'PAUSADO' : 'MONITORANDO'}</div>
        </div>
        <div className={`h-3 w-3 rounded-full ${activated ? 'bg-red-400 shadow-[0_0_18px_rgba(248,113,113,0.9)]' : 'bg-emerald-400'}`} />
      </div>
      <div className="space-y-4 px-5 py-5">
        <div className="rounded-lg border border-white/10 bg-white/[0.04] p-4">
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Reason</div>
          <p className="mt-2 text-sm leading-6 text-slate-200">{reason}</p>
        </div>
        <div>
          <div className="text-xs font-semibold uppercase tracking-[0.18em] text-slate-400">Guardian Message</div>
          <p className="mt-2 text-base font-semibold leading-6 text-white">{message}</p>
        </div>
        <div className="grid grid-cols-3 gap-2 text-center text-[11px] font-bold uppercase tracking-wide text-slate-300">
          <div className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-2">Quarantine</div>
          <div className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-2">Verify</div>
          <div className="rounded-md border border-white/10 bg-white/[0.04] px-2 py-2">Escalate</div>
        </div>
      </div>
    </div>
  )
}
