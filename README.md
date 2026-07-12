# CyberAlerta Guardian

**Proteção contra golpes no WhatsApp — um alerta antes do prejuízo.**

CyberAlerta Guardian analisa as mensagens recebidas em um número de WhatsApp **autorizado**, descarta as conversas normais e mostra no painel apenas os **alertas de risco**: Pix suspeito, link falso, falso banco, parente pedindo dinheiro, código de verificação e mensagens de urgência/manipulação. O responsável (familiar, cuidador ou instituição) revisa cada alerta com risco, motivo e ação recomendada.

O projeto está em estágio **MVP / demonstração técnica**. Não é produção, **não é ferramenta de espionagem** e só deve ser usado em contas próprias ou com **autorização expressa do titular**. Não substitui banco, polícia, advogado ou canais oficiais, e não promete detecção infalível.

## Status atual

**Beta Técnico Local.** Backend FastAPI + frontend Next.js, autenticação com Google OIDC, MFA/TOTP, recovery codes (Argon2id), RBAC, auditoria, rate limit, persistência SQLite e painel operacional. **301 testes automatizados** no backend, além de testes e2e do frontend com Playwright (acesso, redirecionamento e animação); dataset rotulado de 305 mensagens com métricas medidas (`docs/metrics_v1.md`).

Detecção em camadas: regras determinísticas explicáveis + **pipeline híbrido com LLM e Policy Engine** (desligado e em shadow por padrão — a LLM nunca decide envio). **Regra cardinal: o bot nunca responde ao remetente.** O único destino possível de mensagem de saída é o contato de confiança cadastrado, e apenas em golpe explícito, sempre atrás do safety gate (simulação/envio real/allowlist).

O canal de WhatsApp usa a **Evolution API** (WhatsApp Web / Baileys) — não-oficial, gratuita, pareada por QR code em `/whatsapp-setup`. Adequada para portfólio/demo: o número pode ser bloqueado pela Meta e a sessão pode cair exigindo novo pareamento. As antigas integrações Meta Cloud API e Twilio Sandbox foram removidas.

## Problema

Golpes digitais por engenharia social exploram pressa, confiança familiar, medo e falsa autoridade. Muitas vítimas só percebem o risco depois de transferir dinheiro, clicar em um link ou enviar um código.

O CyberAlerta Guardian foca no momento anterior ao dano:

- antes do Pix;
- antes do clique;
- antes de enviar senha, código ou documento;
- antes de instalar aplicativo remoto;
- antes de responder a um contato suspeito.

## Solução

O Guardian organiza uma proteção assistida e contínua:

1. conecta-se um número de WhatsApp autorizado por QR code (`/whatsapp-setup`);
2. cadastra-se o número da pessoa protegida e o do contato de confiança (na mesma tela);
3. as mensagens recebidas são analisadas em tempo real, **em silêncio** — o bot nunca responde no chat;
4. conversas normais são descartadas — não ficam no painel;
5. mensagens suspeitas viram um caso com risco, motivo e ação recomendada;
6. golpe explícito (risco alto) dispara alerta **somente ao contato de confiança** (simulado por padrão; envio real exige dupla autorização na UI);
7. o responsável revisa e decide (confirmar golpe, falso positivo, resolver);
8. tudo com consentimento/opt-in, retenção limitada e trilha auditável.

## Status Real

| Área | Status | Observação |
| --- | --- | --- |
| Backend FastAPI | Implementado | API local com análise, console, canais mock/demo e consentimento. |
| Frontend Next.js | Implementado | Interface demo com Home, `/assisted-demo`, console, intake e telas auxiliares. |
| `/health` | Implementado | Health check do backend. |
| `/analyze` | Implementado | Fluxo principal de análise rule-based/agentic local. |
| `/assisted-demo` | Implementado | Rota recomendada para apresentar o produto. |
| Guardian Console | Implementado para demo/local | Inclui caso, risco, timeline, feedback e consentimento. |
| Event Model | Implementado em `memory` ou SQLite | Eventos, casos, avaliações e audit log persistem quando `STORAGE_BACKEND=sqlite`. |
| Pattern Intelligence | Implementado com regras | Sem ML pesado e sem IA externa. |
| Pipeline híbrido (regras + LLM + Policy Engine) | Implementado | Desligado e em shadow por padrão; só a Policy Engine + safety gate decidem envio. |
| Cadastro pessoa protegida + contato de confiança | Implementado | UI em `/whatsapp-setup`, persistido em SQLite, sobrevive restart. |
| Toggles de envio na UI (simulação/envio real) | Implementado | Sem editar `.env`; allowlist re-pinada automaticamente ao contato de confiança. |
| Dataset rotulado + métricas | Implementado | 305 mensagens, harness com código de produção, regressão em testes (`docs/metrics_v1.md`). |
| Testes e2e frontend (Playwright) | Implementado | Smoke tests de acesso, redirecionamento de login e respeito a reduced motion (`frontend/e2e/`). |
| Agentes controlados | Implementados | Sem agente autônomo livre; LLM externa é opcional e nunca decide envio. |
| Consentimento/opt-in | Implementado como base local | Não é consultoria jurídica nem compliance completo. |
| Autenticação local | Implementado | Login email/senha, cookies HttpOnly, MFA/TOTP, RBAC e auditoria. |
| Google OAuth/OIDC | Implementado como opcional | Desativado por padrão; exige configuração local segura. |
| Persistência | `memory` ou SQLite local | SQLite é opcional via env; não há banco de produção. |
| WhatsApp (Evolution) | Implementado (não-oficial) | Canal via Evolution API/WhatsApp Web (Baileys). Pareamento por QR em `/whatsapp-setup`. Portfólio/demo, não produção; risco de ban do número. |
| n8n/WhatsApp | Parcial/MVP | Endpoint inbound n8n-first para WhatsApp local/controlado; CyberAlerta decide risco e ação. |
| Produção | Não pronta | Ainda falta multi-tenant, observabilidade gerenciada, migrações formais e hardening final. |

## Fluxo Principal da Demo

Rota recomendada:

```text
http://localhost:3000/assisted-demo
```

Roteiro conceitual:

```text
Mensagem suspeita
  -> normalização e análise silenciosa
  -> decisão determinística / Policy Engine
  -> Guardian Console (caso revisável)
  -> alerta somente ao contato de confiança, se HIGH e todos os gates permitirem
  -> Proof of Trust
  -> Agent Decision Trace
  -> relatório
```

Exemplo de narrativa:

> Dona Lucia recebe uma mensagem dizendo "mãe, troquei de número, preciso de Pix urgente, não liga agora". O Guardian identifica sinais de risco, orienta pausa, cria um caso para Gabriel revisar e recomenda confirmação por canal independente.

