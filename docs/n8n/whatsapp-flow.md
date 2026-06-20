# Fluxo WhatsApp via n8n

Este documento descreve o desenho recomendado dos nodes n8n para o fluxo WhatsApp MVP/demo do CyberAlerta Guardian.

O fluxo e neutro em relacao a provider. Comece com Webhook Trigger para testes locais e depois substitua por um trigger/provider oficial de WhatsApp quando houver ambiente controlado.

## Fluxo Geral

```text
Webhook Trigger ou WhatsApp Trigger
  -> Set/Edit Fields
  -> HTTP Request para CyberAlerta
  -> Switch por n8n_action
  -> Send Message para pessoa protegida
  -> Send Message para contato confiavel quando necessario
  -> Rota de Recovery quando necessario
  -> Log opcional
```

## Node 1 - Webhook Trigger ou WhatsApp Trigger

Para desenvolvimento local, use Webhook Trigger:

- Method: `POST`
- Path: `cyberalerta-whatsapp-demo`
- Response mode: `Using Respond to Webhook node` ou `Last node`, conforme seu workflow local.

Payload de teste:

```json
{
  "message_id": "demo-message-001",
  "from": "masked-demo-contact",
  "to": "cyberalerta-demo",
  "body": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
  "profile_name": "Dona Lucia"
}
```

Para pilotos com WhatsApp real, use API oficial ou provider controlado. Mantenha detalhes especificos do provider dentro do n8n e envie ao CyberAlerta somente campos normalizados.

## Node 2 - Set/Edit Fields

Normalize o payload do provider para o contrato do backend:

| Campo | Exemplo de expressao |
| --- | --- |
| `message_id` | `{{$json.message_id || $json.id || $execution.id}}` |
| `from` | `{{$json.from || "masked-demo-contact"}}` |
| `to` | `{{$json.to || "cyberalerta-demo"}}` |
| `body` | `{{$json.body || $json.message || $json.text}}` |
| `channel` | `whatsapp` |
| `user_name` | `{{$json.profile_name || "Pessoa protegida"}}` |
| `trusted_contact_name` | `Contato de confianca` |
| `trusted_contact_relation` | `contato de confianca` |
| `already_acted` | `false`, exceto quando a pessoa confirmou que ja agiu |

Nao coloque tokens, payloads completos de provider ou telefones reais em logs.

## Node 3 - HTTP Request para CyberAlerta

Request:

```text
Method: POST
URL: {{$env.CYBERALERTA_API_URL}}/integrations/n8n/whatsapp/inbound
```

Headers:

```text
Content-Type: application/json
X-N8N-CyberAlerta-Secret: {{$env.CYBERALERTA_N8N_SECRET}}
X-N8N-Execution-ID: {{$execution.id}}
```

Body: use o JSON normalizado pelo Node 2.

Campos importantes da resposta:

| Campo | Uso no n8n |
| --- | --- |
| `case_id` | Correlacionar mensagens, alertas, logs e recovery. |
| `risk_score` / `risk_level` | Mostrar contexto, nao prova final. |
| `n8n_action` | Rotear o workflow. |
| `user_message` | Mensagem para pessoa protegida quando `safe_to_send=true`. |
| `trusted_contact_should_alert` | Decidir se alerta contato confiavel. |
| `trusted_contact_message` | Mensagem para contato confiavel. |
| `recovery_should_start` | Rotear para recovery. |
| `dry_run` | Impedir envio real em modo local/demo. |

## Node 4 - Switch por `n8n_action`

Use:

```text
{{$json.n8n_action}}
```

| `n8n_action` | Acao |
| --- | --- |
| `allow_with_warning` | Enviar aviso simples. |
| `ask_for_confirmation` | Pedir pausa e confirmacao por canal confiavel. |
| `activate_trust_lock` | Enviar orientacao forte de parar. |
| `alert_trusted_contact` | Enviar resposta ao usuario e alerta ao contato confiavel. |
| `start_recovery` | Rotear para recovery. |

## Node 5 - Send Message para Usuario

Em modo demo, use Set node ou NoOp em vez de envio real.

Body da mensagem:

```text
{{$json.user_message}}
```

Checklist de seguranca:

- Enviar somente se `{{$json.safe_to_send}}` for true.
- Nunca pedir senha, codigo, token ou dados bancarios.
- Se `{{$json.dry_run}}` for true, nao chamar provider real de envio.

## Node 6 - Send Message para Contato Confiavel

Enviar somente quando:

```text
{{$json.trusted_contact_should_alert === true}}
```

Body da mensagem:

```text
{{$json.trusted_contact_message}}
```

Em testes locais, grave essa mensagem em Set node ou log seguro com destino mascarado.

## Node 7 - Recovery

Na Fase 1, `/recovery` existe e retorna orientacao estruturada. Um endpoint dedicado `/integrations/n8n/recovery` ainda nao faz parte desta etapa de documentacao.

HTTP Request sugerido quando `n8n_action` for `start_recovery`:

```text
Method: POST
URL: {{$env.CYBERALERTA_API_URL}}/recovery
Content-Type: application/json
X-N8N-Execution-ID: {{$execution.id}}
```

Body exemplo:

```json
{
  "incident_type": "pix_sent",
  "already_paid": true,
  "case_id": "{{$json.case_id}}",
  "n8n_execution_id": "{{$execution.id}}",
  "source": "n8n"
}
```

Se a resposta tiver varios itens em `whatsapp_step_messages`, envie cada passo como mensagem separada ou exiba em ordem no modo demo.

## Node 8 - Log Opcional

Registre somente campos operacionais seguros:

```json
{
  "request_id": "{{$json.request_id}}",
  "n8n_execution_id": "{{$json.n8n_execution_id}}",
  "case_id": "{{$json.case_id}}",
  "n8n_action": "{{$json.n8n_action}}",
  "risk_level": "{{$json.risk_level}}",
  "dry_run": "{{$json.dry_run}}"
}
```

Nao logue telefone completo, mensagem completa, secrets, tokens de provider ou payload bruto.

## Teste Manual com Webhook

1. Suba o backend em `http://localhost:8000`.
2. Suba o n8n em `http://localhost:5678`.
3. Crie os nodes acima.
4. Configure `CYBERALERTA_API_URL=http://localhost:8000`.
5. Configure um secret local ficticio no n8n e o mesmo valor em `N8N_WEBHOOK_SECRET` no backend.
6. Execute manualmente o Webhook Trigger.
7. Envie o payload de exemplo por curl/Postman/interface de teste do n8n.
8. Confirme que o Switch recebeu um `n8n_action` valido.

## Regra para Troca de Provider

Ao trocar Webhook Trigger por um trigger de provider WhatsApp, mantenha o payload do backend estavel. Detalhes especificos do provider ficam no n8n; o CyberAlerta recebe campos normalizados.
