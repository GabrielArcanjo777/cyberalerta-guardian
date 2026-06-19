# CyberAlerta Guardian

**Slogan:** Antes do Pix. Antes do clique. Antes do prejuízo.

CyberAlerta Guardian é um MVP técnico para intervenção pré-dano em golpes digitais. O projeto foca em detectar sinais de engenharia social, fraudes por Pix, mensagens de falso familiar e links suspeitos antes que a vítima execute uma ação de risco.

A proposta de valor é oferecer uma demonstração de fluxo assistido de análise e mitigação para casos de fraude, com decisão assistida por agentes, contêineres de confiança e simulações de canais.

Status: MVP / demo técnica em desenvolvimento. O projeto não é um produto de produção, mas mostra a arquitetura e os componentes principais de um protótipo de segurança digital.

## O que o projeto faz

- Analisa mensagens suspeitas e sinaliza risco em tempo real.
- Detecta sinais de manipulação e engenharia social.
- Calcula um score de risco e classifica o tipo de golpe.
- Identifica estágio do golpe e ações perigosas.
- Ativa um mecanismo de Trust Lock quando o risco é crítico.
- Recomenda etapas de Proof of Trust para verificação segura.
- Permite escalonamento para um contato confiável (trusted circle).
- Gera relatório estruturado com evidências e recomendações.
- Suporta persistência em memória ou SQLite para dados de sessão e casos.
- Possui um fluxo de demonstração assistida em frontend.

## Arquitetura

```text
Frontend Next.js/TypeScript
        |
        v
Backend FastAPI/Python
        |
        v
Agents + Services
        |
        v
Mock channels / Console / Consent / Recovery
```

- `frontend/`: interface de usuário, páginas de demo e fluxo assistido.
- `backend/main.py`: ponto de entrada da API FastAPI.
- `backend/app/agents/`: agentes de decisão e análise de fraude.
- `backend/app/services/`: serviços auxiliares para segurança, mock channels e orquestração.
- `backend/app/schemas/`: contratos Pydantic para requisições e respostas.
- `docs/`: documentação de sprint, roteiro de demo e especificações de arquitetura.

## Stack

- Python
- FastAPI
- Pydantic
- Uvicorn
- Pytest
- Next.js
- TypeScript
- Tailwind CSS
- Node.js / npm

## Executando localmente

### Backend

```bash
cd backend
python -m venv .venv
# Windows:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

pip install -r requirements.txt
uvicorn main:app --reload
```

O backend ficará disponível em `http://localhost:8000`.

### Frontend

```bash
cd frontend
npm install
npm run dev
```

A rota recomendada da demo é:

```text
http://localhost:3000/assisted-demo
```

A documentação interativa do FastAPI está em:

```text
http://localhost:8000/docs
```

## Variáveis de ambiente

Use `.env.example` como base para suas configurações locais. Nunca commit um arquivo `.env` com credenciais reais.

- `NEXT_PUBLIC_API_URL`: URL do backend, normalmente `http://localhost:8000`.
- `USE_LLM`: modo de modelo de linguagem (`false` para mocks / demo local).
- `LLM_PROVIDER`: provider de LLM (`mock` por padrão no MVP).
- `CHANNEL_PROVIDER`: provedor de canal ativo no backend.
- `DUAL_BOT_CHANNEL_PROVIDER`: provedor de canal do dual bot.
- `STORAGE_BACKEND`: backend de persistência do backend (`memory` ou `sqlite`).
- `SQLITE_DATABASE_URL`: URL de conexão SQLite, por exemplo `sqlite:///./cyberalerta_guardian.db`.
- `TWILIO_*`: variáveis de sandbox Twilio / WhatsApp em modo de teste.
- `EVOLUTION_*`: variáveis de integração Evolution demo.
- `APP_ENV`: ambiente da aplicação (`development` ou `production`).
- `API_KEY_ENABLED`: habilita proteção por API key para endpoints sensíveis (`false` no local).
- `API_KEY_HEADER`: header esperado para a chave de API.
- `CYBERALERTA_API_KEY`: chave de API usada quando `API_KEY_ENABLED=true`.
- `ALLOWED_ORIGINS`: origens permitidas para CORS, separadas por vírgula.
- `TRUSTED_WEBHOOK_IPS`: IPs confiáveis para webhooks (opcional).
- `MAX_MESSAGE_LENGTH`: tamanho máximo do texto analisado.
- `EVOLUTION_WEBHOOK_SECRET`: segredo opcional para o webhook de Evolution.

Integrações reais podem estar mockadas no MVP. Não use tokens, telefones reais ou chaves secretas em um repositório público.

### Usando API key opcional

Para proteger endpoints sensíveis em homologação ou produção, configure:

```env
API_KEY_ENABLED=true
API_KEY_HEADER=X-CyberAlerta-API-Key
CYBERALERTA_API_KEY=um-segredo-forte
```

Exemplo de chamada com cabeçalho:

```bash
curl -H "X-CyberAlerta-API-Key: um-segredo-forte" http://localhost:8000/guardian-console/status
```

Em `development`, deixe `API_KEY_ENABLED=false` para não bloquear o demo local.

## Endpoints principais

