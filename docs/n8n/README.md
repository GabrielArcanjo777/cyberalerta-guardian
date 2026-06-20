# n8n Workflow - CyberAlerta Guardian

Esta pasta documenta como montar um workflow local/controlado no n8n para o CyberAlerta Guardian.

A fronteira do produto e simples:

```text
n8n orquestra canais. CyberAlerta decide risco e acao.
```

O n8n recebe um evento parecido com WhatsApp, normaliza os campos minimos, chama o backend do CyberAlerta e roteia a decisao para resposta, alerta ao contato confiavel, recovery ou log.

## Status

Esta e documentacao de MVP/demo, nao documentacao de WhatsApp em producao.

- O endpoint backend documentado e `POST /integrations/n8n/whatsapp/inbound`.
- O backend local usa por padrao `http://localhost:8000`.
- O fluxo pode ser testado sem WhatsApp real usando Webhook Trigger no n8n.
- WhatsApp real deve usar API oficial ou provider controlado. Nao apresente WhatsApp pessoal por QR Code como solucao principal.
- Mantenha `DRY_RUN=true` e `N8N_DRY_RUN=true` em demos e desenvolvimento.

## Arquivos

| Arquivo | Objetivo |
| --- | --- |
| `README.md` | Visao geral, fronteiras e teste rapido. |
| `whatsapp-flow.md` | Desenho passo a passo dos nodes no n8n. |
| `env-example.md` | Exemplos seguros de variaveis de ambiente. |
| `workflow-pseudo-json.json` | Esqueleto conceitual do workflow sem credenciais. |
| `troubleshooting.md` | Erros comuns e checklist de debug. |

## Contrato do Backend

### Health

```http
GET http://localhost:8000/integrations/n8n/health
```

### WhatsApp Inbound

```http
POST http://localhost:8000/integrations/n8n/whatsapp/inbound
Content-Type: application/json
X-N8N-CyberAlerta-Secret: {{$env.CYBERALERTA_N8N_SECRET}}
X-N8N-Execution-ID: {{$execution.id}}
```

Body minimo:

```json
{
  "message_id": "demo-message-001",
  "from": "masked-or-demo-contact",
  "to": "cyberalerta-demo",
  "body": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
  "channel": "whatsapp",
  "user_name": "Dona Lucia",
  "trusted_contact_name": "Gabriel",
  "trusted_contact_relation": "filho",
  "already_acted": false
}
```

Formato esperado da resposta:

```json
{
  "status": "processed",
  "request_id": "req-demo",
  "n8n_execution_id": "exec-demo",
  "case_id": "n8n-case-demo",
  "risk_score": 95,
  "risk_level": "critical",
  "n8n_action": "alert_trusted_contact",
  "user_message": "Mensagem curta e segura para a pessoa protegida.",
  "trusted_contact_should_alert": true,
  "trusted_contact_message": "Mensagem curta para contato de confianca.",
  "recovery_should_start": false,
  "report_summary": "Resumo operacional do caso.",
  "safe_to_send": true,
  "dry_run": true
}
```

## Acoes n8n

| `n8n_action` | Acao no n8n |
| --- | --- |
| `allow_with_warning` | Enviar aviso simples. |
| `ask_for_confirmation` | Pedir pausa e confirmacao por canal confiavel. |
| `activate_trust_lock` | Enviar orientacao forte de parar/pausar. |
| `alert_trusted_contact` | Responder usuario e alertar contato confiavel. |
| `start_recovery` | Chamar ou rotear para recovery. |

## Teste Manual Sem WhatsApp

1. Suba o backend localmente.
2. No n8n, crie um Webhook Trigger com metodo `POST`.
3. Adicione um node Set/Edit Fields para mapear um payload demo para o contrato do CyberAlerta.
4. Adicione um HTTP Request apontando para `/integrations/n8n/whatsapp/inbound`.
5. Adicione um Switch em `{{$json.n8n_action}}`.
6. Para cada rota, use um node fake de envio ou um Set node enquanto `DRY_RUN=true`.
7. Confirme que a resposta do backend inclui `X-Request-ID` e, quando enviado, `X-N8N-Execution-ID`.

## Regras de Seguranca

- Nao commitar tokens, secrets, numeros reais, API keys ou payloads reais.
- Nao logar telefone completo nem mensagem completa.
- Usar valores falsos como `masked-demo-contact`.
- Usar o backend como fonte de decisao. O n8n nao decide se e golpe.
- Manter exemplos e testes locais com `DRY_RUN=true`.

## Docs Relacionadas

- [Fluxo WhatsApp](./whatsapp-flow.md)
- [Exemplos de ambiente](./env-example.md)
- [Pseudo JSON do workflow](./workflow-pseudo-json.json)
- [Troubleshooting](./troubleshooting.md)
- [Templates de mensagem](../n8n-whatsapp-message-templates.md)
