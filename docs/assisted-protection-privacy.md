# Privacidade e consentimento — Proteção assistida (Sprint 18H)

Documento institucional para clientes, pilotos e avaliadores do **CyberAlerta Guardian**.

## Visão geral

O Guardian é uma plataforma de **proteção assistida** e **prevenção pré-dano**. Não é ferramenta de vigilância, não monitora conversas automaticamente e não substitui bancos, polícia, advogados ou canais oficiais.

## Fluxo assistido

1. **Pessoa protegida** — usa canal simples (chatbot / WhatsApp **mock** no MVP) e encaminha **voluntariamente** um trecho suspeito.
2. **Guardian** — calcula risco, explica sinais, responde com orientação curta e recomenda pausa (Trust Lock).
3. **Responsável** — acompanha o caso no Guardian Console, conduz Proof of Trust por canal independente e registra decisão.
4. **Círculo de confiança** — pode ser **simulado** em risco alto (sem envio real no MVP).
5. **Relatório / Recovery** — documentação e orientação; decisão humana sobre próximos passos.

## Consentimento

- A análise ocorre **somente** após encaminhamento consciente.
- Checkbox e copy de consentimento no intake e canal simples.
- Sem consentimento, não há “varredura” de mensagens ou contatos.

## Minimização de dados

- Preferir **trechos**, não conversas completas.
- **Aliases** (ex.: Dona Lucia, Gabriel) em vez de telefones reais na demo.
- Metadados reduzidos (canal, tipo de ação, nível de risco).
- Store **in-memory** no MVP — sem banco persistente de mensagens brutas.

## Redaction / mascaramento

- CPF, telefone, e-mail e chaves Pix podem ser mascarados antes da análise (intake técnico).
- Orientação explícita: **não enviar** senhas, códigos ou documentos reais na demo.

## O que o Guardian faz / não faz

Ver também o [Trust Center](/trust-center) no produto.

**Faz:** analisa conteúdo voluntário, explica risco, pausa ações perigosas, cria caso para responsável, recomenda verificação segura.

**Não faz:** monitorar WhatsApp, pedir credenciais, realizar Pix, substituir autoridades, enviar notificações reais no MVP.

## Limites do MVP

| Tópico | MVP |
|--------|-----|
| WhatsApp | Mock / visão futura com opt-in |
| Dados | Simulados e in-memory |
| Notificações | Simuladas |
| Compliance legal | Princípios de design, não certificação LGPD |
| CPF / documentos | Não coletados nem validados |

## Integração futura segura (visão)

Qualquer canal real (WhatsApp Business, e-mail, extensão) exigiria:

- Opt-in explícito e reversível  
- Escopo granular (o que pode ser enviado)  
- Termos e política por instituição  
- Minimização e retenção definidas  
- Auditoria e humano no loop  

## Linguagem para instituições

> O CyberAlerta Guardian ajuda famílias e instituições a **pausar antes do golpe**, com transparência sobre risco e próxima ação segura. Não monitoramos conversas em silêncio: a pessoa ou o responsável **escolhe** o que compartilhar. No piloto, usamos dados demonstrativos e não substituímos canais oficiais de denúncia ou recuperação financeira.

## Privacidade da pessoa protegida

- Não precisa operar dashboard complexo.  
- Recebe respostas curtas e claras no canal simples.  
- O responsável conduz verificação e decisão crítica.

## Referências no produto

- Trust Center: `/trust-center`  
- Canal simples: `/chatbot-demo`  
- Guardian Console: `/family-console`  
- Demo guiada: `/assisted-demo`  
