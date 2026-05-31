# Trusted Circle — Escalonamento (Sprint 18E)

Fluxo simulado para acionar o **círculo de confiança** quando um caso tem risco alto ou crítico. Nenhum envio real (WhatsApp, SMS, e-mail).

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/trusted-circle/status` | Status do serviço e contagem de escalonamentos |
| POST | `/trusted-circle/escalate` | Registra escalonamento simulado |
| GET | `/trusted-circle/escalations/{escalation_id}` | Detalhe de um escalonamento |

### Exemplo — POST `/trusted-circle/escalate`

```json
{
  "case_id": "case-demo-001",
  "risk_level": "alto",
  "protected_person_alias": "Dona Lucia",
  "trusted_contacts": ["Gabriel", "Marcia"],
  "reason": "pedido de Pix urgente com identidade não verificada"
}
```

### Resposta (risco alto)

```json
{
  "escalation_id": "esc-…",
  "status": "simulated_notified",
  "message_to_guardian": "Dona Lucia recebeu uma mensagem com sinais de risco (…). Verifique antes de qualquer transferência.",
  "trusted_contacts": ["Gabriel", "Marcia"],
  "proof_of_trust_recommended": true,
  "sent_real_notification": false,
  "demo_note": "MVP: escalonamento simulado…"
}
```

## Regras de risco

| Nível | Comportamento |
|-------|----------------|
| **Baixo** | `not_escalated` — não recomenda círculo |
| **Médio** | `review_suggested` — revisão do responsável |
| **Alto / crítico** | `simulated_notified` — círculo de confiança recomendado |

- `sent_real_notification` é sempre `false`.
- Contatos são **aliases** apenas (sem telefone real).
- Mensagens curtas, em português, para o responsável.

## Integração Guardian Console

- Rota UI: `/family-console`
- Painel **Círculo de confiança** no detalhe do caso
- Botão **Acionar círculo de confiança**
- Atualiza `trusted_circle_status` no caso (`simulated_notified`, `review_suggested`, `not_required`)

## Frontend

- `TrustedCircleEscalationPanel` — console do responsável
- `TrustedCircleAlert` — alerta em `/before-pix` (tema escuro, copy PT-BR)
- Referência narrativa em `/assisted-demo` (passo 6)

## Limitações MVP

- Armazenamento in-memory; reinício do backend limpa escalonamentos novos.
- Sem autenticação, webhooks ou provedores de mensagem.
- ML/agentes de análise não são alterados por este fluxo.

## Testes

```bash
cd backend
python -m pytest app/tests/test_trusted_circle.py -q
```

```bash
cd frontend
npm run build
```
