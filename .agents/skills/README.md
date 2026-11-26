# Skills do agente

O que um agente consegue executar neste repositório, e com qual comando. Se não está aqui, o agente não deve improvisar.

## Procedimentos com passo a passo

| Skill | Para quê |
|---|---|
| [`verificar-projeto`](verificar-projeto/SKILL.md) | mesma checagem do CI antes de abrir PR |
| [`rodar-e2e`](rodar-e2e/SKILL.md) | testes Playwright com API e painel no ar |
| [`avaliar-dataset`](avaliar-dataset/SKILL.md) | medir o detector depois de mexer em regras |

## Rodar e verificar

| Skill | Comando | Onde |
|---|---|---|
| Subir API | `python -m uvicorn main:app --reload --port 8000` | `backend/` |
| Rodar testes backend | `python -m pytest app/tests -q` | `backend/` |
| Rodar um teste | `python -m pytest app/tests/test_hybrid_policy.py -q` | `backend/` |
| Typecheck frontend | `npx tsc --noEmit` | `frontend/` |
| Lint frontend | `npm run lint` | `frontend/` |
| Subir painel | `npm run dev` | `frontend/` |
| Testes Android | `./gradlew testDevDebugUnitTest` | `apps/android-companion/` |
| Avaliar dataset | `python scripts/evaluate_dataset.py` | `backend/` |
| Criar admin | `python scripts/create_admin.py` | `backend/` |

## Nunca executar sem humano

- qualquer coisa com `BETA_REAL_SEND_ENABLED=true`
- envio via Evolution API com `DRY_RUN=false`
- `git push --force` na `main`
- alteração de `.env` real

## Convenções

- Idioma do código e comentários: português no domínio, inglês em infraestrutura.
- Nome de teste: descreve comportamento, não número de sprint.
- Mensagem de commit: `tipo: o que mudou`, em minúsculas.
- Toda decisão estrutural ganha entrada em `docs/decisoes.md`.

## Antes de abrir PR

```bash
bash .agents/skills/verificar-projeto/scripts/verificar.sh
```

Se o script termina em `OK: tudo verde` e existe teste para o comportamento novo, o PR está pronto.
