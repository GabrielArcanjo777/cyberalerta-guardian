# Guia de demonstração — CyberAlerta Guardian

## Status atual

O README já embute uma demonstração real: [`docs/assets/demo.gif`](./assets/demo.gif) (~26s), gravada automatizando um navegador real (Playwright, gravação nativa de vídeo) contra a rota **`/assisted-demo`** rodando localmente — sem dados fabricados, sem screenshot fake. Screenshots individuais também disponíveis: [`screenshot-message.png`](./assets/screenshot-message.png), [`screenshot-analyze.png`](./assets/screenshot-analyze.png), [`screenshot-alert.png`](./assets/screenshot-alert.png), [`screenshot-console.png`](./assets/screenshot-console.png).

**Limitação conhecida desta gravação:** `/assisted-demo` é uma simulação **self-contained** do frontend (dados fixos em `components/AssistedProtectionDemo.tsx`, sem chamar o backend) — é a rota oficialmente recomendada para demo (ver `assisted-protection-demo-script.md`), mas não mostra o backend real decidindo, nem login, nem o Guardian Console autenticado com um caso persistido, nem um push chegando de fato no Android Companion. Isso continua pendente — roteiro abaixo, ainda válido para quem quiser gravar essa versão mais completa.

## Onde salvar (gravações futuras)

Nomes padronizados em `docs/assets/`:

| Arquivo | Conteúdo | Status |
| --- | --- | --- |
| `docs/assets/demo.gif` | Vídeo/GIF principal — `/assisted-demo` local | ✅ Gravado |
| `docs/assets/screenshot-message.png` / `screenshot-analyze.png` / `screenshot-alert.png` | Etapas 1–3 de `/assisted-demo` | ✅ Gravados |
| `docs/assets/screenshot-console.png` | Troca de cenário em `/assisted-demo` (não é o Guardian Console autenticado real) | ✅ Gravado, mas é uma versão simplificada |
| `docs/assets/demo-e2e.gif` ou `.mp4` | Fluxo completo com backend real: login → `/analyze` ou webhook → caso no Guardian Console autenticado → push real no Android Companion | 📋 Pendente |

## Como foi gravada a versão atual (reproduzível)

1. `cd frontend && npm run dev` (não precisa do backend — a rota é self-contained).
2. Script Playwright (Node, usa `frontend/node_modules/playwright`) abre `http://localhost:3000/assisted-demo` em `1280×800`, navega pelas 3 etapas com pausas, troca de cenário (Pix urgente → Falso banco) e grava vídeo nativo do Chromium.
3. Conversão para GIF com `ffmpeg` (paleta otimizada, 640px, 7fps, ~3MB) para ficar leve no README.

Nenhum arquivo de script foi commitado neste repositório — é um script de captura pontual, não parte da suíte de testes do projeto.

## Roteiro sugerido para a versão completa (30–60 segundos, ainda pendente)

Requer backend rodando local (`DRY_RUN=true`), login e um contato de confiança cadastrado:

1. **Mensagem suspeita** (0–8s) — texto de entrada real, ex.: *"Mãe, troquei de número, preciso de Pix urgente, não liga agora"*.
2. **Análise de risco** (8–18s) — chamada real a `POST /analyze` ou webhook, retornando score/risco.
3. **Sinais encontrados** (18–25s) — sinais explicáveis identificados (ex.: `urgency`, `pix_or_payment`, `new_number`).
4. **Criação do caso** (25–35s) — o caso aparecendo no Guardian Console **autenticado** com risco, motivo e ação recomendada.
5. **Alerta ao contato de confiança** (35–48s) — alerta simulado (`DRY_RUN=true`) chegando só ao contato de confiança. Se possível, mostrar o push chegando de fato no Android Companion (FCM real).
6. **Painel de acompanhamento** (48–60s) — o responsável revisando e confirmando/rejeitando no console.

## Cuidados ao gravar

- Use dados fictícios (ex.: "Dona Lúcia" e "Gabriel", já usados na demo) — nunca números reais.
- Rode com `DRY_RUN=true`: nenhuma mensagem real deve ser enviada durante a gravação.
- Não exponha `.env`, chaves, tokens ou IPs de rede local na tela.
- GIF com no máximo ~8 MB para não pesar o README (a versão atual tem ~3,1 MB).
