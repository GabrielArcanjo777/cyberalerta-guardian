# Referências

Documentação externa que sustenta decisões do projeto. Só entra aqui o que o código de fato usa.

## Lei e privacidade

- [LGPD — Lei 13.709/2018](https://www.planalto.gov.br/ccivil_03/_ato2015-2018/2018/lei/l13709.htm) — base do opt-in e da trilha de auditoria (ADR-006).

## Segurança

- [OWASP Password Storage Cheat Sheet](https://cheatsheetseries.owasp.org/cheatsheets/Password_Storage_Cheat_Sheet.html) — por que Argon2id para senha.
- [RFC 6238 — TOTP](https://www.rfc-editor.org/rfc/rfc6238) — MFA por código de 6 dígitos.
- [OpenID Connect Core](https://openid.net/specs/openid-connect-core-1_0.html) e [Google Identity — OIDC](https://developers.google.com/identity/openid-connect/openid-connect) — login com Google (`backend/app/auth/google_oidc.py`).
- [OWASP — Unvalidated Redirects](https://cheatsheetseries.owasp.org/cheatsheets/Unvalidated_Redirects_and_Forwards_Cheat_Sheet.html) — o que `frontend/e2e/redirect.spec.ts` testa.
- [OWASP LLM Top 10 — Prompt Injection](https://genai.owasp.org/llmrisk/llm01-prompt-injection/) — por que a LLM não decide nada (ADR-002).

## Stack

- [FastAPI](https://fastapi.tiangolo.com/) — API.
- [Next.js — `allowedDevOrigins`](https://nextjs.org/docs/app/api-reference/config/next-config-js/allowedDevOrigins) — causa das falhas do e2e (demanda 002).
- [Playwright — `webServer`](https://playwright.dev/docs/test-webserver) — sobe API e painel antes do e2e.
- [Firebase Cloud Messaging HTTP v1](https://firebase.google.com/docs/cloud-messaging/send/v1-api) — push para o Android.
- [Tauri](https://tauri.app/) — casca Windows.
- [android-actions/setup-android](https://github.com/android-actions/setup-android) — entrada `packages` usada no CI.

## WhatsApp

- [Evolution API](https://doc.evolution-api.com/) — integração **não oficial** usada hoje.
- [WhatsApp Cloud API (Meta)](https://developers.facebook.com/docs/whatsapp/cloud-api) — caminho oficial, ainda em aberto em `decisoes.md`.

## Licença

- [Elastic License 2.0](https://www.elastic.co/licensing/elastic-license) — ver `LICENSE`.
