# Sprint 23V4 - Dual Bot Flows

## Objetivo

Esta sprint implementa os fluxos do Bot Protegido e do Bot Responsavel sobre o Event Model
e o Channel Adapter Contract.

O core nao depende de Twilio, Meta ou Mock. Ele depende de `WhatsAppChannelAdapter`.

## Bot Protegido

Fluxo:

1. Recebe payload inbound do provider.
2. Normaliza via adapter.
3. Registra mensagem e eventos pelo `ChannelIngressService`.
4. Executa risk assessment rule-based.
5. Envia resposta curta, calma e segura.
6. Cria caso quando o score atinge o threshold.
7. Quando ha caso, aciona o Bot Responsavel.

Mensagem PT com risco:

> Recebi sua mensagem. Ela tem sinais de risco. Nao faca pagamento agora. Seu responsavel foi avisado.

Mensagem PT sem caso:

> Recebi sua mensagem. Se houver pedido de dinheiro, codigo ou pressa, confirme por outro canal antes de agir.

## Bot Responsavel

Fluxo:

1. Recebe alerta com pessoa protegida, risco, sinais e caso.
2. Permite consultar contexto e historico auditavel.
3. Registra feedback:
   - `confirm_scam`
   - `false_alarm`
   - `needs_review`
   - `mark_resolved`
4. Atualiza status do caso.
5. Persiste `GuardianFeedbackReceived`.

Mensagem PT:

> Alerta Guardian: {pessoa} recebeu mensagem suspeita. Risco {risco}. Sinais: {sinais}. Caso {case_id}. Abra o caso para revisar.

## Endpoints internos

- `POST /dual-bot/mock/protected-message`
- `GET /dual-bot/cases/{case_id}/context`
- `POST /dual-bot/cases/{case_id}/feedback`

## Eventos principais

- `SuspiciousMessageReceived`
- `RiskAssessmentCreated`
- `CaseCreated`
- `GuardianAlertTriggered`
- `ProtectedPersonReplied`
- `GuardianNotified`
- `GuardianFeedbackReceived`
- `DeliveryStatusUpdated`

## Compatibilidade

O fluxo principal foi testado com `MockWhatsAppAdapter`.
`ProtectedBotService` e `ResponsibleBotService` recebem qualquer adapter que implemente
`WhatsAppChannelAdapter`, preparando uso com Twilio Sandbox sem transformar Sandbox em producao.

## Fora do escopo

- Pattern Intelligence avancado.
- Agentes avancados.
- WhatsApp producao.
- Meta Cloud API.
- UI nova.
- Persistencia fisica.