## Funcionalidades Implementadas

- Análise de mensagem suspeita via `POST /analyze`.
- Score de risco e sinais explicáveis.
- Trust Lock como recomendação de pausa protetiva.
- Agent Decision Trace para explicar decisões.
- Recovery checklist para orientação pós-incidente.
- Preparação para n8n/WhatsApp como camada de orquestração de canais.
- Report estruturado.
- Simple Channel mock para entrada voluntária.
- Mock WhatsApp Adapter.
- Channel Adapter Contract adapter-first.
- Evolution Demo Adapter para desenvolvimento controlado.
- Dual Bot Flow:
  - Bot Protegido (recebe e analisa — nunca responde ao remetente);
  - Bot Responsável (alerta somente o contato de confiança);
  - feedback auditável.
- Pipeline híbrido de detecção (regras + LLM + Policy Engine):
  - abstração de provedor LLM (OpenAI-compatible/OpenRouter) com Mock para testes;
  - Policy Engine determinística e versionada (DISCARD / REVIEW / AUTO_ALERT);
  - sanitização de PII e proteção contra prompt injection antes da chamada externa;
  - shadow mode por padrão; a LLM nunca chama o adapter nem decide envio;
  - trilha de auditoria com hash de conteúdo, versões e latência (sem secrets).
- Cadastro do número da pessoa protegida + contato de confiança na UI, com persistência.
- Toggles de simulação (DRY_RUN) e envio real (beta) direto na UI, com allowlist automática.
- Dataset rotulado (305 mensagens) + harness de métricas rodando o código de produção.
- Testes e2e do frontend com Playwright (acesso, redirecionamento e reduced motion).
- Sanitização de conteúdo exibido no frontend (`frontend/lib/sanitize.ts`).
- Acessibilidade de animações: `prefers-reduced-motion` respeitado via `usePrefersReducedMotion` e `frontend/lib/motion.ts`.
- Idempotência inbound com TTL e limite de tamanho no registro em memória (aceita reenvio legítimo após expirar, rejeita replay dentro da janela).
- Fail-fast de produção: a aplicação não sobe com `APP_ENV=production` sem `RATE_LIMIT_ENABLED=true` e `EVOLUTION_WEBHOOK_SECRET` definidos.
- Event Model com eventos, casos, mensagens e risk assessments.
- Pattern Intelligence rule-based.
- Agentes controlados:
  - `TriageAgent`;
  - `ResponsibleAlertAgent`;
  - `CaseSummaryAgent`;
  - `PatternReviewAgent`.
- Guardian Console real/local com:
  - lista de casos;
  - caso ativo;
  - pessoa protegida;
  - responsável vinculado;
  - risco e sinais;
  - timeline de eventos;
  - feedback;
  - ações do responsável;
  - status de consentimento.
- Consentimento/opt-in local com ativar, desativar, revogar e escopos.
- Autenticação local por email/senha com hash Argon2id.
- Sessão assinada em cookie HttpOnly com SameSite=Lax.
- MFA/TOTP com setup, enable, verify e bloqueio de admin sem MFA.
- Google OAuth/OIDC opcional, com state anti-CSRF, validação de issuer/audience/email verificado e auto-create seguro.
- RBAC com roles `admin`, `analyst` e `viewer`.
- Admin API com `/admin/users` e `/admin/audit-logs`.
- Script `scripts/create_admin.py` para criação segura do admin inicial.
- Auditoria de login, logout, MFA, Google e falhas de autenticação.
- Rate limit básico em memória para login/MFA.
- Storage em memória ou SQLite local para partes da demo.
- Headers básicos de segurança e API key opcional para endpoints sensíveis.

## Funcionalidades Simuladas ou Demo

- Trusted Circle não envia SMS, WhatsApp ou e-mail real.
- Mock WhatsApp não se conecta ao WhatsApp real.
- Evolution API é canal não-oficial (WhatsApp Web/Baileys) para portfólio/demo.
- Guardian Console usa dados locais/in-memory ou SQLite local.
- Proof of Trust é checklist assistido, não valida identidade automaticamente.
- Pattern Intelligence usa regras explicáveis, não modelo treinado.
- Agentes são orquestradores controlados, não agentes autônomos.
- Consentimento é base técnica de opt-in, não implementação jurídica completa.

## Planejado

- Integração oficial futura com Meta Cloud API ou outro provider aprovado.
- Persistência de produção com migrações, criptografia e retenção formal.
- Multi-tenant, políticas refinadas por organização e gerenciamento completo de usuários.
- Observabilidade, auditoria robusta e logging estruturado.
- Políticas completas de LGPD, retenção e exclusão.
- Ampliação da cobertura e2e do frontend (hoje há smoke tests com Playwright).
- Deploy controlado para piloto.
- Dataset/ground truth para ML futuro, sem treinar modelo agora.

## Pipeline Híbrido de Detecção (regras + LLM + Policy Engine)

Combina três camadas para decidir se um alerta ao contato de confiança deve ser
enviado. **A LLM é apenas um insumo estruturado** — só a Policy Engine (determinística
e versionada) e o safety gate decidem envios. A LLM nunca chama o adapter de WhatsApp
nem decide sozinha.

```
Mensagem → Regras determinísticas ─┐
                                    ├→ Policy Engine → DISCARD | REVIEW | AUTO_ALERT
           Análise LLM ────────────┘                                       │
                                                              Contato de confiança
                                                            (via safety gate existente)
```

- **DISCARD**: score baixo, sem sinais fortes, LLM benigna concordante.
- **REVIEW**: LLM indisponível, conflito regras×LLM, faixa intermediária, injeção
  suspeita, saída inválida ou evidência insuficiente. **Default seguro.**
- **AUTO_ALERT**: só com `classification=SCAM`, `confidence>=0.85`, score determinístico
  `>=65`, ≥2 sinais objetivos, concordância e uma combinação de risco (A/B/C/D).
  A LLM sozinha **nunca** autoriza; regras sozinhas **nunca** autorizam.

### Config padrão segura

| Variável | Padrão | Efeito |
| --- | --- | --- |
| `HYBRID_LLM_ENABLED` | `false` | LLM não é chamada; roda só determinístico. |
| `HYBRID_LLM_SHADOW_MODE` | `true` | Grava a decisão que seria tomada; **nunca envia** por causa do híbrido. |
| `HYBRID_REQUIRE_LLM_FOR_AUTO_ALERT` | `true` | LLM indisponível ⇒ máximo `REVIEW`. |
| `HYBRID_REDACT_PII` | `true` | Redige cartão/CPF/telefone/código antes da LLM. |

