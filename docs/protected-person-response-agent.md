# Protected Person Response Agent (Sprint 18C)

Camada de resposta **curta, calma e segura** para a pessoa protegida — sem dashboard, sem jargão técnico e sem conversa com golpista.

## Objetivo

Receber nível de risco, categoria do golpe e sinais detectados e devolver:

- `short_reply` — no máximo **2 frases**, linguagem simples;
- `tone` — `calm_clear`;
- `do_not_do` — lista de ações a evitar;
- `next_step` — próximo passo seguro (ex.: aguardar contato de confiança).

## Backend

### Módulos

| Arquivo | Função |
|---------|--------|
| `response_schemas.py` | Contratos de entrada/saída |
| `response_templates.py` | Templates seguros por categoria |
| `response_policy.py` | Limite de frases e frases proibidas |
| `response_service.py` | Geração e inferência de categoria |

### Endpoint

**POST** `/protected-response/generate`

```json
{
  "risk_level": "alto",
  "category": "golpe_pix",
  "signals": ["urgencia", "numero_novo", "pedido_pix"],
  "trusted_contact_alias": "Gabriel"
}
```

Resposta:

```json
{
  "short_reply": "Não faça Pix agora. Essa mensagem tem sinais de golpe e estou avisando Gabriel.",
  "tone": "calm_clear",
  "do_not_do": ["não fazer Pix", "não clicar", "não enviar código"],
  "next_step": "aguardar contato de confiança"
}
```

## Regras de segurança

- Máximo **2 frases** por resposta.
- Tom calmo; sem culpar a pessoa protegida.
- **Nunca** orientar confrontar golpista ou responder ao contato suspeito.
- **Nunca** pedir senha, código, documento ou Pix.
- Risco alto/crítico: avisar que o contato de confiança será acionado (ou usar `trusted_contact_alias`).
- Sem alias: orientar aguardar responsável ou canal oficial.

## Categorias suportadas

- `golpe_pix`
- `link_suspeito`
- `codigo_senha`
- `falso_banco`
- `risco_baixo`
- `generico`

## Integração Sprint 18B

`POST /simple-channel/submit` chama o Protected Person Response Agent após calcular risco e sinais. O campo `simple_reply` na resposta do canal simples contém o `short_reply` gerado.

Campo opcional na entrada do canal: `trusted_contact_alias`.

## Limites do MVP

- Templates/regras — **sem LLM obrigatório**.
- **Sem envio real** de mensagens (WhatsApp mock apenas na UI).
- Sem conversa automatizada com golpista.

## Testes

```bash
cd backend
python -m pytest app/tests/test_protected_response.py -q
```

## Frontend

`/chatbot-demo` — bolhas de chat, estado “analisando…” e resposta curta do Guardian, com aviso de caso enviado ao responsável.
