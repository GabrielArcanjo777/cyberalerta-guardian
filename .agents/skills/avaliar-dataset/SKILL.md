---
name: avaliar-dataset
description: Mede o detector de golpes contra o dataset sintético e atualiza docs/metrics_v1.md. Use depois de mexer em regras de risco.
---

# Avaliar o dataset

## Quando usar

Sempre que mudar `backend/app/hybrid/`, `backend/app/event_model/risk_assessment_service.py` ou limiares de risco.

## Passos

```bash
python backend/scripts/evaluate_dataset.py
git diff docs/metrics_v1.md
```

O script roda o código de produção (sem LLM) contra `backend/data/scam_dataset_v1.jsonl` e reescreve `docs/metrics_v1.md`.

## Como ler

- **Alerta** (score ≥ 65): precisão alta e recall baixo é a escolha do projeto — alerta falso faz a família parar de confiar.
- **Caso** (score ≥ 40): vai para revisão humana; aqui recall importa mais.
- O dataset é sintético. O número vale como **regressão** (piorou ou melhorou em relação ao commit anterior), nunca como desempenho real (ADR-007).

## Pronto quando

O diff de `metrics_v1.md` está explicado na mensagem de commit e nenhum falso positivo de alerta apareceu sem justificativa.
