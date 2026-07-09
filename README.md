# CyberAlerta Guardian

**Antes do Pix. Antes do clique. Antes do prejuízo.**

CyberAlerta Guardian é um MVP técnico de intervenção pré-dano contra golpes digitais. O projeto demonstra como uma pessoa protegida pode encaminhar voluntariamente uma mensagem suspeita, receber uma orientação curta e segura, e envolver um responsável antes de realizar uma ação de risco como Pix, clique em link, envio de código ou instalação de app.

O projeto está em estágio **MVP/demo técnica**. Ele não é produção, não monitora conversas automaticamente, não substitui banco, polícia, advogado ou canais oficiais, e não deve ser vendido como detecção infalível de fraude.

## Status atual

O CyberAlerta Guardian está em **Beta Técnico Local**.

O sistema já possui backend FastAPI, frontend Next.js, autenticação segura com Google OIDC, MFA/TOTP, recovery codes com Argon2id, RBAC, auditoria, rate limit, painel admin e integração n8n validada em ambiente local.

A integração com WhatsApp Business Cloud está preparada em nível de workflow, mas a ativação real depende da liberação/provisionamento da Meta. No momento, o envio real pelo WhatsApp ainda não deve ser declarado como ativo.

## Problema

Golpes digitais por engenharia social exploram pressa, confiança familiar, medo e falsa autoridade. Muitas vítimas só percebem o risco depois de transferir dinheiro, clicar em um link ou enviar um código.

O CyberAlerta Guardian foca no momento anterior ao dano:

- antes do Pix;
- antes do clique;
- antes de enviar senha, código ou documento;
- antes de instalar aplicativo remoto;
- antes de responder a um contato suspeito.

## Solução

O Guardian organiza uma proteção assistida:

1. a pessoa protegida compartilha um trecho suspeito;
2. o backend analisa sinais de risco;
3. o sistema gera uma resposta curta e calma;
4. um caso aparece no Guardian Console;
5. o responsável revisa evidências, risco e histórico;
6. o fluxo recomenda pausa, verificação por canal confiável e Proof of Trust;
7. feedback humano atualiza o caso e melhora a base futura.

## Status Real

| Área | Status | Observação |
| --- | --- | --- |
| Backend FastAPI | Implementado | API local com análise, console, canais mock/demo e consentimento. |
| Frontend Next.js | Implementado | Interface demo com Home, `/assisted-demo`, console, intake e telas auxiliares. |
| `/health` | Implementado | Health check do backend. |
| `/analyze` | Implementado | Fluxo principal de análise rule-based/agentic local. |
| `/assisted-demo` | Implementado | Rota recomendada para apresentar o produto. |
| Guardian Console | Implementado para demo/local | Inclui caso, risco, timeline, feedback e consentimento. |
| Event Model | Implementado em memória | Base auditável local para eventos, casos e avaliações. |
| Pattern Intelligence | Implementado com regras | Sem ML pesado e sem IA externa. |
| Agentes controlados | Implementados | Sem agente autônomo livre e sem LLM externo. |
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
  -> análise de risco
  -> resposta protegida
  -> Guardian Console
  -> Trust Lock
  -> Trusted Circle
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
- Twilio Sandbox Adapter para POC controlada.
- Dual Bot Flow:
  - Bot Protegido;
  - Bot Responsável;
  - resposta segura;
  - alerta ao responsável;
  - feedback auditável.
- Event Model com eventos, casos, mensagens e risk assessments.
- Pattern Intelligence rule-based.
- Agentes controlados:
  - `TriageAgent`;
  - `SafeReplyAgent`;
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
- Autenticação local por email/senha com hash PBKDF2-HMAC.
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
- Evolution API é apenas provider de demonstração técnica.
- Twilio Sandbox é somente POC/sandbox, não produto final.
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
- Testes end-to-end e cobertura ampliada no frontend.
- Deploy controlado para piloto.
- Dataset/ground truth para ML futuro, sem treinar modelo agora.

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
    +-- twilio_sandbox/          POC sandbox controlada
    +-- evolution_demo/          provider demo local/controlado
```

No desenho-alvo, o n8n é o orquestrador de canais: recebe eventos do WhatsApp ou de webhooks, chama o backend do CyberAlerta, recebe a decisão e executa a resposta/alerta. O backend continua sendo o cérebro de decisão: risco, Trust Lock, Proof of Trust, Recovery, auditoria e regras explicáveis ficam no CyberAlerta.

```text
WhatsApp Business Cloud API / Twilio / Evolution / Webhook de teste
        |
        v