### Ativar shadow mode (observar sem risco)

```
HYBRID_LLM_ENABLED=true
HYBRID_LLM_SHADOW_MODE=true      # roda a LLM e grava a decisão, sem enviar
HYBRID_LLM_BASE_URL=https://openrouter.ai/api/v1   # ou OpenAI/endpoint compatível
HYBRID_LLM_API_KEY=...
HYBRID_LLM_MODEL=...
```

Para produção real: `HYBRID_LLM_SHADOW_MODE=false` (o safety gate `DRY_RUN`/
`BETA_REAL_SEND_ENABLED`/`BETA_REQUIRE_ALLOWED_RECIPIENT`/`BETA_ALLOWED_RECIPIENTS`
continua valendo em cima da decisão).

**Rollback:** basta `HYBRID_LLM_ENABLED=false` (ou `SHADOW_MODE=true`) — o fluxo
volta ao comportamento determinístico atual sem qualquer alteração de código.

### Auditoria

Cada análise grava eventos (`DeterministicAssessmentCreated`, `LLMAnalysis*`,
`HybridDecisionCreated`/`Shadow`, `ReviewQueued`, `AutoAlertAuthorized`/`Blocked`,
`PromptInjectionDetected`, `PolicyFallbackUsed`) com metadados auditáveis: hash do
conteúdo, scores, versões de prompt/policy, provider/modelo, motivos curtos e latência.
**Nunca** grava API key, prompt, chain-of-thought ou o conteúdo integral.

## Arquitetura Resumida

```text
WhatsApp / Web / Mock
    |
    v
n8n ou frontend
    |
    v
backend/ FastAPI + Pydantic
    |
    +-- agents/                  análise e decisão do fluxo /analyze
    +-- controlled_agents/       agentes controlados do Dual Bot
    +-- channel_adapters/        contrato adapter-first de canais
    +-- dual_bot/                Bot Protegido e Bot Responsável
    +-- event_model/             eventos, mensagens, casos e risco
    +-- guardian_console/        console operacional local/demo
    +-- pattern_intelligence/    regras explicáveis e recorrência
    +-- consent/                 opt-in, escopos e status do bot
    +-- storage/                 memory ou SQLite local
    +-- trusted_circle/          escalonamento simulado
    +-- proof_trust/             verificação assistida
    +-- evolution_demo/          provider demo local/controlado
    +-- llm/                     abstração de provedor LLM (OpenAI-compatible + mock)
    +-- hybrid/                  Policy Engine, PII, eventos e decisão híbrida
```

No desenho-alvo, o n8n é o orquestrador opcional de canais: recebe eventos do WhatsApp ou de webhooks, chama o backend do CyberAlerta e executa apenas a ação autorizada. O backend continua sendo o cérebro de decisão: risco, Trust Lock, Proof of Trust, Recovery, auditoria e regras explicáveis ficam no CyberAlerta. Não existe ramo de resposta ao remetente.

```text
Evolution API (não-oficial) / Mock / Webhook de teste
        |
        v
n8n (opcional)
        |
        v
CyberAlerta Guardian Backend
        |
        v
alerta ao contato de confiança (único destino) / Guardian Console / log auditável
```

O remetente **nunca** recebe resposta em nenhum desenho.

## Stack Técnica

### Backend

- Python 3.13 (versão do CI)
- FastAPI 0.136.3
- Pydantic 2.13.4
- Uvicorn
- Pytest
- SQLite opcional via biblioteca padrão

### Frontend

- Next.js 16.2.6
- React 18.2
- TypeScript
- Tailwind CSS
- Framer Motion
- Three.js
- ESLint
- Playwright (testes e2e)

## Pré-Requisitos

- Python 3.13 (mesma versão do CI).
- Node.js 22 (mesma versão do CI; versões mais novas podem funcionar, mas não são a baseline).
- npm.
- Git.
- Docker opcional, necessário para Evolution API + PostgreSQL + Redis locais.

No Windows, se `python` não estiver no PATH, use `py` ou crie/ative uma venv explicitamente.

## Setup Rápido Local

Use dois terminais, um para o backend e outro para o frontend.

Terminal 1, API:

```powershell
cd cyberalerta-guardian\backend
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Terminal 2, interface:

```powershell
cd cyberalerta-guardian\frontend
npm ci
npm run dev
```

Acesse:

```text
Home: http://localhost:3000
Demo assistida: http://localhost:3000/assisted-demo
Health backend: http://localhost:8000/health
Swagger/OpenAPI: http://localhost:8000/docs
```

Para testar o n8n sem WhatsApp real, deixe o backend rodando e use o exemplo da seção [Integração n8n/WhatsApp](#integração-n8nwhatsapp).

## Como Rodar o Backend

```bash
cd backend
python -m venv .venv
```

Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

Linux/macOS:

```bash
source .venv/bin/activate
```

Instale dependências:

```bash
python -m pip install -r requirements.txt
```

Suba a API:

```bash
python -m uvicorn main:app --reload --port 8000
```

Verifique:

```bash
curl http://localhost:8000/health
```

Swagger/OpenAPI:

```text
http://localhost:8000/docs
```

## Autenticação, Admin e MFA

O backend agora possui autenticação local, Google OAuth opcional, MFA/TOTP, RBAC e auditoria. O estado padrão continua seguro para demo local: Google fica desativado e nenhum segredo real deve ser commitado.

Para criar o primeiro administrador local, rode com a venv ativa:

```powershell
cd cyberalerta-guardian
.\backend\.venv\Scripts\python.exe scripts\create_admin.py
```

Ou, se estiver dentro da pasta `backend` com a venv ativada:

```powershell
cd ..
python scripts\create_admin.py
```

O script pede email, nome e senha, valida força mínima e não imprime a senha. A senha precisa ter 12 caracteres, maiúscula, minúscula, número e símbolo. Em desenvolvimento local, também é possível usar `INITIAL_ADMIN_EMAIL`, `INITIAL_ADMIN_NAME` e `INITIAL_ADMIN_PASSWORD`, mas nunca coloque esses valores no Git.

**Persistência do admin:** o padrão `STORAGE_BACKEND=memory` é volátil — o admin criado some ao reiniciar. Para uso real local, configure antes de criar o admin:

```env
STORAGE_BACKEND=sqlite
SQLITE_DATABASE_URL=sqlite:///./cyberalerta_guardian.db
```

Com SQLite, o admin e todos os usuários persistem entre reinicializações.

Fluxo recomendado:

1. Suba o backend.
2. Crie o admin com `scripts/create_admin.py`.
3. Acesse `http://localhost:3000/login`.
4. Entre com email/senha.
5. Abra `http://localhost:3000/mfa` e habilite TOTP.
6. Acesse `http://localhost:3000/admin`.

