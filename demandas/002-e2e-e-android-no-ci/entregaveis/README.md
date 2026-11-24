# Entregáveis

| Arquivo | Mudança |
|---|---|
| `frontend/next.config.js` | `allowedDevOrigins: ['127.0.0.1']` |
| `.github/workflows/ci.yml` | e2e sem `continue-on-error`; `setup-android` com `packages: platform-tools` |

Commit: `fix: e2e volta a passar e android ci instala o sdk` (PR "Organiza o projeto para portfólio e deixa o CI inteiro verde").

## Verificação

- Local: `CI=1 npx playwright test` → 25 passed.
- Local: `ruff check .` + `pytest` → 359 passed; `tsc` e `eslint` limpos.
- CI do PR: ver checks do PR.
