# Contexto

Este arquivo responde "o que é isto e onde estão os limites". Para o detalhe técnico de cada componente, ver `ARCHITECTURE.md`.

## Problema

Golpes por engenharia social exploram pressa, medo e falsa autoridade. A vítima descobre o risco depois do Pix, do clique ou do código enviado. O sistema atua **antes** desse ponto: lê a mensagem, aponta sinais e avisa alguém de confiança — sem impedir a decisão humana.

## Escopo

**Dentro:**
- ingestão de mensagens de um número autorizado
- classificação de risco por sinais nomeados
- registro de caso, com trilha auditável
- alerta a um contato de confiança
- painel de revisão humana

**Fora:**
- bloquear ou interceptar o golpe
- responder ao remetente
- múltiplos clientes isolados (multi-tenant completo)
- uso comercial ou em terceiros sem consentimento

## Atores

| Ator | O que faz |
|---|---|
| Pessoa protegida | dona do número autorizado; consente e pode revogar |
| Contato de confiança | recebe o alerta e decide o que fazer |
| Responsável (analista) | revisa casos no painel, marca falso positivo |
| Sistema | analisa, registra, sugere — nunca decide sozinho |

## Fluxo principal

1. Número autorizado é conectado por QR code.
2. Mensagens recebidas são analisadas em silêncio.
3. Conversa normal é descartada. Mensagem suspeita vira caso com risco, motivo e ação sugerida.
4. Risco alto dispara alerta **só** ao contato de confiança (simulado por padrão).
5. O responsável revisa e fecha o caso.

## Dados

- `backend/data/scam_dataset_v1.jsonl` — 305 mensagens sintéticas, 150 golpe / 155 legítimas.
- Métricas medidas nesse dataset valem como teste de regressão, **não** como desempenho real.
- `STORE_FULL_MESSAGE=false` por padrão: guarda hash e preview curto.

## Limites conhecidos

- WhatsApp via Evolution API é integração não oficial — risco de bloqueio.
- Persistência em SQLite.
- Rate limit e idempotência em memória.
- Multi-tenant parcial.
- Sem observabilidade gerenciada.