Administradores sem MFA conseguem entrar apenas para configurar MFA, mas não acessam `/admin/users` nem `/admin/audit-logs`. O token de sessão fica em cookie HttpOnly com SameSite=Lax; o frontend não usa `localStorage` para token.

Google OAuth/OIDC é opcional. Para usar em desenvolvimento, configure valores fictícios substituindo pelos dados do seu projeto Google local:

```env
GOOGLE_OAUTH_ENABLED=true
GOOGLE_CLIENT_ID=your-google-client-id
GOOGLE_CLIENT_SECRET=your-google-client-secret
GOOGLE_REDIRECT_URI=http://localhost:8000/auth/google/callback
GOOGLE_AUTH_ALLOWED_EMAILS=admin@example.com
GOOGLE_AUTH_ALLOWED_DOMAINS=example.com
GOOGLE_AUTO_CREATE_USERS=false
```

Usuários criados automaticamente via Google, quando liberados por allowlist, nascem como `viewer`, nunca como `admin`.

## Como Rodar o Frontend

```bash
cd frontend
npm ci
npm run dev
```

Abra:

```text
http://localhost:3000
```

Demo principal:

```text
http://localhost:3000/assisted-demo
```

Se o backend estiver em outra porta, ajuste `NEXT_PUBLIC_API_URL` no `.env.local` do frontend.

## Rotas Frontend Úteis

| Rota | Objetivo |
| --- | --- |
| `/` | Home premium do produto. |
| `/assisted-demo` | Demo guiada recomendada. |
| `/before-pix` | Análise antes de uma ação de risco. |
| `/chatbot-demo` | Ingresso mock para análise local; orientação aparece apenas na tela, sem resposta ao remetente. |
| `/family-console` | Guardian Console para responsável. |
| `/intake` | Intake técnico com privacidade/redaction. |
| `/integrations` | Demos de conectores e integrações. |
| `/login` | Login local e entrada via Google OAuth opcional. |
| `/mfa` | Setup e verificação MFA/TOTP. |
| `/admin` | Painel administrativo de sessão, usuários, auditoria e status. |
| `/whatsapp-setup` | Pareia o número de WhatsApp (Evolution) via QR code. |
| `/ml-lab` | Laboratório rule-based/ML realista. |
| `/recovery` | Fluxo de recuperação. |
| `/trust-center` | Privacidade, limites e confiança. |

## Variáveis de Ambiente

Use `.env.example` como referência. Não commit `.env`, `.env.local`, tokens, números reais ou bancos locais.

| Variável | Exemplo local | Uso |
| --- | --- | --- |
| `NEXT_PUBLIC_API_URL` | `http://localhost:8000` | URL do backend usada pelo frontend. |
| `DRY_RUN` | `true` | Padrão seguro para integrações externas; não enviar ações reais no local/demo. |
| `STORAGE_BACKEND` | `memory` ou `sqlite` | Define storage local. |
| `SQLITE_DATABASE_URL` | `sqlite:///./cyberalerta_guardian.db` | Caminho SQLite local. |
| `STORE_FULL_MESSAGE` | `false` | Mantém apenas hash e preview curto em estado operacional novo. |
| `LOG_LEVEL` | `INFO` | Nível de logs planejado/configurável. |
| `ENABLE_AUDIT_LOG` | `true` | Flag documental para auditoria; manter ligada em ambientes controlados. |
| `RISK_ENGINE_VERSION` | `v1` | Versão do motor de risco para rastreabilidade. |
| `RULESET_VERSION` | `ruleset-local-v1` | Versão do conjunto de regras explicáveis. |
| `APP_ENV` | `development` | Ambiente da aplicação. |
| `API_KEY_ENABLED` | `false` | Ativa/desativa API key opcional. |
| `API_KEY_HEADER` | `X-CyberAlerta-API-Key` | Header esperado quando API key estiver ativa. |
| `CYBERALERTA_API_KEY` | vazio localmente | Chave local; nunca commitar valor real. |
| `ALLOWED_ORIGINS` | `http://localhost:3000,http://127.0.0.1:3000` | CORS do backend. Em produção, não use `*`. |
| `N8N_ALLOWED_ORIGINS` | `http://localhost:5678` | Origem local/controlada do n8n. |
| `TRUSTED_WEBHOOK_IPS` | vazio | Lista opcional de IPs confiáveis. |
| `MAX_MESSAGE_LENGTH` | `4000` | Limite de texto analisado. |
| `RATE_LIMIT_ENABLED` | `false` | Ativa rate limit em endpoints públicos/controlados. Obrigatório `true` em produção (a aplicação não sobe sem ele). |
| `RATE_LIMIT_PER_MINUTE` | `60` | Limite simples por minuto quando rate limit estiver ativo. |
| `AUTH_SECRET_KEY` | vazio no exemplo | Segredo para assinar sessão local; defina valor forte no `.env`, nunca no Git. |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Janela de access token reservada; não define hoje a duração do cookie único. |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duração atual da sessão assinada no cookie (não há fluxo de refresh separado). |
| `AUTH_COOKIE_NAME` | `cyberalerta_session` | Nome do cookie HttpOnly. |
| `AUTH_COOKIE_SECURE` | `false` local, `true` produção | Cookie Secure. |
| `AUTH_COOKIE_SAMESITE` | `lax` | Política SameSite do cookie. |
| `AUTH_RATE_LIMIT_ENABLED` | `true` | Rate limit básico em login/MFA. |
| `AUTH_REQUIRE_SENSITIVE_ROUTES` | `false` local, `true` produção | Exige sessão/role em rotas sensíveis antigas além da Admin API. |
| `GOOGLE_OAUTH_ENABLED` | `false` | Ativa OAuth Google opcional. |
| `GOOGLE_CLIENT_ID` | `your-google-client-id` | Client ID Google fictício/local. |
| `GOOGLE_CLIENT_SECRET` | `your-google-client-secret` | Client secret Google; nunca commitar valor real. |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/auth/google/callback` | Callback OAuth. |
| `GOOGLE_AUTH_ALLOWED_EMAILS` | `admin@example.com` | Allowlist de emails para auto-create Google. |
| `GOOGLE_AUTH_ALLOWED_DOMAINS` | `example.com` | Allowlist de domínios para auto-create Google. |
| `GOOGLE_AUTO_CREATE_USERS` | `false` | Se `true`, cria apenas usuários allowlisted como `viewer`. |
| `INITIAL_ADMIN_EMAIL` | vazio | Opcional apenas em dev para `scripts/create_admin.py`. |
| `INITIAL_ADMIN_NAME` | vazio | Opcional apenas em dev para `scripts/create_admin.py`. |
| `INITIAL_ADMIN_PASSWORD` | vazio | Opcional apenas em dev; nunca commitar valor real. |
| `N8N_WEBHOOK_SECRET` | vazio | Segredo local do webhook n8n; nunca commitar valor real. |
| `N8N_WEBHOOK_HEADER` | `X-N8N-CyberAlerta-Secret` | Header esperado para integração n8n MVP/controlada. |
| `N8N_BASE_URL` | vazio | URL local/controlada do n8n, quando usado. |
| `N8N_DRY_RUN` | `true` | Impede ação outbound real pelo fluxo n8n durante a demo. |
| `CHANNEL_PROVIDER` | `evolution` | Provider técnico de canal. |
| `DUAL_BOT_CHANNEL_PROVIDER` | `mock_whatsapp` | Provider ativo do Dual Bot. |
| `TRUSTED_CONTACT` | vazio | **Único** número que o bot pode contatar (o alerta vai só para ele; nunca para o remetente). Vazio => alerta simulado. Também configurável pela UI em `/whatsapp-setup` (persistido em SQLite). Aliases legados: `EVOLUTION_GUARDIAN_TO`, `DUAL_BOT_GUARDIAN_TO`. |
| `PROTECTED_PERSON_NUMBER` | vazio | Número da pessoa protegida (identificação; o bot nunca escreve para ele). Também configurável pela UI. |
| `HYBRID_LLM_*` | ver `.env.example` | Pipeline híbrido; padrão seguro `HYBRID_LLM_ENABLED=false` + `HYBRID_LLM_SHADOW_MODE=true`. |
| `EVOLUTION_API_URL` | `http://localhost:8080` | URL local da Evolution demo. |
| `EVOLUTION_API_KEY` | vazio | Chave local não commitada. |
| `EVOLUTION_INSTANCE_NAME` | `guardian-demo` | Instância local da Evolution demo. |
| `EVOLUTION_WEBHOOK_SECRET` | vazio | Segredo do webhook. Opcional em desenvolvimento; obrigatório em produção (a aplicação não sobe sem ele). |

