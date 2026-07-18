// Unica fonte de verdade pra "estamos rodando dentro do shell Windows
// (Tauri) ou no navegador (Web)?" — platformFetch, o bridge de deep link e
// o Header (pra esconder a navegacao de marketing dentro do app) usam isso.
export function isTauriRuntime(): boolean {
  return typeof window !== 'undefined' && '__TAURI_INTERNALS__' in window
}
