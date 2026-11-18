# Decisões

Registro curto do que foi decidido e por quê. Ordem cronológica. Não reescreva uma decisão antiga: adicione uma nova que a substitua.

---

## ADR-001 — O bot nunca responde ao remetente

**Decisão:** nenhuma mensagem de saída vai para quem enviou. O único destino possível é o contato de confiança.

**Por quê:** responder confirma que o número está sendo monitorado e pode ser usado contra a própria vítima.

**Consequência:** todo caminho de envio precisa validar o destinatário contra o cadastro, não contra a origem.

---

## ADR-002 — Regras determinísticas decidem; LLM sugere

**Decisão:** quem cria caso e dispara alerta é o motor de regras. A LLM produz insumo estruturado e não aciona nada.

**Por quê:** LLM alucina e é alvo de prompt injection. Um alerta falso destrói a confiança; um alerta perdido é pior ainda.

**Consequência:** existe `PolicyEngine` separado, versionado, que combina regras + LLM numa decisão auditável (`DISCARD` / `REVIEW` / `AUTO_ALERT`).

---

## ADR-003 — Explicabilidade total nos alertas

**Decisão:** todo alerta cita sinais nomeados. Não existe score sem motivo.

**Por quê:** a pessoa protegida precisa entender por que aquilo foi sinalizado, ou ignora o aviso.

---

## ADR-004 — Contato de confiança em vez de ação automática

**Decisão:** o sistema avisa uma pessoa e ela decide.

**Por quê:** o contexto que falta ao sistema está com quem conhece a vítima.

---

## ADR-005 — Nada de envio real por padrão

**Decisão:** `DRY_RUN=true`, allowlist re-pinada e `BETA_REAL_SEND_ENABLED` obrigatório para envio real.

**Por quê:** um teste mal configurado não pode mandar mensagem para número real.

**Consequência:** qualquer PR que afrouxe isso precisa de aprovação humana explícita.

---

## ADR-006 — Auditoria e consentimento como requisito, não feature

**Decisão:** o sistema lê mensagens de terceiros. Toda decisão é rastreável e o uso exige opt-in explícito.

**Por quê:** sem trilha e sem consentimento, o produto é ilegal no Brasil (LGPD), independente de funcionar.

---

## ADR-007 — Métrica de dataset sintético não é métrica de produção

**Decisão:** números de precisão/recall só valem contra o dataset interno e são publicados como regressão.

**Por quê:** o dataset foi gerado, não coletado. Serviria para enganar quem lê rápido.

---

## Em aberto

- Migrar de Evolution API (não oficial) para WhatsApp Cloud API (Meta).
- Persistência: SQLite → Postgres com migrações.
- Rate limit e idempotência: memória → Redis.
- Observabilidade: logging estruturado + tracing.