## API Principal

### Canal WhatsApp — Evolution API (WhatsApp Web / Baileys)

O canal de WhatsApp usa a **Evolution API** (WhatsApp Web via Baileys): não-oficial,
gratuita, ideal para portfólio/demo. **Não é a API oficial do WhatsApp Business e não é
produção** — o número pode ser bloqueado pela Meta e a sessão pode cair, exigindo novo
pareamento por QR. A integração oficial paga (Meta Cloud API) foi removida deste MVP.

Suba a Evolution API localmente (Docker) e configure no `.env`:

```env
CHANNEL_PROVIDER=evolution
DUAL_BOT_CHANNEL_PROVIDER=evolution
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-local
EVOLUTION_INSTANCE_NAME=guardian-demo
EVOLUTION_WEBHOOK_SECRET=         # segredo do webhook (obrigatório em produção)
TRUSTED_CONTACT=                 # único número que o bot pode contatar (o alerta vai só para ele)
```

#### Pareamento (QR code) e endpoints

| Método | Rota | Finalidade | Protegido |
| --- | --- | --- | --- |
| `GET` | `/api/channels/evolution/status` | Estado da conexão (open/connecting/close). Aceita `?auto_reconnect=true`. | Sessão sensível |
| `GET` | `/api/channels/evolution/qr` | QR code (base64) para parear o número. | Sessão sensível |
| `POST` | `/api/channels/evolution/reconnect` | Força reconexão se a sessão cair. | Sessão sensível |
| `POST` | `/webhook/evolution` | Recebe mensagens inbound, normaliza e analisa; só pode alertar o contato de confiança após os gates. | `EVOLUTION_WEBHOOK_SECRET` (opcional em dev, obrigatório em produção) |

Fluxo de pareamento: abra `http://localhost:3000/whatsapp-setup` (requer login), escaneie o
QR com o WhatsApp (**Aparelhos conectados > Conectar aparelho**) e envie uma mensagem
suspeita para o número pareado. O CyberAlerta analisa em silêncio, registra o caso e, apenas
para risco alto com todos os gates liberados, alerta o contato de confiança. A tela faz polling
do status e oferece reconexão automática. Nada é enviado ao remetente.

**Aviso:** Nunca commitar `.env` com a `EVOLUTION_API_KEY` real. Canal não-oficial: risco de
ban do número e de reautenticação por QR. Não use para volume/produção.

