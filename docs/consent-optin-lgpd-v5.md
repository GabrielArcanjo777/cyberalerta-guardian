# Sprint 27V5 - Consentimento, Opt-in e LGPD

Esta sprint cria a base operacional de consentimento para o Guardian, sem juridico avancado e sem WhatsApp producao.

## Entidades

- `ConsentRecord`: registro de opt-in da pessoa protegida/responsavel.
- `OptInStatus`: `pending`, `active`, `revoked`, `bot_disabled`.
- `ConsentScope`: escopos autorizados para bot protegido, alertas, analise de padroes, historico e canal demo.
- `ConsentEvent`: evento local de aceite, revogacao, ativacao, desativacao ou mudanca de escopo.
- `DataRetentionPolicy`: politica basica de retencao local.

## Eventos no Event Model

- `ConsentAccepted`
- `ConsentRevoked`
- `BotActivated`
- `BotDeactivated`
- `ConsentScopeChanged`

Os eventos sao publicados pelo `ConsentService` no Event Model e geram audit log local.

## Endpoints

- `GET /consent/status`
- `POST /consent/accept`
- `POST /consent/revoke`
- `POST /consent/bot/activate`
- `POST /consent/bot/deactivate`
- `POST /consent/scopes`

## Guardian Console

O Console mostra:

- status de opt-in;
- bot ativo/inativo;
- escopos autorizados;
- janela de retencao;
- aviso de limitacao;
- acoes de aceitar opt-in, reativar, desativar e revogar.

Quando `ConsentService` esta conectado ao Console, o estado de ativacao dos bots reflete `bot_active`.

## Fora do escopo

- WhatsApp producao.
- Meta Cloud API.
- automacao juridica avancada.
- apagamento fisico real de banco.
- DPO/legal workflow completo.
- billing ou contrato comercial.
