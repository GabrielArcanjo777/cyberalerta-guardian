'use client'

import { useEffect } from 'react'
import { useRouter } from 'next/navigation'
import { postLogout } from '@/lib/api'
import { isTauriRuntime } from '@/lib/runtime'

// So faz algo dentro do shell Windows (Tauri) — no build Web normal,
// window.__TAURI_INTERNALS__ nao existe e o efeito e um no-op.
//
// cyberalerta://case/{id} ainda nao tem uma rota de detalhe de caso no
// Console Web (isso e escopo da Sprint 5 — integracao real com Case).
// Por enquanto so leva pro /admin, que e a visao mais proxima que existe;
// cyberalerta://pair nao se aplica ao Windows (quem pareia e o Android
// Companion) e fica so logado.
export default function TauriDeepLinkBridge() {
  const router = useRouter()

  useEffect(() => {
    if (!isTauriRuntime()) return

    let unlistenDeepLink: (() => void) | undefined
    let unlistenTray: (() => void) | undefined
    let cancelled = false

    import('@tauri-apps/api/event').then(async ({ listen }) => {
      if (cancelled) return
      unlistenTray = await listen('tray://disconnect-requested', async () => {
        try {
          await postLogout()
        } catch {
          // Sessao pode ja ter expirado no backend — segue pro /login de
          // qualquer forma, e o objetivo real (sair) e alcancado.
        }
        router.push('/login')
      })
    })

    async function handleUrls(urls: string[]) {
      for (const raw of urls) {
        let url: URL
        try {
          url = new URL(raw)
        } catch {
          continue
        }
        if (url.host === 'case') {
          router.push('/admin')
        } else if (url.host === 'pair') {
          console.info('[deep-link] cyberalerta://pair recebido no Windows — ignorado (pareamento e so no Android Companion).')
        }
      }
    }

    import('@tauri-apps/plugin-deep-link').then(async ({ getCurrent, onOpenUrl }) => {
      if (cancelled) return
      const startUrls = await getCurrent()
      if (startUrls) await handleUrls(startUrls)
      unlistenDeepLink = await onOpenUrl(handleUrls)
    })

    return () => {
      cancelled = true
      unlistenDeepLink?.()
      unlistenTray?.()
    }
  }, [router])

  return null
}
