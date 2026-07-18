// O app Windows (Tauri) e a casca do CONSOLE, nao uma copia do site
// publico inteiro (Plano Mestre v1.1, Secao 3.4): landing page, demos,
// simuladores e paginas educacionais ficam so na Web. Roda depois de
// `next build` (BUILD_TARGET=tauri) e remove do `out/` estatico tudo que
// nao e login/MFA/Admin/Console/whatsapp-setup antes do Tauri empacotar.
import { rm, readdir } from 'node:fs/promises'
import path from 'node:path'

const OUT_DIR = path.resolve(process.cwd(), 'out')

const CORE_ROUTES = ['login', 'mfa', 'admin', 'family-console', 'whatsapp-setup']

const ALWAYS_KEEP = new Set([
  '_next',
  '_not-found',
  '_not-found.html',
  '_not-found.txt',
  '404.html',
  'icon.svg',
  ...CORE_ROUTES,
  ...CORE_ROUTES.map((r) => `${r}.html`),
  ...CORE_ROUTES.map((r) => `${r}.txt`),
])

function isSharedNextMetadataFile(name) {
  // __next.__PAGE__.txt, __next._full.txt etc. — payload do root layout,
  // usado pela navegacao client-side de qualquer rota mantida.
  return name.startsWith('__next.')
}

async function main() {
  const entries = await readdir(OUT_DIR)
  let removed = 0
  for (const name of entries) {
    if (ALWAYS_KEEP.has(name) || isSharedNextMetadataFile(name)) continue
    await rm(path.join(OUT_DIR, name), { recursive: true, force: true })
    removed++
  }
  console.log(`[prune-tauri-export] removidas ${removed} entradas de marketing/demo de ${OUT_DIR}`)
}

main().catch((err) => {
  console.error('[prune-tauri-export] falhou:', err)
  process.exit(1)
})
