# -*- coding: utf-8 -*-
"""Regressão de qualidade do detector contra o dataset rotulado v1.

Roda o pipeline de produção sobre as 305 mensagens e trava pisos/tetos medidos
em docs/metrics_v1.md (com folga para não ser frágil). Se alguém mexer nas
regras/thresholds e degradar precisão ou explodir falso positivo, isso quebra.
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import pytest

SCRIPTS_DIR = Path(__file__).resolve().parent.parent.parent / "scripts"
sys.path.insert(0, str(SCRIPTS_DIR))

from dataset_v1 import entries  # noqa: E402

from app.event_model import EventModelService
from app.event_model.models import Message, MessageDirection
from app.event_model.risk_assessment_service import (
    CASE_CREATION_THRESHOLD,
    HIGH_RISK_THRESHOLD,
)
from app.hybrid.deterministic import build_deterministic_assessment
from app.hybrid.models import HybridAction, HybridDecisionContext
from app.hybrid.policy import HybridDecisionPolicy


@pytest.fixture(scope="module")
def evaluated():
    event_model = EventModelService.in_memory()
    policy = HybridDecisionPolicy()
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
        rows.append({**entry, "score": assessment.score, "action": decision.action})
    return rows


def test_dataset_has_a_few_hundred_unique_entries(evaluated):
    assert len(evaluated) >= 300
    ids = [r["id"] for r in evaluated]
    assert len(ids) == len(set(ids)), "ids duplicados no dataset"
    labels = Counter(r["label"] for r in evaluated)
    assert labels["scam"] >= 140 and labels["legit"] >= 140


def test_alert_precision_and_fpr(evaluated):
    tp = sum(1 for r in evaluated if r["label"] == "scam" and r["score"] >= HIGH_RISK_THRESHOLD)
    fp = sum(1 for r in evaluated if r["label"] == "legit" and r["score"] >= HIGH_RISK_THRESHOLD)
    tn = sum(1 for r in evaluated if r["label"] == "legit" and r["score"] < HIGH_RISK_THRESHOLD)
    assert tp + fp > 0, "nenhum alerta disparado no dataset"
    # Medido: precisão 100%, FPR 0%. Pisos com folga:
    assert tp / (tp + fp) >= 0.90
    assert fp / (fp + tn) <= 0.02


def test_case_creation_quality(evaluated):
    tp = sum(1 for r in evaluated if r["label"] == "scam" and r["score"] >= CASE_CREATION_THRESHOLD)
    fp = sum(1 for r in evaluated if r["label"] == "legit" and r["score"] >= CASE_CREATION_THRESHOLD)
    fn = sum(1 for r in evaluated if r["label"] == "scam" and r["score"] < CASE_CREATION_THRESHOLD)
    tn = sum(1 for r in evaluated if r["label"] == "legit" and r["score"] < CASE_CREATION_THRESHOLD)
    # Medido: precisão 96.7%, recall 58%, FPR 1.9%. Pisos com folga:
    assert tp / (tp + fp) >= 0.90
    assert tp / (tp + fn) >= 0.50
    assert fp / (fp + tn) <= 0.05


def test_policy_without_llm_never_auto_alerts(evaluated):
    # Invariante inviolável: sem LLM disponível, nenhuma mensagem — golpe ou não —
    # pode resultar em AUTO_ALERT.
    assert all(r["action"] != HybridAction.AUTO_ALERT for r in evaluated)


def test_policy_without_llm_routes_most_scams_to_review(evaluated):
    scams = [r for r in evaluated if r["label"] == "scam"]
    discarded = sum(1 for r in scams if r["action"] == HybridAction.DISCARD)
    # Medido: 26/150 (17.3%) descartados. Teto com folga:
    assert discarded / len(scams) <= 0.25