| Método | Endpoint | Finalidade | Status |
|---|---|---|---|
| GET | `/health` | Verifica se o backend está ativo | real |
| GET | `/examples` | Retorna cenários de golpe de exemplo | real |
| POST | `/analyze` | Analisa mensagem suspeita e retorna decisão | real |
| POST | `/recovery` | Gera checklist de recuperação condicional | real |
| POST | `/report` | Recebe análise e retorna relatório resumido | real |
| GET | `/simple-channel/status` | Status do canal simples de demo | demo |
| POST | `/simple-channel/submit` | Envia mensagem ao canal simples | demo |
| GET | `/mock-whatsapp/fixtures` | Lista fixtures do mock WhatsApp | mock |
| POST | `/mock-whatsapp/simulate-inbound` | Simula mensagem de entrada no WhatsApp | mock |
| GET | `/mock-whatsapp/simulations` | Consulta simulações de mensagens | mock |
| POST | `/dual-bot/mock/protected-message` | Envia mensagem para fluxo mock Dual Bot | mock |
| GET | `/dual-bot/status` | Status do provedor Dual Bot | demo |
| POST | `/dual-bot/provider/protected-message` | Recebe mensagem de provedor Dual Bot | demo |
| GET | `/dual-bot/cases/{case_id}/context` | Contexto de caso Dual Bot | demo |
| POST | `/dual-bot/cases/{case_id}/feedback` | Envia feedback de caso Dual Bot | demo |
| GET | `/consent/status` | Status de consentimento | real |
| POST | `/consent/accept` | Aceita consentimento do usuário | real |
| POST | `/consent/revoke` | Revoga consentimento | real |
| POST | `/consent/bot/activate` | Ativa bot de consentimento | real |
| POST | `/consent/bot/deactivate` | Desativa bot de consentimento | real |
| POST | `/consent/scopes` | Atualiza escopos de consentimento | real |
| GET | `/guardian-console/real/status` | Status do Guardian Console real | demo |
| GET | `/guardian-console/real/cases` | Lista de casos do Guardian Console real | demo |
| GET | `/guardian-console/real/cases/{case_id}` | Detalhe de caso no Guardian Console real | demo |
| POST | `/guardian-console/real/cases/{case_id}/feedback` | Feedback de caso no Guardian Console real | demo |
| GET | `/guardian-console/status` | Status do console de administração | demo |
| GET | `/guardian-console/cases` | Lista casos do console de administração | demo |
| GET | `/guardian-console/cases/{case_id}` | Detalhe de caso administrativo | demo |
| POST | `/guardian-console/cases/from-channel` | Cria caso a partir de canal | demo |
| GET | `/trusted-circle/status` | Status do Trusted Circle | demo |
| POST | `/trusted-circle/escalate` | Escala para contato confiável | demo |
| GET | `/trusted-circle/escalations/{escalation_id}` | Consulta registro de escalamento | demo |
| POST | `/proof-trust/assisted-session` | Cria sessão de Proof of Trust | demo |
| GET | `/proof-trust/assisted-session/{session_id}` | Consulta sessão de Proof of Trust | demo |
| POST | `/proof-trust/assisted-session/{session_id}/step` | Avança etapa de Proof of Trust | demo |
| GET | `/api/channels/twilio/whatsapp/health` | Health do Twilio sandbox | mock |
| POST | `/api/channels/twilio/whatsapp/inbound` | Webhook inbound do Twilio sandbox | mock |
| POST | `/api/channels/twilio/whatsapp/status` | Callback de status Twilio sandbox | mock |
| GET | `/webhook/evolution/health` | Health do Evolution demo | mock |
| POST | `/webhook/evolution` | Webhook de Evolution demo | mock |
| POST | `/protected-response/generate` | Gera resposta protegida para usuário | demo |

## Exemplo de payload para `/analyze`

Payload de requisição compatível com o schema `AnalysisRequest`:

```json
{
  "user_name": "Maria",
  "age_group": "adult",
  "trusted_contact_name": "João",
  "trusted_contact_relation": "filho",
  "action_type": "pix",
  "channel": "whatsapp",
  "message": "Mãe, troquei de número. Preciso de um Pix urgente agora.",
  "already_acted": false
}
```

Exemplo de resposta resumida esperada:

```json
{
  "risk_score": 78,
  "risk_level": "alto",
  "dangerous_action": "enviar_pix",
  "scam_type": "falso familiar",
  "trust_lock": {
    "activated": true,
    "title": "Trust Lock ativado",
    "reason": "mensagem com urgência e familiaridade suspeita",
    "message": "Recomendado não enviar Pix antes de verificar a identidade."
  },
  "proof_of_trust": [
    "Verifique o número do contato",
    "Confirme código de segurança com familiar"
  ]
}
```

## Limitações atuais

- O MVP usa regras, heurísticas e sinais textuais para análise.
- Não há garantia de detecção de todos os golpes.
- A persistência pode estar em memória ou em implementações temporárias.
- Integrações externas podem estar mockadas ou em sandbox.
- Não substitui orientação jurídica, bancária ou policial.
- O sistema está em fase de protótipo / demo técnica.

## Roadmap técnico

- [x] Documentação do projeto e roteiro de demo
- [ ] Segurança mínima e validação de entrada
- [ ] Persistência de dados confiável
- [ ] Testes automatizados mais robustos
- [ ] Observabilidade e logging centralizado
- [ ] Integrações com canais reais de mensagem
- [ ] Melhoria do motor de risco e classificação
- [ ] Deploy e entrega do MVP

## Por que este projeto é relevante

Fraudes por Pix e engenharia social são ameaças reais para pessoas vulneráveis. Este projeto demonstra como uma arquitetura de decisão assistida pode produzir avisos e recomendações antes que a vítima realize um pagamento perigoso.

O foco em explicabilidade, fluxo pré-dano e contato confiável torna o MVP apropriado para portfólio técnico, especialmente em contextos de cibersegurança, produto responsável e intervenções emergenciais.

## Repositório e contribuições

- A documentação de cada sprint está em `docs/`.
- O backend e a lógica do agente estão em `backend/`.
- O frontend de demonstração está em `frontend/`.
- Contribuições devem preservar o fluxo atual e não alterar a interface pública sem validação.
