# Sprint 19V4 - Event Model + Database Foundation

## Objetivo

Esta sprint cria a fundacao de dominio provider-neutral do CyberAlerta Guardian antes de
qualquer integracao com Twilio ou WhatsApp real.

O fluxo implementado e interno e simulado:

1. Persistir pessoa protegida, responsavel e mensagem.
2. Registrar `SuspiciousMessageReceived`.
3. Criar e persistir um `RiskAssessment` rule-based.
4. Registrar `RiskAssessmentCreated`.
5. Quando o score for maior ou igual a 40, criar um caso com status `new`.
6. Registrar `CaseCreated` e `GuardianAlertTriggered`.

`GuardianAlertTriggered` representa somente a intencao auditavel de alertar. Nenhuma
mensagem real e enviada nesta sprint.

## Entidades

- `ProtectedPerson`
- `Guardian`
- `Message`
- `RiskAssessment`
- `Case`
- `BotEvent`

## Eventos obrigatorios modelados

- `SuspiciousMessageReceived`
- `RiskAssessmentCreated`
- `CaseCreated`
- `ProtectedPersonReplied`
- `GuardianAlertTriggered`
- `GuardianNotified`
- `GuardianFeedbackReceived`
- `PatternDetected`
- `ConsentUpdated`
- `DeliveryStatusUpdated`

## Estados de caso

- `new`
- `under_review`
- `paused`
- `confirmed_scam`
- `false_alarm`
- `resolved`

## Score rule-based inicial

| Sinal | Peso |
| --- | ---: |
| Urgencia | +20 |
| Pix ou pagamento | +25 |
| Numero novo ou troquei de numero | +20 |
| Pedido para nao ligar ou nao contar | +25 |
| Link desconhecido | +20 |
| Pedido de senha ou codigo | +35 |

- Score `>= 40`: cria caso e dispara evento de alerta.
- Score `>= 70`: risco alto.

Cada sinal pontua no maximo uma vez por mensagem. O score preserva a soma dos pesos e
pode ultrapassar 100.

## Storage e caminho para banco

O storage inicial usa implementacoes in-memory atras de interfaces de repositorio para:

- pessoas protegidas;
- responsaveis;
- mensagens;
- risk assessments;
- casos;
- eventos.

O `InMemoryEventRepository` e append-only e funciona como trilha auditavel local. Uma
implementacao futura com banco deve respeitar os mesmos contratos, mantendo servicos e
eventos independentes do provider e da tecnologia de persistencia.

## Fora do escopo

- Twilio, WhatsApp real, webhooks e channel adapters.
- Bots completos e agentes.
- Pattern Intelligence avancado e ML.
- Endpoints novos e integracao com Guardian Console.
- Banco fisico, migrations e operacao de producao.
