---
name: rodar-e2e
description: Sobe API e painel e roda os testes Playwright do frontend, do jeito que o CI roda.
---

# Rodar o e2e

## Pré-requisitos

- Python com `backend/requirements-dev.txt` instalado **e no PATH como `python`** (o Playwright chama `python -m uvicorn`).
- `npm ci` em `frontend/` e `npx playwright install chromium`.

## Passos

```bash
cd frontend
CI=1 npx playwright test
```

Com `CI=1` o Playwright sobe API (`:8000`) e painel (`:3000`) do zero em vez de reaproveitar servidores abertos.

## Se quase tudo falhar de uma vez

Primeiro suspeito: a página não hidratou. Procure no log `[WebServer] Blocked cross-origin request to Next.js dev resource`. A origem usada pelo teste precisa estar em `allowedDevOrigins` (`frontend/next.config.js`). Foi isso na demanda 002.

## Pronto quando

`25 passed` (ou o total atual), sem `flaky`.
