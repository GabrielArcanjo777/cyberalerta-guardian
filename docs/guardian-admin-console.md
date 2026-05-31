# Guardian Admin Case Console (Sprint 18D)

Painel operacional para **responsável, familiar, cuidador ou instituição** acompanhar casos vindos do canal simples — sem expor dashboard à pessoa protegida.

## Objetivo

- Fila de casos com risco, canal, status e pausa protetiva.
- Detalhe com sinais, decisão do agente e trilha da decisão.
- Ações do responsável (status, recovery, relatório, proof — simulados no MVP).

## Fluxo

```text
Pessoa protegida → canal simples (WhatsApp mock)
                → análise Guardian + resposta curta (18C)
                → caso no Guardian Console (18D)
                → responsável age com verificação segura
```

## Backend

Módulo: `backend/app/guardian_console/`

| Endpoint | Descrição |
|----------|-----------|
| `GET /guardian-console/status` | Status do console (modo demo, contagem) |
| `GET /guardian-console/cases` | Lista casos |
| `GET /guardian-console/cases/{case_id}` | Detalhe |
| `PATCH /guardian-console/cases/{case_id}/status` | Atualiza status |
| `POST /guardian-console/cases/from-channel` | Cria caso manualmente |

### Status do caso

- `open`
- `reviewing`
- `verified_safe`
- `confirmed_scam`
- `resolved`
- `recovery_needed`

### Integração 18B/18C

`POST /simple-channel/submit` chama automaticamente a criação de caso quando `admin_case_created` é verdadeiro, usando score, categoria, sinais e `short_reply` do Protected Person Response Agent.

## Frontend

- Rota: `/family-console`
- Componente: `GuardianAdminConsole.tsx`
- Nome visual: **Guardian Console** / Painel do responsável

## Limites do MVP

- Store **in-memory** (reinício apaga casos novos; seeds demo recarregam).
- Sem login, autenticação ou banco persistente.
- Sem envio real de WhatsApp ou notificações.
- Sem dados sensíveis reais — apenas exemplos simulados.

## Testes

```bash
cd backend
python -m pytest app/tests/test_guardian_console.py -q
```

## Teste manual

```bash
curl http://localhost:8001/guardian-console/cases
curl http://localhost:8001/guardian-console/cases/case-demo-001
curl -X PATCH http://localhost:8001/guardian-console/cases/case-demo-001/status \
  -H "Content-Type: application/json" -d "{\"status\":\"reviewing\"}"
```

Abrir `http://localhost:3000/family-console`.
