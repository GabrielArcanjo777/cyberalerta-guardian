from fastapi.testclient import TestClient
from main import app


def test_recovery_paid_true_returns_checklist():
    client = TestClient(app)
    payload = {
        "paid": True,
        "clicked_link": False,
        "shared_documents": False,
        "shared_password": False,
        "installed_app": False,
        "shared_sms_code": False,
    }
    response = client.post("/recovery", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Contactar instituicao financeira imediatamente." in data["checklist"]
    assert "Registrar ocorrencia de fraude e bloquear transacao." in data["checklist"]
    assert data["incident_type"] == "pix_sent"
    assert data["severity"] == "critical"
    assert data["n8n_action"] == "send_recovery_pix_sent"
    assert data["whatsapp_step_messages"]
    assert "Nao ha garantia de recuperacao de valores" in data["disclaimer"]


def test_recovery_accepts_new_optional_fields_without_breaking_legacy_fields():
    client = TestClient(app)
    response = client.post(
        "/recovery",
        json={
            "incident_type": "suspicious_link_clicked",
            "has_clicked_link": True,
            "case_id": "case-recovery-1",
            "n8n_execution_id": "exec-recovery-1",
            "paid": False,
            "clicked_link": False,
            "shared_documents": False,
            "shared_password": False,
            "installed_app": False,
            "shared_sms_code": False,
        },
    )

    assert response.status_code == 200
    data = response.json()
    assert data["incident_type"] == "suspicious_link_clicked"
    assert data["case_id"] == "case-recovery-1"
    assert data["n8n_execution_id"] == "exec-recovery-1"
    assert data["recovery_plan"]
    assert data["evidence_to_save"] == data["evidence_to_collect"]
    assert data["what_not_to_do"] == data["do_not_do"]


def test_recovery_pix_playbook_does_not_promise_guaranteed_refund():
    client = TestClient(app)
    response = client.post(
        "/recovery",
        json={
            "incident_type": "pix_sent",
            "already_paid": True,
            "amount": 250.0,
            "payment_method": "pix",
            "bank_name": "Banco Demo",
        },
    )

    assert response.status_code == 200
    serialized = str(response.json()).lower()
    assert "garantia de recuperacao" in serialized
    assert "devolucao garantida" not in serialized
    assert "reembolso garantido" not in serialized


def test_recovery_playbooks_cover_all_supported_incidents():
    client = TestClient(app)
    incident_types = [
        "pix_sent",
        "suspicious_link_clicked",
        "sms_code_shared",
        "password_shared",
        "remote_app_installed",
        "job_fee_paid",
        "unknown",
    ]

    for incident_type in incident_types:
        response = client.post("/recovery", json={"incident_type": incident_type})
        assert response.status_code == 200
        data = response.json()
        assert data["incident_type"] == incident_type
        assert data["summary"]
        assert data["immediate_steps"]
        assert data["next_24h_steps"]
        assert data["evidence_to_collect"]
        assert data["contacts_to_notify"]
        assert data["do_not_do"]
        assert data["whatsapp_summary_message"].startswith("Guardian Recovery:")
        assert data["trusted_contact_message"]
        assert data["report_summary"]
        assert data["disclaimer"]


def test_safety_policy_service_exists_and_can_be_called():
    from app.services.safety_policy import SafetyPolicyService

    policy = SafetyPolicyService()
    policy.check_text("Este texto e seguro.")
    try:
        policy.check_text("Este texto contem phishing")
    except ValueError as exc:
        assert "blocked by safety policy" in str(exc)
    else:
        assert False, "SafetyPolicyService did not block forbidden text"
