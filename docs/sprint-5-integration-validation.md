# Sprint 5 — Integração ponta a ponta (validação real)

Diferente das sprints anteriores, a Sprint 5 (Plano Mestre v1.1, Secao 8.7)
não constrói um app novo — valida o pipeline real completo (webhook →
regras → LLM → policy → persistência → push → abertura) contra
infraestrutura de verdade: Evolution/WhatsApp real pareado via Docker local
e um LLM real (OpenRouter). Todos os testes abaixo foram executados contra
o backend rodando de verdade, não lidos no código.

## 1. Infraestrutura usada

- Evolution API v2.3.7 (Docker, `docker-compose.evolution.yml`) — WhatsApp
  real pareado via QR code, instância `guardian-demo`.
- Webhook `POST /webhook/evolution` configurado com header
  `X-Evolution-Webhook-Secret` apontando pro backend local
  (`http://host.docker.internal:8000`).
- LLM: OpenRouter, `openrouter/free` (auto-router de modelos gratuitos) —
  a chave paga fornecida ficou sem crédito pro Gemini 3.5 Flash (`HTTP 402`)
  e o primeiro modelo gratuito tentado (`meta-llama/llama-3.3-70b-instruct:free`)
  bateu rate-limit compartilhado do provedor (`HTTP 429`, "temporarily
  rate-limited upstream"). O auto-router resolveu os dois problemas.
- `DRY_RUN=true`, `BETA_REAL_SEND_ENABLED=false` mantidos o tempo todo —
  nenhuma mensagem real foi enviada a ninguém durante os testes.

## 2. Checklist do plano — resultado

| Item | Resultado |
|---|---|
| Cenário golpe do falso familiar | ✅ `risk_score:65`, `high`, caso criado, alerta simulado, trace completo (`MessageReceived→...→ResponsibleNotified`), latência 455ms |
| Cenário benigno | ✅ `risk_score:0`, nenhum caso/alerta falso-positivo |
| Idempotência sob retransmissão | ✅ 2ª entrega com o mesmo `id` de mensagem → `duplicate:true`, nenhum evento/caso duplicado |
| `STORE_FULL_MESSAGE=false` não reduz análise | ✅ `message_summary`/`source_message` = `[REDACTED]` no caso, mas `risk_signals: [urgency, pix_or_payment, new_number]` extraídos corretamente |
| Remetente suspeito nunca recebe resposta | ✅ confirmado em todos os cenários — `outbound_messages` só endereça `simulated_guardian`, nunca o número do remetente |
| Divergência regra×LLM vira REVIEW, nunca DISCARD | ✅ ver Secao 3 |
| Fallback quando LLM indisponível | ✅ observado organicamente (chave sem crédito, depois rate-limit) — `LLMAnalysisFailed→PolicyFallbackUsed`, sistema não quebrou, seguiu sem LLM |
| Fallback quando Evolution indisponível | ✅ ver Secao 4 — corrigindo um falso-positivo do primeiro teste |
| Latência ponta a ponta | ✅ medida em todos os cenários: 320-455ms sem LLM, ~9.6-19.9s com LLM real na chamada síncrona |

## 3. Divergência regra×LLM — evidência real

Mensagem desenhada de propósito pra não bater nenhuma palavra-chave das
regras determinísticas (sem "pix", "urgente", "número novo" etc.) mas que é
um golpe clássico do falso familiar por contexto:

> "Oi mãe, saudações! Troquei de aparelho essa semana e configurei esse
> chip. Minha conta caiu num probleminha bobo com o banco e o RH só
> consegue depositar meu adiantamento se eu mandar um comprovante de outra
> conta hoje à noite. Você consegue passar a chave da sua conta pra eu
> usar só dessa vez? Resolvo tudo e devolvo assim que possível."

Decisão híbrida real (lida direto do evento `HybridShadowDecisionCreated`):

```json
{
  "deterministic_score": 0,
  "classification": "SCAM",
  "confidence": 0.92,
  "llm_score": 88,
  "final_score": 35,
  "action": "REVIEW",
  "reasons": [
    "conflito: regras LOW x LLM SCAM",
    "auto_alert_bloqueado: score_deterministico_baixo",
    "review: conflito entre regras e LLM"
  ],
  "scam_types": ["FAMILY_IMPERSONATION", "PIX_FRAUD", "CREDENTIAL_THEFT"],
  "conflict": true,
  "requires_human_review": true
}
```

Confirma a regra cardinal do plano: divergência forte vira sempre `REVIEW`,
nunca `DISCARD` automático.

**Achado — essa decisão não é visível pra ninguém hoje.** O motor de regras
determinísticas (legado) decide sozinho se um caso é criado (`score>=40`) e
se o responsável é notificado (só `risk_level=HIGH`). A camada híbrida roda
em paralelo e grava a decisão corretamente, mas **não tem efeito
operacional** — só descobri o conteúdo acima lendo o evento direto do
banco via script Python, não existe endpoint/tela que mostre uma decisão
híbrida sem `case_id`, e essa mensagem não gerou `case_id` nenhum. Fechar
esse fio (hybrid decision → visibilidade real pra um humano revisar) é
trabalho de Sprint 6 (hardening), não implementado nesta sessão por ser uma
mudança de comportamento do pipeline de produção que merece revisão
própria, não um ajuste apressado.

## 4. Fallback Evolution indisponível — dois testes, um corrigido

**1º teste (impreciso):** mensagem de risco médio (score 55, "cartão
perdido + código") com Evolution parado → `guardian_notified:false`.
Inicialmente atribuído à queda do Evolution.

**2º teste (isolado corretamente):** mesma mensagem do cenário 1
(garantidamente `HIGH`, score 65-90) com o container `cyberalerta-evolution`
totalmente parado (`docker compose stop`) → `case_created:true`,
**`guardian_notified:true`**, alerta simulado entregue normalmente.

**Conclusão correta:** o gate real é `risk_level`, não a disponibilidade do
Evolution. Em `DRY_RUN=true` (padrão de segurança do projeto), o envio do
alerta é inteiramente simulado no backend e nunca depende de uma chamada
real à API do Evolution — a resiliência a essa falha específica já vem de
graça do próprio modo dry-run. Só risco `MEDIUM` fica sem notificação
automática (comportamento intencional documentado no código,
`evolution_demo/service.py`: alerta automático só dispara em `HIGH`).

## 5. Cobertura de golpes adicionada nesta sessão

O Gabriel pediu proteção explícita contra golpes de INSS/benefício e
ameaça judicial falsa (mandado de prisão, processo judicial) — comuns
contra idosos e sem nenhuma cobertura antes desta sessão (nem regra
determinística, nem tipo de golpe reconhecido pela LLM).

- `ScamType.GOVERNMENT_BENEFIT_SCAM` e `ScamType.FAKE_LEGAL_THREAT`
  adicionados (`app/llm/models.py`) — fluem automaticamente pro prompt da
  LLM (schema gerado dinamicamente a partir do enum).
- Duas `RiskRule` novas no motor determinístico (`government_benefit_threat`,
  `fake_legal_threat`, peso 25 cada) — funcionam mesmo sem LLM configurado.
- Ambas entram no grupo de "personificação institucional" do Policy Engine
  (mesmo grupo de banco/suporte técnico), afetando `has_impersonation` e as
  combinações de auto-alerta.
- 3 testes novos (`test_hybrid_deterministic.py`,
  `test_hybrid_policy.py`) + validado ao vivo via webhook real:
  - INSS: `risk_score:70`, `high`, caso criado, alerta notificado.
  - Ameaça judicial: `risk_score:45`, `medium`, caso criado (sem
    auto-notificação, mesmo gate do item 4).
- Suíte completa: **359/359 testes verdes** depois da mudança.

## 6. Pendências pra Sprint 6 (hardening)

- Conectar a decisão híbrida (`REVIEW`/`AUTO_ALERT`) à visibilidade real
  pro operador — hoje é só uma gravação de auditoria sem consumidor.
- Worker de retry pra alertas que falharem de verdade fora do dry-run
  (Redis/Celery, já mapeado como pendência P0 do plano).
- Repetir esses mesmos cenários com `DRY_RUN=false` +
  `BETA_REAL_SEND_ENABLED=true` num beta controlado — não feito aqui de
  propósito, envolve enviar mensagens reais.
