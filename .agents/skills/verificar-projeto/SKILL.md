---
name: verificar-projeto
description: Roda a mesma verificação do CI (lint, testes, typecheck) antes de dizer que uma mudança está pronta.
---

# Verificar o projeto

Use antes de abrir PR ou de declarar uma tarefa pronta.

## Passos

```bash
bash .agents/skills/verificar-projeto/scripts/verificar.sh
```

O script roda, na ordem, e para no primeiro erro:

1. `ruff check .` (backend)
2. `python -m pytest app/tests -q` (backend)
3. `npx tsc --noEmit` (frontend)
4. `npm run lint` (frontend)

Precisa de `backend/requirements-dev.txt` instalado no Python ativo e de `npm ci` já rodado em `frontend/`.

## O que não cobre

- e2e: ver a skill `rodar-e2e`.
- Android: `./gradlew testDevDebugUnitTest` em `apps/android-companion/` (precisa de JDK 17 e do `google-services.json` placeholder descrito em `BUILD_NOTES.md`).

## Pronto quando

O script termina com `OK: tudo verde`.
