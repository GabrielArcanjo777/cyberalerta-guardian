# -*- coding: utf-8 -*-
"""Avalia o detector real (regras + Policy Engine sem LLM) contra o dataset v1.

Roda o MESMO código de produção (RiskAssessmentService, build_deterministic_assessment,
HybridDecisionPolicy) — nada reimplementado — e mede:

  1. Alerta determinístico (comportamento atual: risk_level == HIGH, score >= 70)
     → precisão, recall, FPR, F1 tratando "alertaria" como classificador binário.
  2. Criação de caso (score >= 40) → mesmas métricas.
  3. Distribuição de decisões da Policy Engine SEM LLM (postura padrão segura):
     como require_llm_for_auto_alert=True, o máximo é REVIEW — mostra quanto
     vai para revisão humana vs descarte.

Saídas:
  - backend/data/scam_dataset_v1.jsonl  (dataset materializado)
  - docs/metrics_v1.md                  (relatório)
  - stdout                              (resumo)

Uso:  backend/venv/Scripts/python.exe backend/scripts/evaluate_dataset.py
"""
from __future__ import annotations

import json
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path

BACKEND_DIR = Path(__file__).resolve().parent.parent
PROJECT_ROOT = BACKEND_DIR.parent
sys.path.insert(0, str(BACKEND_DIR))
sys.path.insert(0, str(Path(__file__).resolve().parent))

import os
os.environ.setdefault("CYBERALERTA_DISABLE_DOTENV", "1")

from dataset_v1 import entries  # noqa: E402

from app.event_model import EventModelService  # noqa: E402
from app.event_model.models import Message, MessageDirection  # noqa: E402
from app.event_model.risk_assessment_service import (  # noqa: E402
    CASE_CREATION_THRESHOLD,
    HIGH_RISK_THRESHOLD,
)
from app.hybrid.deterministic import build_deterministic_assessment  # noqa: E402
from app.hybrid.models import HybridAction, HybridDecisionContext  # noqa: E402
from app.hybrid.policy import HybridDecisionPolicy  # noqa: E402


def _metrics(tp: int, fp: int, fn: int, tn: int) -> dict:
    precision = tp / (tp + fp) if (tp + fp) else 0.0
    recall = tp / (tp + fn) if (tp + fn) else 0.0
    fpr = fp / (fp + tn) if (fp + tn) else 0.0
    f1 = 2 * precision * recall / (precision + recall) if (precision + recall) else 0.0
    return {
        "tp": tp, "fp": fp, "fn": fn, "tn": tn,
        "precision": round(precision, 4),
        "recall": round(recall, 4),
        "fpr": round(fpr, 4),
        "f1": round(f1, 4),
    }


