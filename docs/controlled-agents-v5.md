# Sprint 26V5 - Agentes Controlados

Esta sprint adiciona agentes controlados ao fluxo Guardian sem criar autonomia livre, LLM externo ou decisao irreversivel.

## Agentes criados

- `TriageAgent`: avalia a mensagem normalizada, combina Risk Engine e Pattern Intelligence, e decide se o caso deve seguir para revisao.
- `SafeReplyAgent`: gera uma resposta curta e calma para a pessoa protegida.
- `ResponsibleAlertAgent`: monta o alerta para o responsavel com risco, sinais, resumo e acao recomendada.
- `CaseSummaryAgent`: resume o caso preservando evidencias para Console e relatorio.
- `PatternReviewAgent`: organiza sinais, recorrencia e explicacao do Pattern Intelligence.

## Guardrails

- Nunca afirmar certeza absoluta.
- Usar linguagem de "sinais de risco".
- Orientar pausa e verificacao por canal confiavel.
- Nunca pedir senha, codigo ou dados bancarios.
- Nunca orientar pagamento ou clique.
- Manter revisao humana e auditabilidade.

## Eventos auditaveis

- `TriageDecisionCreated`
- `SafeReplyGenerated`
- `ResponsibleAlertGenerated`
- `CaseSummaryGenerated`
- `PatternReviewGenerated`
- `AgentFallbackUsed`

Cada decisao e publicada no Event Model com payload tipado, agente responsavel, acao recomendada e resultado dos guardrails.

## Integracao

O `DualBotFlowService` usa o `ControlledAgentOrchestrator` para chamar os agentes durante o fluxo:

1. mensagem inbound normalizada;
2. risco e padroes calculados;
3. triagem auditavel;
4. resposta segura gerada;
5. alerta ao responsavel gerado;
6. resumo do caso gerado;
7. Console exibe as decisoes dos agentes no caso ativo.

## Fora do escopo

- LLM externo.
- Agente autonomo.
- WhatsApp producao.
- Decisoes irreversiveis.
- Bloqueio automatico.
