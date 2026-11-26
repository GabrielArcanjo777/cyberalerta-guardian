<p align="center">
  <img src="frontend/public/cyberalerta-guardian-logo-banner.png" alt="CyberAlerta Guardian" width="560">
</p>

<h1 align="center">CyberAlerta Guardian</h1>

<p align="center"><b>Analisa mensagens de um WhatsApp autorizado, aponta sinais de golpe e avisa um contato de confiança.</b></p>

<p align="center">
  <a href="https://github.com/GabrielArcanjo777/cyberalerta-guardian/actions/workflows/ci.yml"><img src="https://github.com/GabrielArcanjo777/cyberalerta-guardian/actions/workflows/ci.yml/badge.svg?branch=main" alt="CI"></a>
</p>

---

## O que é

Um projeto pessoal de estudo. Conecta um número de WhatsApp autorizado por QR code, lê as mensagens recebidas em silêncio e, quando encontra sinais de golpe (Pix suspeito, link falso, falso banco, pedido de código, urgência), registra um caso e manda alerta **apenas para o contato de confiança cadastrado**.

O bot nunca responde ao remetente. Não é produto, não tem usuários, não está publicado em lugar nenhum.

## Como foi feito

Construído com apoio intensivo de IA (LLM) na implementação. O objetivo foi aprender arquitetura, testes, segurança e integração entre plataformas — não lançar software.

Por isso este README lista o que **não** funciona com o mesmo peso do que funciona. Onde eu não sei explicar uma decisão, ela aparece em limitações, não em destaque.

A divisão real do trabalho, o que está verificado e o que não está: [`docs/como-foi-feito.md`](docs/como-foi-feito.md).

## O que funciona hoje

- `POST /analyze` retorna score de risco e sinais nomeados, por motor de regras determinísticas.
- Painel web (Next.js) com casos, timeline e feedback.
- Login local com Argon2id, MFA/TOTP e RBAC.
- App Android (Kotlin/Compose) que recebe push pelo contato de confiança.
- Casca Windows em Tauri reaproveitando o painel.
- CI no GitHub Actions: `ruff` + `pytest` (359 testes) no backend, `tsc` + `eslint` no frontend, e2e com Playwright (25 testes) e testes unitários do Android.

## O que não funciona

- O pipeline com LLM existe e foi testado, mas **não decide nada**. Quem cria caso e notifica é o motor de regras.
- WhatsApp via Evolution API é integração não oficial. Risco real de bloqueio do número.
- Multi-tenant incompleto: `devices` e `notifications` isolam por organização; `Case`, `ProtectedPerson` e `Guardian` não.
- Persistência só em SQLite.
- Rate limit e idempotência ficam em memória — não sobrevivem a restart nem a múltiplos workers.
- Android e Windows com build de debug, sem assinatura.
- Sem observabilidade, sem logging estruturado, sem teste com usuários.
- O dataset de 305 mensagens é sintético e gerado por IA. Os números medidos nele não valem como métrica de mundo real.
- Nesse dataset, o alerta ao contato de confiança pega só 16 de 150 golpes (com zero alarme falso). É uma escolha — alerta falso faz a família parar de ouvir —, mas significa que a maior parte dos golpes vira caso para revisão, não alerta. Ver [`docs/metrics_v1.md`](docs/metrics_v1.md).

## Arquitetura

```text
WhatsApp autorizado ──► Evolution API ──► webhook FastAPI (/webhook/evolution)
                                              │
                               normaliza o texto, aplica as regras
                                              │
                                 score + sinais nomeados
                       ┌──────────────────────┼─────────────────────────┐
                  score < 40             score ≥ 40                risco HIGH (≥ 65)
                  não vira caso       vira caso no painel       alerta ao contato de confiança
                                         (Next.js)              (WhatsApp, atrás de DRY_RUN e allowlist)

Em paralelo (modo sombra, padrão): PII removida → LLM opcional → Policy Engine.
Só registra a decisão para comparação; não muda o alerta.
```

Detalhe por componente e status real em [`docs/ARCHITECTURE.md`](docs/ARCHITECTURE.md).

## Como rodar

Backend:

```powershell
cd cyberalerta-guardian\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Interface:

```powershell
cd cyberalerta-guardian\frontend
npm ci
npm run dev
```

- `http://localhost:3000/assisted-demo` — demo guiada, sem dados reais
- `http://localhost:8000/docs` — Swagger

Setup completo em [`docs/LOCAL_SETUP.md`](docs/LOCAL_SETUP.md).

## Testes

```bash
bash .agents/skills/verificar-projeto/scripts/verificar.sh   # ruff, pytest, tsc, eslint
cd frontend && CI=1 npx playwright test                      # e2e (sobe API e painel)
cd apps/android-companion && ./gradlew testDevDebugUnitTest  # Android (JDK 17)
```

## Estrutura

```text
backend/                 FastAPI — API, motor de risco, auth, devices
frontend/                Next.js — painel web e demo assistida
apps/android-companion/  Kotlin/Compose — app do contato de confiança
apps/windows-shell/      Tauri — casca desktop
docs/                    arquitetura, setup, métricas, decisões, histórico
demandas/                pedidos com especificação, evidência e entrega
.agents/skills/          procedimentos reutilizáveis (verificar, e2e, dataset)
AGENTS.md                regras para quem (pessoa ou agente) for mexer no código
```

## O que eu aprendi

- **Regra decide, LLM sugere.** Um modelo pode ser enganado pelo próprio texto que analisa (prompt injection). Por isso quem dispara alerta é um motor de regras auditável; a LLM só entra como insumo ([ADR-002](docs/decisoes.md)).
- **Precisão e recall puxam para lados opostos.** Subir o limiar do alerta zera o alarme falso, mas deixa golpe passar. Medir num dataset, mesmo sintético, tornou essa troca visível em vez de opinião.
- **Build real acha bug que leitura não acha.** O app Android só compilou de verdade depois de dois erros que nenhuma revisão tinha pegado (`18f4b26`).
- **CI verde não é CI passando.** Os jobs de e2e e Android falharam por dias com `continue-on-error` e ninguém viu. A causa do e2e era uma linha de configuração do Next ([demanda 002](demandas/002-e2e-e-android-no-ci/README.md)).
- **Lint barato paga.** O primeiro `ruff` achou um `import` faltando que fazia um teste de segurança nunca falhar.
- **Segurança é padrão, não opção.** Envio real desligado por padrão, allowlist de números e o bot nunca falando com o remetente evitam que um teste mal configurado vire mensagem para um desconhecido.

## Para quem for mexer no código

[`AGENTS.md`](AGENTS.md) diz o que pode e o que não pode, quando parar e chamar uma pessoa e o que é "pronto". O resto:

| Pergunta | Arquivo |
|---|---|
| O que já foi feito? | [`docs/historico.md`](docs/historico.md) |
| Por que foi feito assim? | [`docs/decisoes.md`](docs/decisoes.md) |
| Como foi produzido (e o papel da IA)? | [`docs/como-foi-feito.md`](docs/como-foi-feito.md) |
| Onde estão os limites? | [`docs/contexto.md`](docs/contexto.md) |
| De onde vêm as referências? | [`docs/referencias.md`](docs/referencias.md) |
| O que está pendente? | [`demandas/`](demandas/README.md) |

## Aviso

Não é ferramenta de vigilância. Roda apenas em conta própria ou com autorização explícita do titular. Não substitui banco, polícia, advogado ou canal oficial, e não promete detecção infalível — identifica sinais e avisa uma pessoa, que decide.

## Licença

[Elastic License 2.0](./LICENSE).
