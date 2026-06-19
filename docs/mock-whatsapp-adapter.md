# Sprint 21V4 - Mock WhatsApp Adapter e Simulador Interno

## Objetivo

Esta sprint implementa um `MockWhatsAppAdapter` realista para testar o dominio sem Twilio,
Meta Cloud API, rede, credenciais ou templates.

O mock nao e producao. Ele simula o fluxo contratado em ambiente local:

1. Bot Protegido recebe uma mensagem suspeita simulada.
2. `MockWhatsAppAdapter` normaliza o payload pelo Channel Adapter Contract.
3. `ChannelIngressService` aplica idempotencia por `provider_message_id`.
4. `EventModelService` persiste mensagem, cria `RiskAssessment` e cria caso quando o score
   atinge o limite.
5. Quando ha caso, o simulador envia um alerta mock para o responsavel.
6. O outbound e registrado como `delivered` no registro de status simulado.
7. Eventos ficam auditaveis.

## Endpoints internos

- `GET /mock-whatsapp/fixtures`
- `POST /mock-whatsapp/simulate-inbound`
- `GET /mock-whatsapp/simulations`

## Fixtures

- `false_relative_pix`
- `suspicious_link_urgency`
- `code_password_pressure`
- `normal_message`

## Eventos esperados para mensagem suspeita com caso

- `SuspiciousMessageReceived`
- `RiskAssessmentCreated`
- `CaseCreated`
- `GuardianAlertTriggered`
- `GuardianNotified`
- `DeliveryStatusUpdated`

## Eventos esperados para mensagem normal

- `SuspiciousMessageReceived`
- `RiskAssessmentCreated`

## Fora do escopo

- Twilio, WhatsApp real e chamadas externas.
- Webhook real e assinatura real.
- UI nova.
- Agentes avancados.
- Pattern Intelligence avancado.
- Persistencia fisica.