n8n
        |
        v
CyberAlerta Guardian Backend
        |
        v
n8n
        |
        v
resposta ao usuário / alerta familiar / recovery / log externo
```

## Stack Técnica

### Backend

- Python
- FastAPI
- Pydantic
- Uvicorn
- Pytest
- SQLite opcional via biblioteca padrão

### Frontend

- Next.js
- React
- TypeScript
- Tailwind CSS
- Framer Motion
- Three.js
- ESLint

## Pré-Requisitos

- Python 3.11+ recomendado.
- Node.js compatível com Next.js 16.
- npm.
- Git.
- Docker opcional, apenas se quiser rodar o n8n localmente em container.

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
npm install
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
npm install
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
| `/chatbot-demo` | Canal simples/mock para pessoa protegida. |
| `/family-console` | Guardian Console para responsável. |
| `/intake` | Intake técnico com privacidade/redaction. |
| `/integrations` | Demos de conectores e integrações. |
| `/login` | Login local e entrada via Google OAuth opcional. |
| `/mfa` | Setup e verificação MFA/TOTP. |
| `/admin` | Painel administrativo de sessão, usuários, auditoria e status. |
| `/whatsapp-setup` | Pareia o número de WhatsApp (Evolution) via QR code. |
| `/ml-lab` | Laboratório rule-based/ML realista. |
| `/recovery` | Fluxo de recuperação. |
| `/report` | Relatório/registro. |
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
| `RATE_LIMIT_ENABLED` | `false` | Ativa rate limit em endpoints públicos/controlados. |
| `RATE_LIMIT_PER_MINUTE` | `60` | Limite simples por minuto quando rate limit estiver ativo. |
| `AUTH_SECRET_KEY` | vazio no exemplo | Segredo para assinar sessão local; defina valor forte no `.env`, nunca no Git. |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Expiração curta do cookie de sessão. |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Reservado para evolução de refresh token. |
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
| `N8N_DRY_RUN` | `true` | Impede execução real de resposta/alerta no n8n durante demo. |
| `CHANNEL_PROVIDER` | `twilio_sandbox` | Provider técnico de canal. |
| `DUAL_BOT_CHANNEL_PROVIDER` | `mock_whatsapp` | Provider ativo do Dual Bot. |
| `DUAL_BOT_GUARDIAN_TO` | vazio | Destino simulado/controlado do responsável. |
| `TWILIO_ACCOUNT_SID` | vazio | Somente sandbox/POC. |
| `TWILIO_AUTH_TOKEN` | vazio | Somente sandbox/POC. |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+1XXXXXXXXXX` | Número fictício/sandbox. |
| `TWILIO_WEBHOOK_SECRET` | vazio | Segredo de webhook sandbox. |
| `TWILIO_STATUS_CALLBACK_URL` | vazio | Callback de status sandbox. |
| `TWILIO_VALIDATE_SIGNATURE` | `false` | Validação de assinatura Twilio em ambiente controlado. |
| `EVOLUTION_API_URL` | `http://localhost:8080` | URL local da Evolution demo. |
| `EVOLUTION_API_KEY` | vazio | Chave local não commitada. |
| `EVOLUTION_INSTANCE_NAME` | `guardian-demo` | Instância local da Evolution demo. |
| `EVOLUTION_WEBHOOK_SECRET` | vazio | Segredo opcional de webhook demo. |

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
EVOLUTION_GUARDIAN_TO=            # número do responsável (opcional)
EVOLUTION_WEBHOOK_SECRET=         # segredo opcional do webhook
```

#### Pareamento (QR code) e endpoints

| Método | Rota | Finalidade | Protegido |
| --- | --- | --- | --- |
| `GET` | `/api/channels/evolution/status` | Estado da conexão (open/connecting/close). Aceita `?auto_reconnect=true`. | Sessão sensível |
| `GET` | `/api/channels/evolution/qr` | QR code (base64) para parear o número. | Sessão sensível |
| `POST` | `/api/channels/evolution/reconnect` | Força reconexão se a sessão cair. | Sessão sensível |
| `POST` | `/webhook/evolution` | Recebe mensagens inbound e aciona risco/resposta/alerta. | `EVOLUTION_WEBHOOK_SECRET` opcional |

Fluxo de pareamento: abra `http://localhost:3000/whatsapp-setup` (requer login), escaneie o
QR com o WhatsApp (**Aparelhos conectados > Conectar aparelho**) e envie uma mensagem
suspeita para o número pareado. O CyberAlerta analisa o risco, responde de forma protegida
e alerta o responsável. A tela faz polling do status e oferece reconexão automática.

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
| `GET` | `/api/channels/twilio/whatsapp/health` | Health do Twilio Sandbox. | Protegido recomendado | Sandbox/POC. |
| `POST` | `/api/channels/twilio/whatsapp/inbound` | Webhook inbound Twilio. | Assinatura/API key recomendada | Sandbox/POC, não produção. |
| `POST` | `/api/channels/twilio/whatsapp/status` | Callback de status Twilio. | Assinatura/API key recomendada | Sandbox/POC, não produção. |
| `GET` | `/webhook/evolution/health` | Health Evolution demo. | Protegido recomendado | Demo local/controlado. |
| `POST` | `/webhook/evolution` | Webhook Evolution demo. | Segredo/API key recomendada | Demo, não oficial produção. |
| `POST` | `/protected-response/generate` | Gera resposta curta para pessoa protegida. | Local/demo | Demo/local. |
| `GET` | `/integrations/n8n/health` | Health da integração n8n em modo teste. | Público local | DRY_RUN/local. |
| `POST` | `/integrations/n8n/whatsapp/inbound` | Recebe payload WhatsApp normalizado pelo n8n e aciona análise segura. | `N8N_WEBHOOK_SECRET` quando configurado; rate limit opcional | MVP local/controlado; não é WhatsApp produção. |
| `POST` | `/integrations/n8n/recovery` | Aciona wrapper de recovery para workflow n8n. | `N8N_WEBHOOK_SECRET` quando configurado | DRY_RUN/local. |
| `POST` | `/integrations/n8n/guardian-feedback` | Registra feedback auditável vindo do workflow n8n. | `N8N_WEBHOOK_SECRET` quando configurado | DRY_RUN/local. |

