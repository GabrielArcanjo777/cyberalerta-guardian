# Dados

Os dados deste projeto ficam fora desta pasta, junto do código que os consome.

| Caminho | O que é | Gerado por |
|---|---|---|
| `backend/data/scam_dataset_v1.jsonl` | 305 mensagens sintéticas — 150 golpe, 155 legítimas | IA, revisão manual |
| `backend/scripts/dataset_v1.py` | gerador do dataset | — |
| `backend/scripts/evaluate_dataset.py` | roda o código de produção contra o dataset e mede | — |
| `docs/metrics_v1.md` | resultado da última medição | — |

## Regra

**Nada de mensagem real aqui.** Todo conteúdo é sintético ou fictício. Se um dia entrar dado real de usuário, ele não vai para o repositório — vai para o armazenamento operacional, com hash e preview curto (`STORE_FULL_MESSAGE=false`).

## Por que não está em `dados/original` e `dados/tratado`

Não existe pipeline de transformação. O dataset é gerado, versionado e consumido direto. Criar duas pastas vazias só para seguir um diagrama seria estrutura sem função.
