# Exemplo de Ambiente n8n

Use este arquivo como referencia segura. Nao crie nem commite um `.env` real com secrets.

## Backend `.env.example`

O backend ja possui estas variaveis relevantes:

```env
APP_ENV=development
DRY_RUN=true
N8N_ALLOWED_ORIGINS=http://localhost:5678
N8N_WEBHOOK_SECRET=
N8N_WEBHOOK_HEADER=X-N8N-CyberAlerta-Secret
N8N_BASE_URL=
N8N_DRY_RUN=true
```

Para testar localmente com webhook protegido, use um valor ficticio somente no seu ambiente local:

```env
N8N_WEBHOOK_SECRET=local-demo-secret-change-me
```

Nao commite esse valor.

## Variaveis no n8n

Configure no ambiente do n8n, docker compose local ou shell de desenvolvimento:

```env
CYBERALERTA_API_URL=http://localhost:8000
CYBERALERTA_N8N_SECRET=local-demo-secret-change-me
CYBERALERTA_DRY_RUN=true
```

O node HTTP Request deve usar:

```text
URL: {{$env.CYBERALERTA_API_URL}}/integrations/n8n/whatsapp/inbound
X-N8N-CyberAlerta-Secret: {{$env.CYBERALERTA_N8N_SECRET}}
X-N8N-Execution-ID: {{$execution.id}}
```

## Headers Obrigatorios

| Header | Valor | Observacao |
| --- | --- | --- |
| `Content-Type` | `application/json` | Necessario para parse JSON no backend. |
| `X-N8N-CyberAlerta-Secret` | `{{$env.CYBERALERTA_N8N_SECRET}}` | Necessario quando `N8N_WEBHOOK_SECRET` estiver configurado no backend. |
| `X-N8N-Execution-ID` | `{{$execution.id}}` | Usado para rastreabilidade. |

## Defaults Seguros

| Variavel | Valor local seguro | Motivo |
| --- | --- | --- |
| `DRY_RUN` | `true` | Evita acao externa acidental. |
| `N8N_DRY_RUN` | `true` | Faz o workflow tratar envio como demo/no-op. |
| `STORE_FULL_MESSAGE` | `false` | Evita armazenar texto sensivel completo. |
| `RATE_LIMIT_ENABLED` | `false` localmente, `true` quando necessario | Mantem demo simples; habilite com cuidado. |

## Nao Commitar

- Secrets reais de webhook.
- Tokens de provider WhatsApp.
- Credenciais Twilio, Meta, Evolution ou n8n.
- Numeros reais.
- Payloads brutos de usuarios reais.

## Health Checks Locais

Backend:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/integrations/n8n/health
```

n8n:

```bash
curl http://localhost:5678
```

Use o navegador para acessar o n8n quando o curl apenas confirmar que o servidor esta de pe.
