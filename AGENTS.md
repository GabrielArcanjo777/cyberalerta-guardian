# AGENTS.md

> Leia inteiro antes de alterar qualquer arquivo. Este projeto é um MVP pessoal, não um produto.

## Contexto

**O que é:** analisa mensagens recebidas por um número de WhatsApp autorizado, identifica sinais de golpe e alerta apenas o contato de confiança cadastrado.

**Regra cardinal:** o bot **nunca** responde ao remetente. O único destino possível de mensagem de saída é o contato de confiança, sempre atrás de um safety gate.

**Estado:** MVP técnico. Backend FastAPI, painel Next.js, app Android (Kotlin/Compose), casca Windows (Tauri). Sem produção, sem usuários em escala.

**Fora de escopo:** escalar, virar SaaS, monitorar terceiros sem consentimento explícito.

## Responsabilidades

**Pode:**
- corrigir bugs, escrever testes, refatorar módulos isolados
- atualizar documentação, testes e este arquivo
- propor mudanças de arquitetura em `demandas/`

**Não pode:**
- alterar a regra cardinal acima
- remover ou afrouxar safety gates (`DRY_RUN`, allowlist, `BETA_REAL_SEND_ENABLED`)
- habilitar envio real de mensagem em teste
- editar `.env` real ou manipular credenciais
- commitar direto na `main` sem os testes passando

**Escala para humano quando:**
- a mudança toca autenticação, PII, consentimento ou auditoria
- entra dependência nova de rede externa
- o teste falha e a causa não é óbvia

## Requisitos de entrega

Toda mudança precisa de:

- `ruff check .` e `python -m pytest app/tests -q` verdes (em `backend/`)
- `npx tsc --noEmit` e `npm run lint` verdes (em `frontend/`)
- `npx playwright test` verde se a mudança mexe no frontend
- teste novo para comportamento novo
- entrada em `docs/decisoes.md` se a mudança for estrutural
- linha em `docs/historico.md` resumindo o que mudou

O passo a passo está em `.agents/skills/verificar-projeto/SKILL.md`.

**Pronto** = código + teste + doc + CI verde.

## Human-in-the-loop

Toda ação com efeito externo — enviar mensagem, notificar, apagar dado — passa por um humano ou por um gate explícito. O agente propõe; o humano aprova.

## Onde está cada coisa

| Preciso de | Vá para |
|---|---|
| Visão geral | `README.md` |
| Como foi feito e o que foi feito com IA | `docs/como-foi-feito.md` |
| Contexto e limites | `docs/contexto.md` |
| Decisões e o porquê | `docs/decisoes.md` |
| Como rodar | `docs/LOCAL_SETUP.md` |
| Arquitetura por componente | `docs/ARCHITECTURE.md` |
| Pedidos e backlog | `demandas/` |
| Skills do agente (procedimentos reutilizáveis) | `.agents/skills/` |
| Histórico do que já foi feito | `docs/historico.md` |
| Referências externas | `docs/referencias.md` |
