"use client"

import React from 'react'
import {privacyConsentChecklist} from '@/lib/privacyConsent'

export default function PrivacyConsentChecklist({
  compact = false,
  title = 'Privacidade por design',
}:{
  compact?: boolean
  title?: string
}){
  return (
    <div className={`privacy-consent-checklist ${compact ? 'privacy-consent-checklist--compact' : ''}`}>
      {!compact && (
        <div className="mb-4">
          <div className="app-label text-cyan-200/90">{title}</div>
          <p className="app-muted-text mt-2 text-sm">
            Proteção assistida com consentimento — não monitoramento automático.
          </p>
        </div>
      )}
      <ul className="privacy-consent-grid">
        {privacyConsentChecklist.map(item=> (
          <li key={item.id} className="privacy-consent-item">
            <span className="privacy-consent-mark" aria-hidden="true">
              {item.label.charAt(0)}
            </span>
            <div className="min-w-0">
              <div className="text-sm font-semibold text-white">{item.label}</div>
              {!compact && (
                <p className="mt-1 text-xs leading-5 text-slate-400">{item.detail}</p>
              )}
            </div>
          </li>
        ))}
      </ul>
    </div>
  )
}
