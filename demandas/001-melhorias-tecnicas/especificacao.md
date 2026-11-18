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
2. Job de e2e no CI — **feito**, ainda com `continue-on-error` até estabilizar.
3. Job Android rodando `./gradlew testDevDebugUnitTest` — **feito**, idem.
4. `ruff check` no CI com regras fatais — **feito**, e já achou 2 bugs reais.
5. Cobertura publicada como artefato do CI — **feito** (92% no backend).
6. `Dependabot` ativo — **feito**.
7. Nenhum teste novo nomeado por sprint — pendente.

## Prioridade

| # | Item | Impacto | Esforço | Estado |
|---|---|---|---|---|
| P0 | Corrigir Playwright | alto | — | feito |
| P0 | Job de e2e no CI | alto | baixo | feito (gradual) |
| P0 | Job Android no CI | alto | baixo | feito (gradual) |
| P1 | `ruff` no CI | alto | baixo | feito |
| P1 | Cobertura no CI | médio | baixo | feito |
| P1 | `mypy` no CI | alto | médio | pendente |
| P2 | Mover `main.py` para `app/main.py` | médio | alto | pendente |
| P2 | Renomear testes por comportamento | médio | alto | pendente |
| P2 | Alembic para SQLite | médio | médio | pendente |
| P2 | `uv` + `pyproject.toml` | baixo | médio | pendente |

## Descartado

**Consolidar `requests` → `httpx`.** Parecia duplicação, mas `google.auth.transport.requests` exige `requests`. As duas bibliotecas têm donos diferentes no projeto: `httpx` para as chamadas da aplicação, `requests` como transporte do google-auth. Remover quebraria o FCM e o OIDC.

## Achado do lint

O primeiro `ruff check` apontou `F821 undefined name 'pytest'` em `app/tests/test_security_hardening.py`. O teste passava porque o caminho que usa `pytest.fail` nunca era executado — a falha real nunca aparecia. Corrigido com o import.

## Achado da cobertura

Cobertura total: **92%**. Os módulos com 0% são de ramo não executável ou de integração externa (`trusted_circle/escalation_log.py`).

## Lição

Ligar `ruff` com o conjunto fatal (`E9`, `F63`, `F7`, `F82`) foi o único item que deu retorno imediato: dois bugs reais em um comando, sem quebrar o build.