| Método | Rota | Finalidade | Público/protegido | Status |
| --- | --- | --- | --- | --- |
| `GET` | `/health` | Health check da API. | Público local | Implementado. |
| `POST` | `/auth/login` | Login local email/senha. | Público; rate limit | Implementado. |
| `POST` | `/auth/logout` | Encerra sessão e limpa cookie. | Sessão opcional | Implementado. |
| `GET` | `/auth/me` | Descobre sessão atual pelo cookie HttpOnly. | Público | Implementado. |
| `POST` | `/auth/change-password` | Troca senha do usuário autenticado. | Sessão exigida | Implementado. |
| `POST` | `/auth/mfa/setup` | Gera segredo e QR TOTP. | Sessão exigida | Implementado. |
| `POST` | `/auth/mfa/enable` | Habilita MFA com código TOTP. | Sessão exigida | Implementado. |
| `POST` | `/auth/mfa/verify` | Valida token temporário MFA e cria sessão. | Público; rate limit | Implementado. |
| `POST` | `/auth/mfa/disable` | Desabilita MFA para usuário não-admin. | Sessão exigida | Implementado. |
| `GET` | `/auth/google/login` | Inicia Google OAuth/OIDC. | Público; desativado por padrão | Implementado. |
| `GET` | `/auth/google/callback` | Callback Google OAuth/OIDC. | Público; valida state/audience/email | Implementado. |
| `GET` | `/admin/users` | Lista usuários para administração. | Admin com MFA | Implementado. |
| `GET` | `/admin/audit-logs` | Lista auditoria de autenticação. | Admin com MFA | Implementado. |
| `GET` | `/examples` | Cenários de golpe de exemplo. | Público local | Implementado. |
| `POST` | `/analyze` | Analisa mensagem suspeita e retorna risco, decisão, Trust Lock e relatório parcial. | Local; API key opcional | Implementado. |
| `POST` | `/recovery` | Gera checklist de recuperação. | Local; API key opcional | Implementado. |
| `POST` | `/report` | Gera relatório estruturado. | Local; API key opcional | Implementado. |
| `GET` | `/simple-channel/status` | Status do canal simples. | Público local | Demo. |
| `POST` | `/simple-channel/submit` | Envia mensagem voluntária pelo canal simples. | Local/demo | Demo/mock. |
| `GET` | `/mock-whatsapp/fixtures` | Lista fixtures de mensagens. | Local/demo | Mock. |
| `POST` | `/mock-whatsapp/simulate-inbound` | Simula inbound WhatsApp. | Local/demo | Mock. |
| `GET` | `/mock-whatsapp/simulations` | Lista simulações executadas. | Local/demo | Mock. |
| `GET` | `/dual-bot/status` | Status do Dual Bot. | Público local | Adapter-first demo. |
| `POST` | `/dual-bot/mock/protected-message` | Simula mensagem da pessoa protegida. | Local/demo | Mock. |
| `POST` | `/dual-bot/provider/protected-message` | Recebe payload de provider ativo. | Protegido recomendado | Demo/controlado. |
| `GET` | `/dual-bot/cases/{case_id}/context` | Contexto do caso para responsável. | Protegido recomendado | Demo/local. |
| `POST` | `/dual-bot/cases/{case_id}/feedback` | Registra feedback do responsável. | Protegido recomendado | Auditável local. |
| `GET` | `/guardian-console/real/status` | Status do console operacional real/local. | Protegido recomendado | Demo/local. |
| `GET` | `/guardian-console/real/cases` | Lista casos do console real/local. | Protegido recomendado | Demo/local. |
| `GET` | `/guardian-console/real/cases/{case_id}` | Detalhe do caso. | Protegido recomendado | Demo/local. |
| `POST` | `/guardian-console/real/cases/{case_id}/feedback` | Feedback do responsável pelo console. | Protegido recomendado | Auditável local. |
| `GET` | `/guardian-console/status` | Status do console administrativo. | Protegido recomendado | Demo/storage local. |
| `GET` | `/guardian-console/cases` | Lista casos administrativos. | Protegido recomendado | Demo/storage local. |
| `GET` | `/guardian-console/cases/{case_id}` | Detalhe administrativo. | Protegido recomendado | Demo/storage local. |
| `PATCH` | `/guardian-console/cases/{case_id}/status` | Atualiza status administrativo. | Protegido recomendado | Demo/storage local. |
| `POST` | `/guardian-console/cases/from-channel` | Cria caso a partir do canal simples. | Protegido recomendado | Demo. |
| `GET` | `/consent/status` | Status de opt-in. | Protegido recomendado | Base local. |
| `POST` | `/consent/accept` | Registra aceite. | Protegido recomendado | Base local. |
| `POST` | `/consent/revoke` | Revoga consentimento. | Protegido recomendado | Base local. |
| `POST` | `/consent/bot/activate` | Ativa bot após opt-in. | Protegido recomendado | Base local. |
| `POST` | `/consent/bot/deactivate` | Desativa bot. | Protegido recomendado | Base local. |
| `POST` | `/consent/scopes` | Atualiza escopos. | Protegido recomendado | Base local. |
| `GET` | `/trusted-circle/status` | Status do Trusted Circle. | Protegido recomendado | Simulado. |
| `POST` | `/trusted-circle/escalate` | Escalonamento para círculo de confiança. | Protegido recomendado | Simulado, sem envio real. |
| `GET` | `/trusted-circle/escalations/{escalation_id}` | Detalhe do escalonamento. | Protegido recomendado | Simulado/storage local. |
| `POST` | `/proof-trust/assisted-session` | Cria sessão de Proof of Trust. | Protegido recomendado | Assistido/demo. |
| `GET` | `/proof-trust/assisted-session/{session_id}` | Consulta sessão. | Protegido recomendado | Assistido/demo. |
| `POST` | `/proof-trust/assisted-session/{session_id}/step` | Avança etapa. | Protegido recomendado | Assistido/demo. |
| `GET` | `/webhook/evolution/health` | Health Evolution demo. | Protegido recomendado | Demo local/controlado. |
| `POST` | `/webhook/evolution` | Webhook Evolution demo. | Segredo/API key recomendada | Demo, não oficial produção. |
| `GET` | `/settings/trusted-contact` | Lê pessoa protegida, contato de confiança e toggles de envio. | Protegido | Persistido em SQLite. |
| `PUT` | `/settings/trusted-contact` | Atualiza números e toggles (`dry_run`, `beta_real_send_enabled`); allowlist re-pinada ao contato. | Protegido | Runtime + persistência. |
| `GET` | `/guardian-console/real/cases/{case_id}/hybrid-decision` | Última decisão híbrida (regras + LLM + policy) do caso. | Protegido | Metadados auditáveis, sem conteúdo bruto. |
| `GET` | `/integrations/n8n/health` | Health da integração n8n em modo teste. | Público local | DRY_RUN/local. |
| `POST` | `/integrations/n8n/whatsapp/inbound` | Recebe payload WhatsApp normalizado pelo n8n e aciona análise segura. | `N8N_WEBHOOK_SECRET` quando configurado; rate limit opcional | MVP local/controlado; não é WhatsApp produção. |
| `POST` | `/integrations/n8n/recovery` | Aciona wrapper de recovery para workflow n8n. | `N8N_WEBHOOK_SECRET` quando configurado | DRY_RUN/local. |
| `POST` | `/integrations/n8n/guardian-feedback` | Registra feedback auditável vindo do workflow n8n. | `N8N_WEBHOOK_SECRET` quando configurado | DRY_RUN/local. |

## Integração n8n/WhatsApp

O n8n deve ser usado como camada de orquestração, não como cérebro de decisão. O fluxo alvo é:

1. Evolution Demo (não-oficial) ou webhook de teste recebe uma mensagem.
2. n8n normaliza metadados mínimos e chama o backend do CyberAlerta.
3. CyberAlerta calcula risco, sinais, Trust Lock e ação recomendada.
4. O backend devolve uma decisão estruturada com risco, caso, eventos e alerta ao responsável.
5. n8n executa a ação permitida: alertar o contato de confiança, iniciar recovery ou registrar log externo — **nunca responder ao remetente**.

Regra central:

```text
n8n orquestra. CyberAlerta decide.
```

### Teste rápido sem n8n instalado

Este teste chama diretamente o endpoint que o n8n chamaria. Ele não envia WhatsApp real e não usa API externa.

Com o backend rodando em `http://localhost:8000`, execute no PowerShell:

