# Setup local completo — CyberAlerta Guardian

Guia completo de instalação e execução. Para o caminho mais rápido (só rodar a demo), veja a seção "Como executar" do [README](../README.md).

## Pré-requisitos

- Python 3.13 (mesma versão do CI).
- Node.js 22 (mesma versão do CI; versões mais novas podem funcionar, mas não são a baseline).
- npm.
- Git.
- Docker opcional, necessário para Evolution API + PostgreSQL + Redis locais.

No Windows, se `python` não estiver no PATH, use `py` ou crie/ative uma venv explicitamente.

## Setup rápido (dois terminais)

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

## Como rodar o backend (passo a passo)

```bash
cd backend
python -m venv .venv
```

Windows PowerShell: `.\.venv\Scripts\Activate.ps1` · Linux/macOS: `source .venv/bin/activate`

```bash
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
curl http://localhost:8000/health
```

Swagger/OpenAPI: `http://localhost:8000/docs`

## Autenticação, admin e MFA

O backend possui autenticação local, Google OAuth opcional, MFA/TOTP, RBAC e auditoria. O estado padrão continua seguro para demo local: Google fica desativado e nenhum segredo real deve ser commitado.

Para criar o primeiro administrador local, rode com a venv ativa:

```powershell
cd cyberalerta-guardian
.\backend\.venv\Scripts\python.exe scripts\create_admin.py
```

O script pede email, nome e senha, valida força mínima (12 caracteres, maiúscula, minúscula, número e símbolo) e não imprime a senha. Em desenvolvimento, também é possível usar `INITIAL_ADMIN_EMAIL`, `INITIAL_ADMIN_NAME` e `INITIAL_ADMIN_PASSWORD` — nunca coloque esses valores no Git.

**Persistência do admin:** o padrão `STORAGE_BACKEND=memory` é volátil — o admin criado some ao reiniciar. Para persistir localmente:

```env
STORAGE_BACKEND=sqlite
SQLITE_DATABASE_URL=sqlite:///./cyberalerta_guardian.db
```

Fluxo recomendado: suba o backend → crie o admin (`scripts/create_admin.py`) → `http://localhost:3000/login` → entre com email/senha → `http://localhost:3000/mfa` e habilite TOTP → `http://localhost:3000/admin`.

Administradores sem MFA conseguem entrar apenas para configurar MFA, mas não acessam `/admin/users` nem `/admin/audit-logs`. O token de sessão fica em cookie HttpOnly com SameSite=Lax; o frontend não usa `localStorage` para token.

Google OAuth/OIDC é opcional:

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

## Como rodar o frontend

```bash
cd frontend
npm ci
npm run dev
```

Abra `http://localhost:3000`. Se o backend estiver em outra porta, ajuste `NEXT_PUBLIC_API_URL` no `.env.local` do frontend.

### Rotas frontend úteis

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

## Variáveis de ambiente

