# Troubleshooting n8n

Use este guia quando o workflow n8n nao chamar o CyberAlerta corretamente.

## 401 Unauthorized

Causa provavel: o backend tem `N8N_WEBHOOK_SECRET` configurado, mas o n8n nao enviou o header esperado.

Verifique:

- Backend env: `N8N_WEBHOOK_SECRET=local-demo-secret-change-me`
- Backend env: `N8N_WEBHOOK_HEADER=X-N8N-CyberAlerta-Secret`
- Header no HTTP Request do n8n:

```text
X-N8N-CyberAlerta-Secret: {{$env.CYBERALERTA_N8N_SECRET}}
```

Se estiver testando sem secret em desenvolvimento local, deixe `N8N_WEBHOOK_SECRET` vazio no backend. Nao use essa configuracao em ambiente compartilhado ou exposto.

## 403 Forbidden

Causa provavel: o n8n enviou o header, mas o valor nao bate com `N8N_WEBHOOK_SECRET`.

Como corrigir:

1. Troque para um secret local ficticio.
2. Coloque o mesmo valor no backend e no n8n.
3. Reinicie os dois processos.
4. Tente novamente com nova execucao.

Nao cole secrets reais em prints, logs, issues ou docs.

## Backend Offline

Sintomas:

- HTTP Request do n8n retorna connection refused.
- n8n nao consegue acessar `localhost`.
- `/health` nao responde.

Verifique:

```bash
curl http://localhost:8000/health
curl http://localhost:8000/integrations/n8n/health
```

Se o n8n estiver em Docker, `localhost` dentro do container pode nao apontar para sua maquina host. Use o host gateway ou uma URL de rede local adequada ao seu setup.

## Payload sem Mensagem

Sintomas:

- Backend retorna `422`.
- Resposta menciona ausencia de `message`, `body` ou `text`.

O endpoint inbound aceita aliases:

- `message`
- `body`
- `text`

O node Set/Edit Fields deve sempre produzir:

```json
{
  "body": "Texto da mensagem recebida"
}
```

Nao envie payload bruto de provider sem normalizacao.

## Execucao ou Mensagem Duplicada

Sintomas:

- n8n tenta reexecutar workflow.
- Backend retorna a mesma resposta para o mesmo `message_id`.
- Logs mencionam `duplicate_message_ignored`.

Isso e esperado. O CyberAlerta usa `message_id` para idempotencia basica no MVP local.

Regras:

- Mantenha `message_id` estavel para a mesma mensagem do provider.
- Nao gere novo `message_id` em retry.
- Se precisar de nova decisao, use novo message id e preserve o caso antigo para auditoria.

## Duvida com DRY_RUN

Sintomas:

- O backend retorna decisao, mas nenhuma mensagem real de WhatsApp e enviada.
- O n8n roteia para um node demo/no-op.

Isso e esperado quando:

```env
DRY_RUN=true
N8N_DRY_RUN=true
CYBERALERTA_DRY_RUN=true
```

Para demos MVP, mantenha dry run ligado. Troque Set nodes demo por nodes reais de envio somente em ambiente controlado de provider.

## Logs e Trace IDs

Toda resposta do backend deve incluir:

```text
X-Request-ID
```

Chamadas do n8n devem incluir:

```text
X-N8N-Execution-ID: {{$execution.id}}
```

Use esses campos para correlacionar:

- tela de execucao do n8n;
- logs do backend;
- campos `request_id` e `n8n_execution_id` no body de resposta;
- `case_id` retornado pelo CyberAlerta.

Campos seguros para log:

```json
{
  "request_id": "req-demo",
  "n8n_execution_id": "exec-demo",
  "case_id": "n8n-case-demo",
  "n8n_action": "alert_trusted_contact",
  "risk_level": "critical",
  "dry_run": true
}
```

Nao logue telefone completo, texto completo da mensagem, tokens de provider, webhook secrets, authorization headers ou payload bruto.

## Switch Caiu na Rota Errada

Confira exatamente o valor de:

```text
{{$json.n8n_action}}
```

Valores suportados:

- `allow_with_warning`
- `ask_for_confirmation`
- `activate_trust_lock`
- `alert_trusted_contact`
- `start_recovery`

Se o valor estiver vazio, inspecione a saida do HTTP Request. Ele pode estar retornando erro em vez da decisao do backend.

## Recovery Retorna Varias Mensagens

A resposta de `/recovery` pode incluir `whatsapp_step_messages`.

No n8n, voce pode:

- enviar cada item como uma mensagem separada em ambiente controlado; ou
- exibir/salvar como saida demo enquanto `DRY_RUN=true`.

Nao comprima instrucoes de recovery em uma mensagem longa demais para o usuario seguir.

## Lembrete de Producao

Este workflow e um guia de demo/control-plane. WhatsApp em producao exige API oficial ou provider controlado, consentimento, revisao de privacidade, rate limits, retencao de auditoria e monitoramento operacional.