```powershell
$body = @{
  message_id = "n8n-local-demo-001"
  from = "masked-whatsapp-contact"
  to = "cyberalerta-demo"
  body = "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora."
  channel = "whatsapp"
  user_name = "Dona Lucia"
  trusted_contact_name = "Gabriel"
  trusted_contact_relation = "filho"
  already_acted = $false
} | ConvertTo-Json

Invoke-RestMethod `
  -Uri "http://localhost:8000/integrations/n8n/whatsapp/inbound" `
  -Method Post `
  -ContentType "application/json" `
  -Headers @{
    "X-Request-ID" = "req-local-demo-001"
    "X-N8N-Execution-ID" = "exec-local-demo-001"
  } `
  -Body $body
```

Resposta esperada:

- `status`: `processed`
- `case_id`: id local do caso
- `risk_score` e `risk_level`
- `n8n_action`: ação que o workflow deve seguir
- `user_message`: orientação de segurança exibida no console (nunca enviada ao remetente)
- `trusted_contact_message`: alerta sugerido ao contato confiável, quando aplicável

Se `N8N_WEBHOOK_SECRET` estiver configurado no backend, inclua também este header:

```powershell
"X-N8N-CyberAlerta-Secret" = "local-demo-secret-change-me"
```

### Rodando com n8n local

O n8n é opcional para desenvolvimento. Se quiser testar o desenho do workflow localmente com Docker:

```powershell
docker run -it --rm --name cyberalerta-n8n -p 5678:5678 -e N8N_SECURE_COOKIE=false n8nio/n8n
```

Abra:

```text
http://localhost:5678
```

Workflow mínimo:

1. Crie um `Webhook Trigger` com método `POST`.
2. Normalize os campos para o contrato do backend.
3. Adicione um nó `HTTP Request` apontando para:
   - `http://host.docker.internal:8000/integrations/n8n/whatsapp/inbound`, se o n8n estiver em Docker.
   - `http://localhost:8000/integrations/n8n/whatsapp/inbound`, se o n8n estiver rodando fora do Docker.
4. Envie `Content-Type: application/json`.
5. Envie `X-N8N-Execution-ID` com um identificador da execução.
6. Se `N8N_WEBHOOK_SECRET` estiver definido, envie o header configurado em `N8N_WEBHOOK_HEADER`.
7. Use o campo `n8n_action` da resposta para decidir o próximo passo.

Payload mínimo esperado pelo backend:

```json
{
  "message_id": "demo-message-001",
  "from": "masked-whatsapp-contact",
  "to": "cyberalerta-demo",
  "body": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
  "channel": "whatsapp",
  "user_name": "Dona Lucia",
  "trusted_contact_name": "Gabriel",
  "trusted_contact_relation": "filho",
  "already_acted": false
}
```

Ações atuais que o workflow deve tratar:

| `n8n_action` | Uso esperado no workflow |
| --- | --- |
| `ask_for_confirmation` | Mostrar orientação no console e encaminhar para verificação humana; não enviar ao remetente. |
| `alert_trusted_contact` | Alertar o contato confiável com contexto resumido. |
| `activate_trust_lock` | Tratar como risco alto e priorizar bloqueio/pausa antes da ação. |
| `start_recovery` | Iniciar fluxo de recuperação quando a pessoa já clicou, pagou ou informou código. |

## Confiabilidade Operacional

O projeto deve evitar o padrão "frontend bonito + chamada de modelo/API + resposta bonita". A direção arquitetural é sistema de decisão com estado próprio, auditoria, idempotência e reprocessamento controlado.

| Controle | Status atual | Direção |
| --- | --- | --- |
| Estado próprio | Parcial | Memory/SQLite local em módulos existentes; estado operacional n8n em memória na Fase 1. |
| Idempotência por `message_id` | Implementado em memória | Registro com TTL (1h) e limite de tamanho (100k): rejeita replay dentro da janela, aceita reenvio legítimo após expirar. Endpoint n8n retorna `last_response_json` para mensagem já processada. Produção multi-worker exigiria Redis/DB. |
| `X-Request-ID` | Parcial | Middleware aceita e ecoa o header para rastreio local/controlado. |
| `X-N8N-Execution-ID` | Parcial | Endpoint n8n aceita e ecoa o header para rastrear execução ponta a ponta. |
| Audit log | Parcial | Event Model e audit logs locais existem; falta padronizar request/trace. |
| Versionamento de ruleset | Planejado | `RISK_ENGINE_VERSION` e `RULESET_VERSION` estão documentados para rastreabilidade. |
| Retry controlado | Planejado | n8n deve reprocessar sem duplicar decisão. |
| Dead letter | Planejado | Mensagens falhas devem ir para fila/estado revisável. |
| Rate limit | Parcial | In-memory e opcional em `/analyze`, `/recovery` e `/integrations/n8n/whatsapp/inbound`. |
| Reprocessamento | Planejado | Deve exigir idempotência, auditoria e motivo explícito. |

## Exemplo de `/analyze`

```bash
curl -X POST http://localhost:8000/analyze ^
  -H "Content-Type: application/json" ^
  -d "{\"user_name\":\"Dona Lucia\",\"age_group\":\"elderly\",\"trusted_contact_name\":\"Gabriel\",\"trusted_contact_relation\":\"neto\",\"action_type\":\"pix\",\"channel\":\"whatsapp\",\"message\":\"Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.\",\"already_acted\":false}"
```

Linux/macOS:

```bash
curl -X POST http://localhost:8000/analyze \
  -H "Content-Type: application/json" \
  -d '{
    "user_name": "Dona Lucia",
    "age_group": "elderly",
    "trusted_contact_name": "Gabriel",
    "trusted_contact_relation": "neto",
    "action_type": "pix",
    "channel": "whatsapp",
    "message": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
    "already_acted": false
  }'
```

## Validações e Testes

Backend:

```bash
python -m compileall backend
```

```bash
cd backend
python -m pip install -r requirements-dev.txt
python -m pytest app/tests -q
```

Frontend:

```bash
cd frontend
npm ci
npx tsc --noEmit
npm run lint
npm run build
```

Testes e2e do frontend (Playwright; o `playwright.config.ts` sobe backend e frontend automaticamente, ou reutiliza servidores já em execução):

```bash
cd frontend
npx playwright install chromium
npm run test:e2e
```

