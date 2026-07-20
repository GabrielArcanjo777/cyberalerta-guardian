# Documentação — CyberAlerta Guardian

Índice da documentação detalhada. O [README principal](../README.md) é a landing page do projeto; aqui ficam os detalhes.

## Guias principais

| Documento | Conteúdo |
| --- | --- |
| [`ARCHITECTURE.md`](./ARCHITECTURE.md) | Arquitetura completa (diagramas Mermaid), status real por componente, pipeline híbrido de detecção, apps Companion, deploy de referência. |
| [`LOCAL_SETUP.md`](./LOCAL_SETUP.md) | Instalação e execução local completas: pré-requisitos, backend, frontend, auth/MFA/admin, variáveis de ambiente, dataset/métricas, troubleshooting. |
| [`API.md`](./API.md) | Referência de todos os endpoints do backend, integração n8n/WhatsApp, confiabilidade operacional. |
| [`metrics_v1.md`](./metrics_v1.md) | Métricas medidas do detector determinístico contra o dataset rotulado v1 (precisão/recall/FPR, falsos positivos e negativos). |
| [`server-deployment.md`](./server-deployment.md) | Deploy do piloto num servidor Linux atrás de Cloudflare Tunnel (`compose.server.yml`). |
| [`DEMO_GUIDE.md`](./DEMO_GUIDE.md) | Como o GIF/screenshots do README foram gravados, e roteiro para a versão completa (backend real + Console autenticado) ainda pendente. |

## Segurança, privacidade e consentimento

| Documento | Conteúdo |
| --- | --- |
| [Segurança e Privacidade](../README.md#segurança-e-privacidade) (README) | Lista dos mecanismos de segurança implementados e verificados no código. |
| [`assisted-protection-privacy.md`](./assisted-protection-privacy.md) | Documento institucional de privacidade e consentimento para clientes/pilotos/avaliadores. |
| [`consent-optin-lgpd-v5.md`](./consent-optin-lgpd-v5.md) | Base operacional de consentimento e opt-in (Sprint 27V5). |

## Integrações

| Documento | Conteúdo |
| --- | --- |
| [`n8n/README.md`](./n8n/README.md) | Visão geral da integração com n8n. |
| [`n8n/whatsapp-flow.md`](./n8n/whatsapp-flow.md) | Arquitetura do fluxo WhatsApp via n8n. |
| [`n8n/real-beta-whatsapp.md`](./n8n/real-beta-whatsapp.md) | Setup do beta real de WhatsApp com n8n. |
| [`evolution-demo-adapter-setup.md`](./evolution-demo-adapter-setup.md) | Setup local do Evolution Demo Adapter (canal WhatsApp não-oficial). |
| [`channel-adapter-contract.md`](./channel-adapter-contract.md) | Contrato adapter-first de canais. |
| [`mock-whatsapp-adapter.md`](./mock-whatsapp-adapter.md) | Mock WhatsApp Adapter e simulador interno. |

## Testes e qualidade

| Documento | Conteúdo |
| --- | --- |
| [Testes](../README.md#testes) (README) | Como rodar os testes de backend, frontend e Android. |
| [`pattern-intelligence-testing.md`](./pattern-intelligence-testing.md) | Testes do Pattern Intelligence e ML realista (Sprint 25V5). |

## Limitações e roadmap

| Documento | Conteúdo |
| --- | --- |
| [Limitações atuais](../README.md#limitações-atuais) (README) | O que ainda não está pronto, de forma explícita. |
| [Roadmap](../README.md#roadmap) (README) | Próximos passos priorizados. |
| [`01-build-plan.md`](./01-build-plan.md) | Ordem histórica das sprints do plano de implementação. |

## Divulgação

| Documento | Conteúdo |
| --- | --- |
| [`GITHUB_REPOSITORY_SETUP.md`](./GITHUB_REPOSITORY_SETUP.md) | Descrição, tópicos e social preview sugeridos para o "About" do GitHub. |
| [`LINKEDIN_POST.md`](./LINKEDIN_POST.md) | Textos prontos para divulgação, roteiro de vídeo e pontos para entrevista. |

## Histórico de sprints (contexto de evolução do projeto)

Documentos escritos durante o desenvolvimento inicial (Sprints 18–27), mantidos como registro histórico das decisões de cada etapa:

`00-project-brief.md` · `assisted-proof-of-trust.md` · `assisted-protection-demo-script.md` · `controlled-agents-v5.md` · `dual-bot-flows.md` / `dual-bot-flows-v5.md` · `guardian-admin-console.md` · `protected-person-response-agent.md` · `simple-channel-intake.md` · `sprint-19v4-event-model.md` / `sprint-19v5-event-model-db-foundation.md` · `sprint-20v5-channel-adapter-contract.md` · `sprint-5-integration-validation.md` · `trusted-circle-escalation.md`
