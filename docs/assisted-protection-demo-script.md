# Roteiro — Demo de proteção assistida (Sprint 18G)

Demo principal recomendada para hackathon, clientes e portfolio. Rota: **`/assisted-demo`**.

## Mensagem de privacidade (abrir a apresentação)

> Tudo o que você verá é simulado. Não há WhatsApp real, envio automático de mensagens, login ou coleta de dados sensíveis. A pessoa protegida escolhe o que compartilhar pelo canal simples.

## Fala sugerida — 3 minutos

1. **Contexto:** “Famílias e instituições precisam agir antes do Pix, não depois do prejuízo.”
2. **Cena:** “Dona Lucia recebe uma mensagem clássica de falso familiar no WhatsApp.”
3. **Canal simples:** “Ela encaminha só o trecho suspeito — sem dashboard complexo.”
4. **Resposta curta:** “O Guardian responde com calma: não faça Pix, estou avisando o contato de confiança.”
5. **Console:** “Gabriel, o responsável, vê o caso com score, sinais e categoria no Guardian Console.”
6. **Pausa:** “Trust Lock pausa a decisão — o sistema orienta, não decide no lugar dela.”
7. **Rede:** “Trusted Circle é simulado no MVP — sem SMS real.”
8. **Verificação:** “Proof of Trust com checklist prático.”
9. **Auditoria:** “Agent Decision Trace explica cada passo.”
10. **Fechamento:** “Relatório para registro e CTAs para explorar o produto.”

## Fluxo passo a passo (tela `/assisted-demo`)

| Passo | O que mostrar | Módulo |
|-------|----------------|--------|
| 1 | Mensagem suspeita no chat mock | Canal simples (18B) |
| 2 | Encaminhamento voluntário | Privacidade / intake |
| 3 | Resposta curta do Guardian | Protected Person Response (18C) |
| 4 | Caso no painel (score, sinais) | Guardian Console (18D) |
| 5 | Trust Lock — pausa protetiva | Trust Lock |
| 6 | Trusted Circle simulado | Family / alertas |
| 7 | Proof of Trust — checklist | Verificação segura |
| 8 | Agent Decision Trace | Trace auditável |
| 9 | Preview de relatório | Report |
| 10 | CTAs | Navegação no produto |

## Limitações do MVP

- Dados in-memory e seeds demo; reinício do backend pode resetar casos novos.
- Sem autenticação, multi-tenant ou persistência real.
- Sem integração WhatsApp Business, webhooks ou notificações push.
- ML/agentes existentes não são reexecutados nesta rota — narrativa orquestrada.

## Próximos passos do produto (falar após a demo)

- WhatsApp Business com opt-in explícito.
- Notificações reais ao responsável com minimização.
- Persistência e auditoria em produção.
- Integrações bancárias e institucionais com compliance regional.

## Links úteis durante a demo

- Demo guiada: `/assisted-demo`
- Canal simples: `/chatbot-demo`
- Guardian Console: `/family-console`
- Trust Center: `/trust-center`
- Relatório: `/report`

## Dados de referência

- Pessoa protegida: Dona Lucia  
- Responsável: Gabriel  
- Mensagem: “Oi mãe, troquei de número. Preciso fazer um Pix urgente. Não liga agora.”  
- Resposta: “Não faça Pix agora. Essa mensagem tem sinais de golpe. Estou avisando seu contato de confiança.”  
- Score: 87/100 · Risco: alto · Categoria: golpe_pix  
