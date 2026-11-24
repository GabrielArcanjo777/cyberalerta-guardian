# Histórico

O que já foi feito, em ordem, tirado do `git log`. Cada fase cita os commits principais para quem quiser ver o código daquela época (`git show <hash>`).

Para o **porquê** das escolhas, ver [`decisoes.md`](decisoes.md). Para **como** o trabalho foi feito, ver [`como-foi-feito.md`](como-foi-feito.md).

---

## Fase 1 — Protótipo (30–31/mai/2026)

Primeira versão: API FastAPI que analisa uma mensagem e devolve score de risco, mais um painel Next.js.

- `bcf1217` protótipo inicial
- `431b7e4` canal simples de entrada (chatbot)
- `07bdc91` console de casos para o responsável
- `d504b44` escalonamento para o círculo de confiança
- `385a93e` fluxo assistido de "prova de confiança" (checklist antes de pagar)
- `e2c1fb3` demo guiada sem dados reais

## Fase 2 — Canais e autenticação (18–21/jun/2026)

- `bfb9975` contrato de adapter de canal (o resto do sistema não sabe de onde veio a mensagem)
- `5fa747b` fluxo "dual bot" (um lado conversa com a pessoa protegida, outro avisa o responsável)
- `ce3bcfc` controles de consentimento no console
- `a3be6f0` beta com n8n atrás de allowlist de números
- `bdabeac`, `0fe2b86` login com Argon2id, MFA/TOTP, códigos de recuperação, Google OIDC e RBAC

## Fase 3 — WhatsApp real, limpeza e motor híbrido (08–12/jul/2026)

- `e9ce452` canal WhatsApp via Evolution API, persistência SQLite
- `56a33a4`, `4ab40e5`, `6a23e03` remoção do canal Twilio e de código morto
- `4eece41` primeiro CI: `pytest` + `tsc` + `eslint`
- `8d57151` **regra cardinal**: o bot só fala com o contato de confiança, nunca com o remetente
- `224e6c2` alerta por WhatsApp só para risco alto
- `00ff7e6` bug: caminho relativo do SQLite criava dois bancos diferentes
- `87e5b28` bug: sessão expirava em 15 min
- `1f4f809` abstração de provedor de LLM
- `254083e`, `7d9f604`, `9e35fd0` pipeline híbrido: avaliação determinística, Policy Engine, sanitização de PII, defesa contra prompt injection e eventos de auditoria
- `da43c9b` dataset rotulado v1 (305 mensagens sintéticas) e métricas medidas
- `2032ef2` testes e2e com Playwright
- `3aef846` fail-fast em produção e idempotência com TTL
- `de91916` preparação de deploy em servidor

## Fase 4 — Dispositivos, Android e Windows (18–19/jul/2026)

- `a577974` `Organization` como fronteira de isolamento
- `38715d5` pareamento de dispositivo com teste de IDOR entre organizações
- `2b6e49a` push real via FCM com ACK
- `7926ea2` revogação de dispositivo
- `586712a` app Android (Kotlin/Compose): pareamento, push, ACK
- `18f4b26` build real do Android revelou 2 bugs que a leitura do código não mostrava
- `e3553c6` casca Windows em Tauri
- `fe51787` regras para golpes de INSS/benefício e falsa ameaça judicial
- `87e7d64` licença Elastic 2.0

## Fase 5 — Honestidade e qualidade (set–nov/2026)

- `b5e97ee` README reescrito sem marketing, com o que **não** funciona
- `d73eac9` estrutura para agentes: `AGENTS.md`, `contexto.md`, `decisoes.md`, `demandas/`
- `1de78a5` CI ganha `ruff`, cobertura, e2e e Android; o `ruff` achou um `import pytest` faltando que escondia uma falha de teste

## Fase 6 — CI inteiro verde (23/nov/2026)

Demanda [`002-e2e-e-android-no-ci`](../demandas/002-e2e-e-android-no-ci/README.md).

- E2E: 18 de 25 testes falhavam porque o Next 16 bloqueia `/_next/*` vindo de `127.0.0.1`. Corrigido com `allowedDevOrigins`; o job deixou de ser opcional.
- Android: o job morria no `setup-android` tentando instalar o pacote `tools`, que não existe mais.
- `docs/metrics_v1.md` estava desatualizado desde julho. Regenerado: o alerta pega 16 de 150 golpes (antes registrava 15).
- Skills reutilizáveis em `.agents/skills/`, este histórico e `referencias.md`.
