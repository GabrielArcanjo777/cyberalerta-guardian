# Sprint 20V4 - Channel Adapter Contract

## Objetivo

Esta sprint cria o contrato adapter-first para canais de WhatsApp sem acoplar o core do
produto a Twilio, Meta Cloud API ou qualquer provider especifico.

O core deve receber e produzir objetos normalizados:

- `NormalizedInboundMessage`
- `OutboundMessageRequest`
- `OutboundMessageResult`
- `DeliveryStatusEvent`

Adapters futuros traduzem payloads de provider para esses tipos. O Event Model da Sprint
19V4 continua trabalhando com mensagens, risk assessments, casos e eventos de dominio.

## Providers suportados pelo contrato

- `mock`
- `twilio_sandbox`
- `twilio_production`
- `meta_cloud_api`

Nenhum provider real foi integrado nesta sprint.

## Contrato `WhatsAppChannelAdapter`

Todo adapter deve expor:

- `provider`
- `normalize_inbound(payload)`
- `send_protected_reply(payload)`
- `send_guardian_alert(payload)`
- `parse_status_callback(payload)`

`verify_signature(request)` e opcional e pode ser detectado por `verify_signature_if_supported`.

## Idempotencia

`provider_message_id` e usado junto com `provider` para impedir duplicidade. A camada
`ChannelIngressService` registra mensagens vistas antes de enviar para o Event Model.

Se o mesmo inbound chegar duas vezes:

- a segunda ingestao retorna `duplicate=True`;
- nenhuma nova mensagem e persistida;
- nenhum novo caso e criado;
- nenhum novo evento de dominio e emitido.

## Status outbound

`InMemoryDeliveryStatusRegistry` registra o status inicial retornado por envio outbound e
atualiza o status quando um callback normalizado chega:

- `pending`
- `sent`
- `delivered`
- `failed`

Campos como `retryable` e `retry_after_seconds` deixam retry planejado sem executar retry real
nesta sprint.

## Integracao com Sprint 19V4

`ChannelIngressService` recebe qualquer `WhatsAppChannelAdapter`, normaliza o inbound e chama
`EventModelService.process_suspicious_message`.

Com isso, o core continua desacoplado:

- nao conhece payload Twilio;
- nao conhece payload Meta;
- nao conhece SDK externo;
- nao chama API real;
- trabalha apenas com dominio normalizado e eventos auditaveis.

## Fora do escopo

- Twilio Sandbox, Twilio Production e Meta Cloud API.
- Adapter mock real de produto.
- Webhooks reais, credenciais, assinatura real e envio externo.
- Bots completos, agentes e Pattern Intelligence.
- Alteracoes no frontend premium.
