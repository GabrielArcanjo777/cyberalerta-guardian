from fastapi.testclient import TestClient

from main import app

client = TestClient(app)

CREATE_PAYLOAD = {
    "case_id": "case-demo-001",
    "protected_person_alias": "Dona Lucia",
    "guardian_alias": "Gabriel",
    "risk_level": "alto",
    "suspected_request": "Pix urgente para falso filho",
    "trusted_contact_alias": "Gabriel",
}


def test_create_assisted_proof_session():
    response = client.post("/proof-trust/assisted-session", json=CREATE_PAYLOAD)
    assert response.status_code == 200
    body = response.json()
    assert body["case_id"] == "case-demo-001"
    assert body["status"] == "in_progress"
    assert body["current_step"] == "confirm_independent_channel"
    assert body["steps"][0]["id"] == "do_not_reply"
    assert body["steps"][0]["status"] == "completed"
    assert body["final_decision"] is None
    assert "MVP" in body["demo_note"] or "simulad" in body["demo_note"].lower()


def test_low_risk_cannot_start_session():
    response = client.post(
        "/proof-trust/assisted-session",
        json={**CREATE_PAYLOAD, "case_id": "case-demo-002", "risk_level": "baixo"},
    )
    assert response.status_code == 400


def test_full_proof_session_flow():
    created = client.post("/proof-trust/assisted-session", json=CREATE_PAYLOAD)
    session_id = created.json()["session_id"]

    fetched = client.get(f"/proof-trust/assisted-session/{session_id}")
    assert fetched.status_code == 200

    flow = [
        ("confirm_independent_channel", "Responsável confirmou pelo contato salvo."),
        ("identity_challenge", "Pergunta combinada respondida corretamente."),
        ("confirm_request_real", "Pedido de Pix não era real."),
        ("record_decision", "Golpe confirmado após verificação independente."),
        ("release_or_block", "Manter pausa protetiva e orientar relatório."),
    ]

    for step_id, note in flow:
        payload = {"step_id": step_id, "status": "completed", "note": note}
        if step_id == "record_decision":
            payload["final_decision"] = "confirmed_scam"
        response = client.post(
            f"/proof-trust/assisted-session/{session_id}/step",
            json=payload,
        )
        assert response.status_code == 200, response.text

    final = client.get(f"/proof-trust/assisted-session/{session_id}").json()
    assert final["status"] == "confirmed_scam"
    assert final["final_decision"] == "confirmed_scam"
    assert final["guardian_note"]

    case = client.get("/guardian-console/cases/case-demo-001").json()
    assert case["proof_of_trust_status"] == "completed"
    assert case["status"] == "confirmed_scam"


def test_session_not_found():
    response = client.get("/proof-trust/assisted-session/proof-missing")
    assert response.status_code == 404
