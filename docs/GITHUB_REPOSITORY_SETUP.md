# Configuração manual do repositório no GitHub

Estas ações não podem ser feitas via Git — precisam ser aplicadas manualmente em `Settings` / na página do repositório.

## Descrição sugerida (campo "About")

Máximo ~160 caracteres:

```text
MVP de proteção assistida contra golpes no WhatsApp: regras + LLM + Policy Engine, alerta a um contato de confiança. FastAPI, Next.js, Android, Tauri.
```

Alternativa mais curta:

```text
Detecção de golpes no WhatsApp com alerta ao contato de confiança — backend FastAPI + apps Android/Windows companion (MVP, open-core).
```

## Website

Não há URL pública de demo hospedada hoje. Deixe o campo em branco até existir um ambiente de piloto real — não invente uma URL.

## Tópicos sugeridos

Escolha os que fazem sentido no momento (todos abaixo representam algo real do repositório):

`cybersecurity` `anti-fraud` `social-engineering` `whatsapp` `fastapi` `nextjs` `kotlin` `tauri` `llm` `fraud-detection` `family-safety` `open-core`

## Social preview (imagem de compartilhamento)

Duas opções reais, sem imagem fabricada:

1. `frontend/public/cyberalerta-guardian-logo-banner.png` (2117×743px, fundo escuro) — mais "institucional".
2. `docs/assets/screenshot-analyze.png` (1280×800px, tela de análise do Guardian) — mostra o produto funcionando, geralmente converte melhor num feed do LinkedIn.

GitHub aceita PNG/JPG até 1MB para social preview, recomendado próximo de 1280×640 — pode ser necessário recortar/redimensionar a opção 2 antes de subir em `Settings → General → Social preview`.

## Licença exibida pelo GitHub

O arquivo `LICENSE` na raiz (Elastic License 2.0) já é reconhecido automaticamente pelo GitHub e aparece na barra lateral do repositório — nenhuma ação manual necessária além de confirmar que aparece como "Elastic-2.0" após o próximo push.

## Branch padrão e proteção (opcional, avaliar)

`main` é a branch padrão. Se quiser exigir CI verde antes de merge no futuro (`Settings → Branches → Branch protection rules`), o workflow relevante é `CI` (`.github/workflows/ci.yml`, jobs `Backend (pytest)` e `Frontend (typecheck + lint)`).
