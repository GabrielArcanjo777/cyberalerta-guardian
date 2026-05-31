# Verificação segura — Assisted Proof of Trust (Sprint 18F)

Protocolo para o **responsável** confirmar uma solicitação suspeita por **canal independente**, sem usar o contato suspeito. A pessoa protegida não opera checklist complexo.

## Objetivo

- Pausar decisões de alto risco (Trust Lock).
- Orientar verificação por telefone salvo, presencial ou pergunta combinada.
- Registrar decisão auditável no MVP (mock, in-memory).

## Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| POST | `/proof-trust/assisted-session` | Inicia sessão (risco alto/crítico) |
| GET | `/proof-trust/assisted-session/{session_id}` | Consulta sessão |
| POST | `/proof-trust/assisted-session/{session_id}/step` | Atualiza passo |

### Criar sessão

```json
{
  "case_id": "case-demo-001",
  "protected_person_alias": "Dona Lucia",
  "guardian_alias": "Gabriel",
  "risk_level": "alto",
  "suspected_request": "Pix urgente para falso filho",
  "trusted_contact_alias": "Gabriel"
}
```

### Atualizar passo

```json
{
  "step_id": "confirm_independent_channel",
  "status": "completed",
  "note": "Responsável confirmou pelo contato salvo que o pedido não era real."
}
```

No passo `record_decision`, incluir `final_decision`: `verified_safe` | `confirmed_scam` | `inconclusive` | `blocked`.

## Passos do protocolo

1. Não responder ao contato suspeito (auto-concluído ao iniciar).
2. Confirmar pelo contato salvo.
3. Pergunta combinada.
4. Confirmar se o pedido é real.
5. Registrar decisão.
6. Liberar somente após confirmação / manter pausa.

## Status da sessão

| Status | Significado |
|--------|-------------|
| `in_progress` | Protocolo em andamento |
| `verified_safe` | Verificado seguro — Trust Lock liberado (demo) |
| `confirmed_scam` | Golpe confirmado — pausa mantida, recovery sugerido |
| `inconclusive` | Manter pausa |
| `blocked` | Pausa protetiva mantida |

## Integração Guardian Console

- Rota: `/family-console`
- Componente: `AssistedProofSession`
- Botão: **Iniciar verificação segura**
- Conecta com **Trusted Circle** quando escalonamento simulado está ativo.

## Integração demo guiada

- `/assisted-demo` — passo 7 com `ProofOfTrustChecklist` e copy para o responsável.

## Limites do MVP

- Sem consulta a banco, governo ou validação real de CPF.
- Sem armazenamento de documentos ou telefones reais.
- Sem WhatsApp/SMS/e-mail reais.
- Armazenamento in-memory (reinício do backend limpa sessões novas).

## Privacidade

- Apenas aliases e notas curtas do responsável.
- Não usar o contato suspeito como fonte de verificação.

## Próximos passos (produto)

- Persistência e auditoria institucional.
- Integração opcional com canais oficiais (com consentimento).
- Sincronização com relatório e recovery automatizado.

## Testes

```bash
cd backend
python -m pytest app/tests/test_proof_trust.py -q
```

```bash
cd frontend
npm run build
```
