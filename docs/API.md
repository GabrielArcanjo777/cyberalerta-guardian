# API — CyberAlerta Guardian

Referência completa dos endpoints do backend FastAPI. Para o caminho rápido de execução local, veja o [README](../README.md); para setup completo, [`LOCAL_SETUP.md`](./LOCAL_SETUP.md).

Swagger/OpenAPI interativo, sempre atualizado a partir do código: `http://localhost:8000/docs` (com o backend rodando localmente).

## Canal WhatsApp — Evolution API (WhatsApp Web / Baileys)

O canal de WhatsApp usa a **Evolution API** (WhatsApp Web via Baileys): não-oficial, gratuita, ideal para portfólio/demo. **Não é a API oficial do WhatsApp Business e não é produção** — o número pode ser bloqueado pela Meta e a sessão pode cair, exigindo novo pareamento por QR.

```env
CHANNEL_PROVIDER=evolution
DUAL_BOT_CHANNEL_PROVIDER=evolution
EVOLUTION_API_URL=http://localhost:8080
EVOLUTION_API_KEY=sua-chave-local
EVOLUTION_INSTANCE_NAME=guardian-demo
EVOLUTION_WEBHOOK_SECRET=         # segredo do webhook (obrigatório em produção)
TRUSTED_CONTACT=                 # único número que o bot pode contatar
```

| Método | Rota | Finalidade | Protegido |
| --- | --- | --- | --- |
| `GET` | `/api/channels/evolution/status` | Estado da conexão (open/connecting/close). Aceita `?auto_reconnect=true`. | Sessão sensível |
| `GET` | `/api/channels/evolution/qr` | QR code (base64) para parear o número. | Sessão sensível |
| `POST` | `/api/channels/evolution/reconnect` | Força reconexão se a sessão cair. | Sessão sensível |
| `POST` | `/webhook/evolution` | Recebe mensagens inbound, normaliza e analisa; só pode alertar o contato de confiança após os gates. | `EVOLUTION_WEBHOOK_SECRET` (opcional em dev, obrigatório em produção) |

Fluxo de pareamento: abra `http://localhost:3000/whatsapp-setup` (requer login), escaneie o QR com o WhatsApp (**Aparelhos conectados > Conectar aparelho**) e envie uma mensagem suspeita para o número pareado.

**Aviso:** nunca commitar `.env` com a `EVOLUTION_API_KEY` real. Canal não-oficial: risco de ban do número. Não use para volume/produção.

## Endpoints principais

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
| `POST` | `/devices/pairing-invitations` | Gera convite de pareamento (token) para um contato de confiança. | Admin/Analyst da organização | Implementado. |
| `POST` | `/devices/pair` | Consome o token de convite e registra o dispositivo (app Android). | Público (token de uso único) | Implementado. |
| `GET` | `/devices` | Lista dispositivos pareados da organização do ator. | Admin/Analyst da organização | Implementado; IDOR entre orgs testado (404). |
| `GET` | `/devices/{device_id}` | Detalhe de um dispositivo. | Admin/Analyst da organização | Implementado. |
| `POST` | `/devices/{device_id}/revoke` | Revoga um dispositivo pareado (401 imediato em ações seguintes). | Admin/Analyst da organização | Implementado. |
| `POST` | `/devices/me/push-token` | Registra/atualiza o token de push (FCM) do dispositivo autenticado. | Sessão de dispositivo (`X-Device-Session`) | Implementado. |
| `POST` | `/devices/{device_id}/test-push` | Dispara um push de teste real via FCM para o dispositivo. | Admin/Analyst da organização | Implementado. |
| `GET` | `/devices/me/alerts/{alert_id}` | Detalhe do alerta recebido pelo dispositivo (payload mínimo). | Sessão de dispositivo | Implementado. |
| `POST` | `/devices/me/alerts/{alert_id}/ack` | Confirma entrega/abertura/ação do alerta pelo dispositivo. | Sessão de dispositivo | Implementado. |

## Exemplo de `/analyze`

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

## Integração n8n/WhatsApp

O n8n deve ser usado como camada de orquestração, não como cérebro de decisão:

```text
n8n orquestra. CyberAlerta decide.
```

1. Evolution Demo (não-oficial) ou webhook de teste recebe uma mensagem.
2. n8n normaliza metadados mínimos e chama o backend do CyberAlerta.
3. CyberAlerta calcula risco, sinais, Trust Lock e ação recomendada.
4. O backend devolve uma decisão estruturada com risco, caso, eventos e alerta ao responsável.
5. n8n executa a ação permitida: alertar o contato de confiança, iniciar recovery ou registrar log externo — **nunca responder ao remetente**.

### Teste rápido sem n8n instalado (PowerShell)

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

Resposta esperada: `status: processed`, `case_id`, `risk_score`/`risk_level`, `n8n_action`, `user_message` (orientação exibida no console, nunca enviada ao remetente), `trusted_contact_message` (alerta sugerido, quando aplicável).

Se `N8N_WEBHOOK_SECRET` estiver configurado, inclua `"X-N8N-CyberAlerta-Secret" = "local-demo-secret-change-me"`.

### Rodando com n8n local

```powershell
docker run -it --rm --name cyberalerta-n8n -p 5678:5678 -e N8N_SECURE_COOKIE=false n8nio/n8n
```

Abra `http://localhost:5678`, crie um `Webhook Trigger` (POST), normalize os campos para o contrato acima e aponte um nó `HTTP Request` para `http://host.docker.internal:8000/integrations/n8n/whatsapp/inbound` (Docker) ou `http://localhost:8000/...` (fora do Docker). Documentação completa em [`docs/n8n/`](./n8n/README.md).

| `n8n_action` | Uso esperado no workflow |
| --- | --- |
| `ask_for_confirmation` | Mostrar orientação no console e encaminhar para verificação humana; não enviar ao remetente. |
| `alert_trusted_contact` | Alertar o contato confiável com contexto resumido. |
| `activate_trust_lock` | Tratar como risco alto e priorizar bloqueio/pausa antes da ação. |
| `start_recovery` | Iniciar fluxo de recuperação quando a pessoa já clicou, pagou ou informou código. |

## Confiabilidade operacional

| Controle | Status atual | Direção |
| --- | --- | --- |
| Estado próprio | Parcial | Memory/SQLite local; estado operacional n8n em memória na Fase 1. |
| Idempotência por `message_id` | Implementado em memória | TTL (1h) e limite de tamanho (100k): rejeita replay dentro da janela, aceita reenvio legítimo após expirar. Produção multi-worker exigiria Redis/DB. |
| `X-Request-ID` / `X-N8N-Execution-ID` | Parcial | Middleware aceita e ecoa os headers para rastreio local/controlado. |
| Audit log | Parcial | Event Model e audit logs locais existem; falta padronizar request/trace. |
| Versionamento de ruleset | Planejado | `RISK_ENGINE_VERSION` e `RULESET_VERSION` documentados para rastreabilidade. |
| Retry controlado / Dead letter | Planejado | n8n deve reprocessar sem duplicar decisão; mensagens falhas devem ir para fila revisável. |
| Rate limit | Parcial | In-memory e opcional em `/analyze`, `/recovery` e `/integrations/n8n/whatsapp/inbound`. |
