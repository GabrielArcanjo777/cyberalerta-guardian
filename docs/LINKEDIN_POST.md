# Material para o post do LinkedIn

Três versões prontas, roteiro de vídeo e pontos para saber explicar em entrevista. Todo o texto assume que o projeto é um **MVP técnico de estudo**, não um produto pronto — evite trocar isso por linguagem de lançamento de produto.

**Evite ao editar:** "revolucionei a segurança", "acabei com os golpes", "sistema infalível", "IA que protege qualquer pessoa", "100% seguro", "pronto para produção".

---

## Versão principal

> Depois que um familiar quase caiu num golpe muito bem feito no WhatsApp — alguém se passando por autoridade, com uma história convincente e pressa artificial — comecei a construir o **CyberAlerta Guardian**: um MVP de proteção assistida contra golpes e engenharia social em mensagens.
>
> A ideia central: analisar mensagens recebidas em silêncio, identificar sinais de risco (Pix suspeito, link falso, pedido de dinheiro de "parente", código de verificação, pressão de urgência) e — só quando o risco é alto — avisar um **contato de confiança**, nunca responder ao possível golpista.
>
> Arquitetura híbrida: regras determinísticas explicáveis decidem hoje; um pipeline com LLM e Policy Engine já roda em paralelo (shadow mode) e foi validado contra um provedor real, mas ainda não tem autoridade para agir sozinho — decisão de design, não limitação escondida. Documentei esse e outros gaps abertamente no repositório.
>
> Além do backend (FastAPI) e do painel web (Next.js), já existe um app **Android Companion** (Kotlin/Compose) para o contato de confiança receber alertas por push, e uma casca **Windows Desktop** (Tauri) — ambos com build validado e testado em dispositivo/máquina real, com lacunas conhecidas e documentadas (sem assinatura de release, por exemplo).
>
> 359 testes automatizados no backend, RBAC, MFA/TOTP, auditoria, rate limiting, sanitização contra prompt injection e um dataset rotulado próprio para medir precisão/recall antes de confiar no sistema. Código público sob Elastic License 2.0.
>
> Ainda é um MVP — sem ambiente de produção, com integração WhatsApp não-oficial e multi-tenant incompleto — mas cada peça foi construída (e testada) com essa consciência. Repositório: [link]

## Versão curta

> Depois de um golpe quase bem-sucedido contra um familiar no WhatsApp, construí o **CyberAlerta Guardian**: um MVP que analisa mensagens em busca de sinais de golpe/engenharia social e alerta um contato de confiança — nunca responde ao remetente suspeito.
>
> Regras determinísticas + pipeline híbrido com LLM (shadow mode, validado com provedor real) + Policy Engine. Backend FastAPI, painel Next.js, app Android Companion e casca Windows (Tauri). 359 testes automatizados, RBAC, MFA, auditoria. Código público (Elastic License 2.0), MVP técnico — não é produto pronto para produção.
>
> Repositório: [link]

## Versão técnica

> **CyberAlerta Guardian** — MVP de detecção de engenharia social em mensagens de WhatsApp, com arquitetura híbrida:
>
> - **Camada determinística**: regras explicáveis por sinais (urgência, Pix, número novo, pressão emocional), decidem hoje se um alerta é disparado.
> - **Camada LLM + Policy Engine**: sanitização de PII e anti-prompt-injection antes de qualquer chamada externa; Policy Engine versionada decide `DISCARD`/`REVIEW`/`AUTO_ALERT`; roda em shadow mode, validada ponta a ponta contra um LLM real (OpenRouter) e uma instância Evolution/WhatsApp real — mas ainda não tem autoridade para criar caso/notificar sozinha (gap documentado, não escondido).
> - **Auth**: login local (Argon2id), MFA/TOTP, Google OIDC opcional, RBAC (`admin`/`analyst`/`viewer`/`trusted_contact`), auditoria de login/MFA.
> - **Multi-tenant (base)**: `Organization` isolando `devices`/`notifications` com teste de IDOR entre orgs; `Case`/`ProtectedPerson`/`Guardian` ainda sem esse filtro — próximo passo antes de qualquer piloto pago.
> - **Clientes nativos**: Android Companion (Kotlin/Compose, FCM push real, 17/17 testes unitários, testado em device físico) e Windows Desktop (Tauri, sem backend local, chama a API via `@tauri-apps/plugin-http` fora do CORS/CSP do navegador).
> - **Testes**: 359 automatizados no backend (pytest), 17 no Android, e2e Playwright no frontend (acesso, redirecionamento, reduced motion).
>
> Código-fonte disponível sob Elastic License 2.0 (não é permissivo no sentido estrito — a única restrição relevante é não revender como serviço hospedado).
>
> Repositório: [link]

## Hashtags sugeridas

`#cybersecurity` `#fraudprevention` `#socialengineering` `#fastapi` `#nextjs` `#kotlin` `#android` `#tauri` `#llm` `#opensource` `#buildinpublic` `#engenhariadesoftware`

## Roteiro de vídeo (30–60s)

Mesmo roteiro do [`DEMO_GUIDE.md`](./DEMO_GUIDE.md):

1. Mensagem suspeita (0–8s).
2. Análise de risco processando (8–18s).
3. Sinais de risco identificados, explicáveis (18–25s).
4. Caso criado no Guardian Console (25–35s).
5. Alerta chegando **só** no contato de confiança — nunca no remetente (35–48s), idealmente mostrando o push no Android Companion.
6. Responsável revisando o caso no painel (48–60s).

## Pontos para saber explicar em entrevista

- **Por que a LLM não decide sozinha:** LLMs alucinam e são alvo de prompt injection; decisão de enviar alerta fica com uma Policy Engine determinística e versionada — a LLM é só um insumo estruturado adicional.
- **Por que existe motor de regras determinísticas:** explicabilidade total (todo alerta tem sinais nomeados, não uma caixa-preta) e funciona mesmo sem LLM disponível — é o fallback seguro.
- **Por que existe um Policy Engine separado das regras:** ponto único e testável que combina múltiplas fontes de sinal (regras + LLM) em uma decisão auditável, sem espalhar lógica de decisão pelo código.
- **Por que o sistema nunca responde ao possível golpista:** qualquer resposta poderia confirmar ao golpista que "encontrou" um alvo ativo/vigiado, ou ser usada contra a própria vítima; o único destino de saída é o contato de confiança.
- **Por que existe um "contato de confiança" em vez de agir sozinho:** o sistema apoia decisão humana, não substitui — quem decide se é golpe de verdade é uma pessoa, com contexto que o sistema não tem.
- **Como falsos positivos/negativos são tratados:** thresholds calibrados com dataset próprio (305 mensagens rotuladas); alerta automático é deliberadamente conservador (alta precisão, recall baixo sozinho); casos de risco médio vão para uma fila de revisão humana em vez de decisão automática.
- **Por que auditoria e consentimento importam:** o sistema lê mensagens de terceiros — cada decisão precisa ser rastreável (hash de conteúdo, versão de regra/policy, latência) e o uso exige opt-in explícito, nunca monitoramento invisível.
- **Estado real do multi-tenant:** `Organization` existe e isola `devices`/`notifications` com teste de IDOR, mas `Case`/`ProtectedPerson`/`Guardian` ainda não — é o item nº1 do roadmap antes de cogitar qualquer piloto pago.
- **Por que Elastic License 2.0 e não MIT/Apache:** visão de longo prazo é open-core (núcleo aberto + eventual serviço hospedado pago); a licença permite uso/estudo/modificação livre, só impede oferecer o software como serviço hospedado a terceiros.
