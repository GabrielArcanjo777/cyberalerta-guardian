# 001 — Melhorias técnicas

**Estado:** aberta · **Aberta em:** 2026-11-17

## Problema

O projeto tem boa cobertura de testes de domínio, mas a infraestrutura de qualidade não acompanha: o e2e nunca rodou com sucesso, o app Android não tem CI, e não há lint nem tipagem no Python. Isso significa que metade do repositório está sem verificação automática.

Evidências levantadas em 2026-11-17:

1. `frontend/playwright.config.ts` usava `cd ../backend && ./venv/Scripts/python` — caminho só de Windows, quebra em Linux. Somado a `retries: 0`, `trace: 'on-first-retry'` nunca gerava trace.
2. `.github/workflows/ci.yml` tem 2 jobs: `pytest` e `tsc`+`eslint`. Não roda e2e, não roda Android, não roda lint de Python, não mede cobertura.
3. `apps/android-companion` tem 5 arquivos de teste e nenhum job de CI.
4. `backend/main.py` tem mais de 800 linhas e manipula `sys.path` para importar `app.*`. O entrypoint deveria ser um módulo do pacote.
5. `requirements.txt` usa `httpx` **e** `requests` — dois clientes HTTP para o mesmo tipo de chamada.
6. Arquivos de teste nomeados por sprint (`test_sprint_25v4_...`, `test_sprint_26v5_...`) — o nome não diz o comportamento verificado, e o teste fica órfão quando o sprint deixa de existir.
7. Persistência SQLite criada em runtime, sem migração versionada.
8. Rate limit e idempotência em memória por processo.

## Objetivo

Todo código do repositório — backend, frontend e Android — é verificado automaticamente a cada push, e qualquer regressão aparece no PR antes do merge.

## Fora de escopo

- migrar para WhatsApp Cloud API
- Postgres/Redis
- assinatura de APK e instalador

## Critério de aceite

1. `playwright.config.ts` roda em Linux e Windows sem caminho absoluto de sistema — **feito**.
2. Job de e2e no CI, verde em `main`.
3. Job Android rodando `./gradlew testDevDebugUnitTest` no CI.
4. `ruff check` e `mypy` no CI (começar com regras fatais, subir depois).
5. Cobertura publicada como artefato do CI.
6. `Dependabot` ativo — **feito**.
7. Nenhum teste novo nomeado por sprint.

## Prioridade

| # | Item | Impacto | Esforço |
|---|---|---|---|
| P0 | Corrigir Playwright | alto | feito |
| P0 | Job de e2e no CI | alto | baixo |
| P0 | Job Android no CI | alto | baixo |
| P1 | `ruff` + `mypy` no CI | alto | médio |
| P1 | Cobertura no CI | médio | baixo |
| P1 | Consolidar `requests` → `httpx` | médio | médio |
| P2 | Mover `main.py` para `app/main.py` | médio | alto |
| P2 | Renomear testes por comportamento | médio | alto |
| P2 | Alembic para SQLite | médio | médio |
| P2 | `uv` + `pyproject.toml` | baixo | médio |

## Risco

Ligar `ruff`/`mypy` de uma vez quebra o build por dívida acumulada. Entrar com o conjunto fatal (`E9`, `F63`, `F7`, `F82`) e ampliar por PR.