Se estiver usando a venv já criada no Windows:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q
```

## Dataset e Métricas Medidas (v1)

Dataset rotulado: **305 mensagens** PT-BR (150 golpe / 155 legítimas, incluindo
hard negatives que citam pix/senha/banco/urgência legitimamente). Sintético,
escrito à mão, sem duplicatas — provenance em `backend/scripts/dataset_v1.py`,
materializado em `backend/data/scam_dataset_v1.jsonl`.

Avaliação roda o **código de produção real** (sem reimplementação):

```bash
backend/.venv/Scripts/python.exe backend/scripts/evaluate_dataset.py
# relatório completo: docs/metrics_v1.md
```

Resultados medidos (regras determinísticas, sem LLM — postura padrão):

| Camada | Precisão | Recall | FPR |
| --- | --- | --- | --- |
| Alerta ao contato (HIGH, score ≥ 65) | **100%** | 10% | **0%** |
| Criação de caso no console (score ≥ 40) | 96,7% | 58% | 1,9% |
| Policy Engine sem LLM → fila de revisão | — | 82,7% dos golpes | 37% das legítimas |

Leitura honesta: o alerta automático é **conservador por design** — nunca
incomodou a família com falso alarme no dataset, mas captura só 10% dos golpes
sozinho (calibrado de 70→65 após a 1ª medição, que dava 4%). A rede de segurança
é a fila de revisão: a Policy Engine encaminha 82,7% dos golpes para o console.
A lacuna de recall está nos golpes com vocabulário fora das regras (falso banco,
prêmio, emprego, investimento) — exatamente o que a análise LLM em **shadow mode**
deve cobrir no piloto. Regressão travada em `backend/app/tests/test_dataset_metrics.py`.

### Piloto com famílias (protocolo curto)

1. Parear um número de teste em `/whatsapp-setup` e cadastrar pessoa protegida +
   contato de confiança.
2. Rodar 1–2 semanas com `DRY_RUN=true` + `HYBRID_LLM_ENABLED=true` +
   `HYBRID_LLM_SHADOW_MODE=true`: nada é enviado; decisões ficam gravadas.
3. Revisar semanalmente no Guardian Console: falsos positivos da fila, decisões
   híbridas gravadas, golpes perdidos relatados pela família.
4. Só depois de FPR real aceitável: `DRY_RUN=false` + allowlist com o contato.

## Estrutura de Pastas

```text
.
├── backend/
│   ├── main.py
│   └── app/
│       ├── agents/
│       ├── channel_adapters/
│       ├── channels/
│       ├── consent/
│       ├── controlled_agents/
│       ├── core/
│       ├── dual_bot/
│       ├── event_model/
│       ├── evolution_demo/
│       ├── guardian_console/
│       ├── hybrid/
│       ├── llm/
│       ├── mock_whatsapp/
│       ├── pattern_intelligence/
│       ├── proof_trust/
│       ├── protected_response/
│       ├── services/
│       ├── storage/
│       └── trusted_circle/
├── frontend/
│   ├── app/
│   ├── components/
│   ├── e2e/
│   ├── lib/
│   ├── public/
│   └── styles/
├── docs/
├── scripts/
├── .env.example
└── README.md
```

## Segurança, Privacidade e Limites

- Não commit `.env`, `.env.local`, banco SQLite local, tokens ou números reais.
- O `.gitignore` deve manter fora do Git: `node_modules`, `.next`, venv, caches e bancos locais.
- A demo usa aliases como "Dona Lucia" e "Gabriel".
- A pessoa protegida compartilha conteúdo voluntariamente; não há monitoramento invisível.
- O sistema não pede senha, código, dados bancários ou documentos reais.
- O canal Evolution é não-oficial e voltado a demo; a integração LLM opcional permanece desligada/shadow por padrão.
- n8n possui endpoint MVP local/controlado, mas ainda não é integração de produção nem substitui API oficial de WhatsApp.
- API key é opcional e desativada no desenvolvimento local por padrão.
- Sessão humana usa cookie HttpOnly; não use `localStorage` para tokens.
- MFA/TOTP é obrigatório para acessar Admin API como administrador.
- Google OAuth fica desativado por padrão e não transforma usuário em admin automaticamente.
- `AUTH_SECRET_KEY`, `GOOGLE_CLIENT_SECRET`, `N8N_WEBHOOK_SECRET`, tokens e números reais devem existir apenas em `.env` local ou secret manager.
- Rotas inbound do n8n continuam usando `N8N_WEBHOOK_SECRET` próprio; não troque esse controle por login humano.
- SQLite local é útil para demo, mas não é banco de produção.
- O MVP não substitui orientação jurídica, bancária ou policial.

## Roadmap Objetivo

- Consolidar persistência com migrações e retenção formal.
- Evoluir autenticação para multi-tenant, reset de senha, recovery codes e políticas por organização.
- Separar ambientes de demo, homologação e produção.
- Ampliar testes de frontend e e2e.
- Adicionar observabilidade e logs estruturados.
- Formalizar políticas LGPD, opt-in e exclusão.
- Implementar provider oficial de WhatsApp somente com opt-in e compliance.
- Preparar dataset/ground truth para ML futuro.

## Troubleshooting

### Backend não sobe

- Confirme que a venv está ativa.
- Rode `python -m pip install -r requirements.txt`.
- Confirme que a porta `8000` está livre.
- Teste `python -m uvicorn main:app --reload --port 8000` dentro de `backend`.

### Frontend não conecta no backend

- Confirme que o backend responde em `http://localhost:8000/health`.
- Verifique `NEXT_PUBLIC_API_URL`.
- Reinicie `npm run dev` após alterar `.env.local`.

### Login funciona, mas `/admin` bloqueia

- Admin precisa de MFA ativo.
- Entre em `/login`, abra `/mfa`, gere a chave TOTP, confirme o código e volte para `/admin`.
- Se perder o MFA em ambiente local, recrie ou sobrescreva o admin com `scripts/create_admin.py` e configure MFA de novo.

### Google retorna "Google OAuth disabled"

- O padrão seguro é `GOOGLE_OAUTH_ENABLED=false`.
- Configure `GOOGLE_CLIENT_ID`, `GOOGLE_CLIENT_SECRET` e `GOOGLE_REDIRECT_URI` apenas no `.env` local.
- Confirme que o callback no Google Console é `http://localhost:8000/auth/google/callback`.

### Porta 3000 ocupada

Use outra porta:

```bash
npm run dev -- -p 3001
```

### `python` não é reconhecido no Windows

Use:

```powershell
py -m venv .venv
```

ou o Python da venv:

```powershell
.\.venv\Scripts\python.exe -m pytest app/tests -q
```

### Lint falha porque `eslint` não existe

Rode dentro de `frontend`:

```bash
npm install
npm run lint
```

### Casos somem ao reiniciar

Com `STORAGE_BACKEND=memory`, os dados são temporários. Para demo local com persistência simples:

```env
STORAGE_BACKEND=sqlite
SQLITE_DATABASE_URL=sqlite:///./cyberalerta_guardian.db
STORE_FULL_MESSAGE=false
```

Não commit o arquivo `.db`.