## Integração n8n/WhatsApp

O n8n deve ser usado como camada de orquestração, não como cérebro de decisão. O fluxo alvo é:

1. WhatsApp Business Cloud API, Twilio Sandbox, Evolution Demo ou webhook de teste recebe uma mensagem.
2. n8n normaliza metadados mínimos e chama o backend do CyberAlerta.
3. CyberAlerta calcula risco, sinais, Trust Lock, ação recomendada e resposta segura.
4. O backend devolve uma decisão estruturada com risco, caso, eventos, resposta protegida e alerta ao responsável.
5. n8n executa a ação: responder usuário, alertar contato confiável, iniciar recovery ou registrar log externo.

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
- `user_message`: resposta segura para a pessoa protegida
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
| `ask_for_confirmation` | Responder com orientação curta e pedir verificação segura. |
| `alert_trusted_contact` | Alertar o contato confiável com contexto resumido. |
| `activate_trust_lock` | Tratar como risco alto e priorizar bloqueio/pausa antes da ação. |
| `start_recovery` | Iniciar fluxo de recuperação quando a pessoa já clicou, pagou ou informou código. |

## Confiabilidade Operacional

O projeto deve evitar o padrão "frontend bonito + chamada de modelo/API + resposta bonita". A direção arquitetural é sistema de decisão com estado próprio, auditoria, idempotência e reprocessamento controlado.

| Controle | Status atual | Direção |
| --- | --- | --- |
| Estado próprio | Parcial | Memory/SQLite local em módulos existentes; estado operacional n8n em memória na Fase 1. |
| Idempotência por `message_id` | Parcial | Endpoint n8n retorna `last_response_json` para mensagem já processada; precisa avançar para SQLite/dead letter/retry operacional. |
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
python -m pytest app/tests -q
```

Frontend:

```bash
cd frontend
npm install
npm run lint
npm run build
```

Se estiver usando a venv já criada no Windows:

```powershell
.\backend\.venv\Scripts\python.exe -m pytest backend/app/tests -q
```

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
│       ├── mock_whatsapp/
│       ├── pattern_intelligence/
│       ├── proof_trust/
│       ├── protected_response/
│       ├── services/
│       ├── storage/
│       ├── trusted_circle/
│       └── twilio_sandbox/
├── frontend/
│   ├── app/
│   ├── components/
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
- Integrações externas são mock, demo ou sandbox, salvo implementação futura explícita.
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
