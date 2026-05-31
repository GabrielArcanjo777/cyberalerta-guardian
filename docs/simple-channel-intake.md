# Simple Channel Intake MVP (Sprint 18B)

Fluxo demonstrável de entrada simples por **WhatsApp mock** / chatbot, sem WhatsApp Business real, sem tokens e sem monitoramento de conversas privadas.

## Objetivo

- Pessoa protegida encaminha mensagem suspeita por canal simples.
- Guardian responde com texto curto e acionável.
- Caso simulado pode ser aberto para o responsável no console.
- Trust Lock pode ser recomendado conforme score de risco.

## Backend

### Módulos

- `backend/app/channels/simple_channel_models.py` — contratos Pydantic
- `backend/app/channels/simple_channel_service.py` — orquestração e armazenamento em memória (demo)
- `backend/app/channels/whatsapp_mock_channel.py` — validação e inferência de ação
- `backend/app/channels/protected_person_response.py` — resposta curta em PT-BR

### Endpoints

| Método | Rota | Descrição |
|--------|------|-----------|
| GET | `/simple-channel/status` | Status do canal mock e notas de privacidade |
| POST | `/simple-channel/submit` | Envia mensagem com consentimento |

### Exemplo de entrada

```json
{
  "protected_person_alias": "Dona Lucia",
  "channel": "whatsapp_mock",
  "content_type": "text",
  "content": "Mae, troquei de numero. Preciso fazer um Pix urgente.",
  "consent": true
}
```

### Exemplo de saída

```json
{
  "channel_case_id": "ch-abc123def456",
  "risk_level": "alto",
  "simple_reply": "Nao faca Pix agora. Essa mensagem tem sinais de golpe. Estou avisando seu contato de confianca.",
  "admin_case_created": true,
  "trust_lock_recommended": true
}
```

### Testes

```bash
cd backend
python -m pytest app/tests/test_simple_channel.py -q
```

## Frontend

- Rota: `/chatbot-demo`
- Componente: `frontend/components/SimpleChannelChat.tsx`
- API client: `getSimpleChannelStatus`, `postSimpleChannelSubmit` em `frontend/lib/api.ts`
- Fallback local quando o backend não responde (modo demonstração)

A rota `/intake` permanece para intake técnico completo; link para o chatbot mock no topo da página.

## Como testar manualmente

1. Subir o backend: `cd backend && uvicorn main:app --reload --port 8001`
2. Subir o frontend: `cd frontend && npm run dev`
3. Abrir `http://localhost:3000/chatbot-demo`
4. Marcar consentimento, enviar mensagem de exemplo com Pix urgente
5. Verificar resposta do Guardian, ID do caso e flags `admin_case_created` / `trust_lock_recommended`
6. Conferir `GET http://localhost:8001/simple-channel/status`

## Limitações do MVP

- Sem WhatsApp Business API real
- Sem webhooks, tokens ou envio de mensagens reais
- Casos armazenados apenas em memória (reinício do processo apaga histórico)
- Sem login ou banco persistente

## Integração futura

Substituir `whatsapp_mock_channel.py` por adaptador real com opt-in, escopos mínimos e fila de casos persistente — mantendo o mesmo contrato `/simple-channel/submit` quando possível.
