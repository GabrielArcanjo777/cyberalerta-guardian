# Causa raiz

## E2E

O `playwright.config.ts` abre o painel em `http://127.0.0.1:3000`. Na versão do Next usada (`^16.2.6`), o servidor de dev bloqueia por padrão pedidos a recursos `/_next/*` vindos de uma origem que não está em `allowedDevOrigins` — e `127.0.0.1` não estava (ver o aviso em `fontes/`).

Resultado: o HTML chega, mas o JavaScript do cliente não roda. Os testes que esperam redirecionamento ou conteúdo renderizado no cliente estouram o timeout.

Reprodução local: `CI=1 npx playwright test` → `18 failed, 7 passed`.

Correção: `allowedDevOrigins: ['127.0.0.1']` em `frontend/next.config.js`. Só vale para o servidor de dev; o build de produção não muda.

Depois da correção: `25 passed`.

## Android

`android-actions/setup-android@v3` instala por padrão os pacotes `tools platform-tools`. O pacote `tools` foi removido do repositório do SDK; o `sdkmanager` da versão 16 falha ao procurá-lo.

Correção: `packages: platform-tools` no passo. A plataforma 35 e o build-tools já eram instalados no passo seguinte.

## Por que ninguém viu antes

`continue-on-error: true`. O job falhava, mas o check do PR ficava verde. Lição registrada em `docs/decisoes.md` (ADR-008).
