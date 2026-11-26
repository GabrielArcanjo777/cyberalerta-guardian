# Especificação

## Problema

Na execução 44210930332 do CI (`main`, 18/nov/2026):

- **E2E:** 18 de 25 testes falhavam. Todos que dependem de JavaScript no cliente (redirecionamento pós-login, rota de admin, animação).
- **Android:** o job parava no passo `setup-android`, antes de compilar.

Os dois jobs tinham `continue-on-error: true`, então o PR mostrava verde.

## Objetivo

Os dois jobs passam de verdade, e o e2e passa a bloquear merge.

## Fora de escopo

- Novos testes e2e.
- Assinatura do APK.

## Critério de aceite

1. `CI=1 npx playwright test` em `frontend/` termina com 25 passed — localmente.
2. Job E2E verde no PR, sem `continue-on-error`.
3. Job Android passa do `setup-android` e roda `testDevDebugUnitTest`.

## Risco

Tornar o e2e bloqueante pode travar PRs por teste instável. Mitigação: `retries: 2` já existe no CI (`playwright.config.ts`).