Use `.env.example` (raiz do repo) como referência — está atualizado com todas as variáveis abaixo. Não commit `.env`, `.env.local`, tokens, números reais ou bancos locais.

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
| `RATE_LIMIT_ENABLED` | `false` | Ativa rate limit em endpoints públicos/controlados. Obrigatório `true` em produção. |
| `RATE_LIMIT_PER_MINUTE` | `60` | Limite simples por minuto quando rate limit estiver ativo. |
| `AUTH_SECRET_KEY` | vazio no exemplo | Segredo para assinar sessão local; defina valor forte no `.env`, nunca no Git. |
| `AUTH_ACCESS_TOKEN_EXPIRE_MINUTES` | `15` | Janela de access token reservada; não define hoje a duração do cookie único. |
| `AUTH_REFRESH_TOKEN_EXPIRE_DAYS` | `7` | Duração atual da sessão assinada no cookie. |
| `AUTH_COOKIE_NAME` | `cyberalerta_session` | Nome do cookie HttpOnly. |
| `AUTH_COOKIE_SECURE` | `false` local, `true` produção | Cookie Secure. |
| `AUTH_COOKIE_SAMESITE` | `lax` | Política SameSite do cookie. |
| `AUTH_RATE_LIMIT_ENABLED` | `true` | Rate limit básico em login/MFA. |
| `AUTH_REQUIRE_SENSITIVE_ROUTES` | `false` local, `true` produção | Exige sessão/role em rotas sensíveis antigas além da Admin API. |
| `GOOGLE_OAUTH_ENABLED` | `false` | Ativa OAuth Google opcional. |
| `GOOGLE_CLIENT_ID` / `GOOGLE_CLIENT_SECRET` | fictícios | Credenciais Google locais; nunca commitar valor real. |
| `GOOGLE_REDIRECT_URI` | `http://localhost:8000/auth/google/callback` | Callback OAuth. |
| `GOOGLE_AUTH_ALLOWED_EMAILS` / `GOOGLE_AUTH_ALLOWED_DOMAINS` | exemplo | Allowlist de auto-create Google. |
| `GOOGLE_AUTO_CREATE_USERS` | `false` | Se `true`, cria apenas usuários allowlisted como `viewer`. |
| `INITIAL_ADMIN_EMAIL` / `_NAME` / `_PASSWORD` | vazio | Opcional apenas em dev; nunca commitar valor real. |
| `N8N_WEBHOOK_SECRET` / `N8N_WEBHOOK_HEADER` / `N8N_BASE_URL` / `N8N_DRY_RUN` | ver `.env.example` | Integração n8n MVP/controlada. |
| `CHANNEL_PROVIDER` | `evolution` | Provider técnico de canal. |
| `DUAL_BOT_CHANNEL_PROVIDER` | `mock_whatsapp` | Provider ativo do Dual Bot. |
| `TRUSTED_CONTACT` | vazio | **Único** número que o bot pode contatar. Também configurável via UI em `/whatsapp-setup`. |
| `PROTECTED_PERSON_NUMBER` | vazio | Número da pessoa protegida (identificação; o bot nunca escreve para ele). |
| `HYBRID_LLM_*` | ver `.env.example` | Pipeline híbrido; padrão seguro `HYBRID_LLM_ENABLED=false` + `HYBRID_LLM_SHADOW_MODE=true`. |
| `EVOLUTION_API_URL` / `_API_KEY` / `_INSTANCE_NAME` / `_WEBHOOK_SECRET` | ver acima | Evolution API local. |

## Dataset e métricas medidas (v1)

Dataset rotulado: **305 mensagens** PT-BR (150 golpe / 155 legítimas, incluindo hard negatives que citam pix/senha/banco/urgência legitimamente). Sintético, escrito à mão, sem duplicatas — provenance em `backend/scripts/dataset_v1.py`, materializado em `backend/data/scam_dataset_v1.jsonl`.

```bash
backend/.venv/Scripts/python.exe backend/scripts/evaluate_dataset.py
# relatório completo: docs/metrics_v1.md
```

Resultados medidos (regras determinísticas, sem LLM — postura padrão): ver [`metrics_v1.md`](./metrics_v1.md) para a tabela completa de precisão/recall/FPR por camada e a leitura honesta dos falsos negativos/positivos.

### Piloto com famílias (protocolo curto)

1. Parear um número de teste em `/whatsapp-setup` e cadastrar pessoa protegida + contato de confiança.
2. Rodar 1–2 semanas com `DRY_RUN=true` + `HYBRID_LLM_ENABLED=true` + `HYBRID_LLM_SHADOW_MODE=true`: nada é enviado; decisões ficam gravadas.
3. Revisar semanalmente no Guardian Console: falsos positivos da fila, decisões híbridas gravadas, golpes perdidos relatados pela família.
4. Só depois de FPR real aceitável: `DRY_RUN=false` + allowlist com o contato.

## Deploy de referência (piloto, não produção multi-tenant)

Guia completo: [`server-deployment.md`](./server-deployment.md).

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

```bash
npm run dev -- -p 3001
```

### `python` não é reconhecido no Windows

```powershell
py -m venv .venv
```

ou use o Python da venv: `.\.venv\Scripts\python.exe -m pytest app/tests -q`

### Lint falha porque `eslint` não existe

```bash
cd frontend
npm install
npm run lint
```

### Casos somem ao reiniciar

Com `STORAGE_BACKEND=memory`, os dados são temporários. Para persistência simples local:

```env
STORAGE_BACKEND=sqlite
SQLITE_DATABASE_URL=sqlite:///./cyberalerta_guardian.db
STORE_FULL_MESSAGE=false
```

Não commit o arquivo `.db`.