def main() -> None:
    event_model = EventModelService.in_memory()
    policy = HybridDecisionPolicy()
    # Postura padrão segura: LLM desligada, shadow, LLM exigida p/ auto-alert.
    ctx = HybridDecisionContext(
        llm_enabled=False, shadow_mode=True, require_llm_for_auto_alert=True
    )

    rows = []
    for entry in entries():
        message = Message(
            protected_person_id="eval",
            direction=MessageDirection.INBOUND,
            channel="whatsapp:eval",
            body=entry["text"],
        )
        assessment = event_model.risk_assessments.assess(message)
        det = build_deterministic_assessment(assessment, entry["text"])
        decision = policy.decide(det, None, ctx, llm_available=False)
        rows.append({
            **entry,
            "score": assessment.score,
            "risk_level": assessment.risk_level.value,
            "signals": assessment.signals,
            "policy_action": decision.action.value,
        })

    n_scam = sum(1 for r in rows if r["label"] == "scam")
    n_legit = sum(1 for r in rows if r["label"] == "legit")

    # --- 1) alerta determinístico atual: HIGH (score >= 70) ------------------
    alert = _metrics(
        tp=sum(1 for r in rows if r["label"] == "scam" and r["score"] >= HIGH_RISK_THRESHOLD),
        fp=sum(1 for r in rows if r["label"] == "legit" and r["score"] >= HIGH_RISK_THRESHOLD),
        fn=sum(1 for r in rows if r["label"] == "scam" and r["score"] < HIGH_RISK_THRESHOLD),
        tn=sum(1 for r in rows if r["label"] == "legit" and r["score"] < HIGH_RISK_THRESHOLD),
    )
    # --- 2) criação de caso: score >= 40 --------------------------------------
    case = _metrics(
        tp=sum(1 for r in rows if r["label"] == "scam" and r["score"] >= CASE_CREATION_THRESHOLD),
        fp=sum(1 for r in rows if r["label"] == "legit" and r["score"] >= CASE_CREATION_THRESHOLD),
        fn=sum(1 for r in rows if r["label"] == "scam" and r["score"] < CASE_CREATION_THRESHOLD),
        tn=sum(1 for r in rows if r["label"] == "legit" and r["score"] < CASE_CREATION_THRESHOLD),
    )
    # --- 3) Policy Engine sem LLM ---------------------------------------------
    dist_scam = Counter(r["policy_action"] for r in rows if r["label"] == "scam")
    dist_legit = Counter(r["policy_action"] for r in rows if r["label"] == "legit")

    false_negatives = [r for r in rows if r["label"] == "scam" and r["score"] < HIGH_RISK_THRESHOLD]
    false_positives = [r for r in rows if r["label"] == "legit" and r["score"] >= HIGH_RISK_THRESHOLD]
    fp_case = [r for r in rows if r["label"] == "legit" and r["score"] >= CASE_CREATION_THRESHOLD]

    # --- write dataset jsonl ---------------------------------------------------
    data_dir = BACKEND_DIR / "data"
    data_dir.mkdir(exist_ok=True)
    dataset_path = data_dir / "scam_dataset_v1.jsonl"
    with dataset_path.open("w", encoding="utf-8") as fh:
        for r in rows:
            fh.write(json.dumps(
                {k: r[k] for k in ("id", "label", "category", "text")},
                ensure_ascii=False,
            ) + "\n")

    # --- write report ----------------------------------------------------------
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%MZ")

    def _table(m: dict) -> str:
        return (
            f"| TP | FP | FN | TN | Precisão | Recall | FPR | F1 |\n"
            f"|---|---|---|---|---|---|---|---|\n"
            f"| {m['tp']} | {m['fp']} | {m['fn']} | {m['tn']} "
            f"| {m['precision']:.1%} | {m['recall']:.1%} | {m['fpr']:.1%} | {m['f1']:.1%} |\n"
        )

    def _list(rs, limit=15):
        lines = []
        for r in rs[:limit]:
            lines.append(
                f"- `{r['id']}` [{r['category']}] score={r['score']} "
                f"sinais={','.join(r['signals']) or '-'} — “{r['text'][:90]}”"
            )
        if len(rs) > limit:
            lines.append(f"- … e mais {len(rs) - limit}")
        return "\n".join(lines) or "- (nenhum)"

    report = f"""# Métricas v1 — detector determinístico (dataset sintético)

Gerado em {now} por `backend/scripts/evaluate_dataset.py` (código de produção real,
sem LLM — postura padrão). Dataset: `backend/data/scam_dataset_v1.jsonl`,
**{len(rows)} mensagens** ({n_scam} golpe / {n_legit} legítimas), sintético e rotulado
à mão (ver provenance em `backend/scripts/dataset_v1.py`).

## 1. Alerta ao contato de confiança (regra atual: risco HIGH, score ≥ {HIGH_RISK_THRESHOLD})

{_table(alert)}

Interpretação: das mensagens que disparariam alerta, {alert['precision']:.1%} são golpe
de verdade; o detector captura {alert['recall']:.1%} dos golpes; {alert['fpr']:.1%} das
mensagens legítimas gerariam alerta indevido.

## 2. Criação de caso no console (score ≥ {CASE_CREATION_THRESHOLD})

{_table(case)}

Casos MEDIUM não alertam ninguém — ficam no Guardian Console para revisão. FPR maior
aqui é esperado e aceitável (custo = revisão humana, não incômodo à família).

## 3. Policy Engine híbrida SEM LLM (postura padrão segura)

Com `HYBRID_REQUIRE_LLM_FOR_AUTO_ALERT=true` e LLM indisponível, o máximo é REVIEW
(nunca AUTO_ALERT) — comportamento verificado:

| Label | {' | '.join(a.value for a in HybridAction)} |
|---|---|---|---|
| golpe (n={n_scam}) | {dist_scam.get('DISCARD', 0)} | {dist_scam.get('REVIEW', 0)} | {dist_scam.get('AUTO_ALERT', 0)} |
| legítima (n={n_legit}) | {dist_legit.get('DISCARD', 0)} | {dist_legit.get('REVIEW', 0)} | {dist_legit.get('AUTO_ALERT', 0)} |

## Falsos negativos do alerta (golpes com score < {HIGH_RISK_THRESHOLD})

{_list(false_negatives)}

## Falsos positivos do alerta (legítimas com score ≥ {HIGH_RISK_THRESHOLD})

{_list(false_positives)}

## Falsos positivos de caso (legítimas com score ≥ {CASE_CREATION_THRESHOLD} → console)

{_list(fp_case)}

## Limitações (honestas)

- Dataset **sintético** escrito à mão; não substitui mensagens reais de piloto.
- Métricas medem apenas a camada **determinística** (regex + pesos). A análise LLM
  do pipeline híbrido não entra aqui — exige provider real; o desenho previsto é
  rodá-la em **shadow mode** durante o piloto e comparar as decisões gravadas.
- Sem near-duplicates/augmentation: cada linha é uma mensagem distinta.
- Rotulagem por um único autor; sem validação cruzada de anotadores.
"""

    docs_dir = PROJECT_ROOT / "docs"
    docs_dir.mkdir(exist_ok=True)
    report_path = docs_dir / "metrics_v1.md"
    report_path.write_text(report, encoding="utf-8")

    # --- stdout summary ---------------------------------------------------------
    print(f"Dataset: {len(rows)} mensagens ({n_scam} scam / {n_legit} legit)")
    print(f"-> {dataset_path}")
    print(f"-> {report_path}")
    print(f"\n[ALERTA HIGH >={HIGH_RISK_THRESHOLD}]", json.dumps(alert))
    print(f"[CASO >={CASE_CREATION_THRESHOLD}]        ", json.dumps(case))
    print("\nPolicy s/ LLM — scam:", dict(dist_scam), "| legit:", dict(dist_legit))
    print(f"\nFalsos negativos (alerta): {len(false_negatives)}")
    print(f"Falsos positivos (alerta): {len(false_positives)}")


if __name__ == "__main__":
    main()
