// Dentro do shell Windows (Tauri), o webview roda em tauri://localhost (ou
// http://tauri.localhost) — origem diferente da API cloud, e o cookie de
// sessao e SameSite=Lax, entao um fetch() normal do navegador simplesmente
// nao envia o cookie (CORS cross-site) e a CSP tambem bloquearia a chamada.
// @tauri-apps/plugin-http executa o request no lado Rust (reqwest), fora do
// contexto do navegador — sem CORS, sem SameSite, sem CSP connect-src — e
// mantem seu proprio cookie jar, entao a sessao httpOnly funciona igual ao
// Web sem o backend precisar saber que e um cliente diferente.
import { isTauriRuntime } from './runtime'

type FetchFn = typeof fetch

let fetchImplPromise: Promise<FetchFn> | null = null

async function resolveFetch(): Promise<FetchFn> {
  if (isTauriRuntime()) {
    const { fetch: tauriFetch } = await import('@tauri-apps/plugin-http')
    return tauriFetch as unknown as FetchFn
  }
  return fetch.bind(globalThis)
}

export async function apiFetch(input: RequestInfo | URL, init?: RequestInit): Promise<Response> {
  if (!fetchImplPromise) {
    fetchImplPromise = resolveFetch()
  }
  const impl = await fetchImplPromise
  return impl(input, init)
}
