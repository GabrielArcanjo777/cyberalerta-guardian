from fastapi.testclient import TestClient
from main import app


def test_main_case_returns_critical_and_trust_lock():
    client = TestClient(app)
    payload = {
        "user_name": "Dona Lucia",
        "age_group": "elderly",
        "trusted_contact_name": "Gabriel",
        "trusted_contact_relation": "neto",
        "action_type": "pix",
        "channel": "whatsapp",
        "message": "Mae, troquei de numero. Meu celular quebrou. Preciso pagar uma conta urgente. Faz um Pix de R$ 780? Nao liga agora porque estou em reuniao.",
        "already_acted": False,
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] == "critical"
    assert data["trust_lock"]["activated"] is True
    assert data["scam_type"] == "falso familiar pedindo Pix"
    assert "urgencia" in data["manipulations"]
    assert data["trusted_circle_alert"]["should_alert"] is True


def test_false_bank_case_generates_proof_of_trust():
    client = TestClient(app)
    payload = {
        "user_name": "Dona Lucia",
        "age_group": "elderly",
        "trusted_contact_name": "Gabriel",
        "trusted_contact_relation": "neto",
        "action_type": "link",
        "channel": "whatsapp",
        "message": "Recebi uma mensagem do banco com um link urgente para atualizar minha conta.",
        "already_acted": False,
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert "Nao responda o numero novo." in data["proof_of_trust"] or len(data["proof_of_trust"]) > 0


def test_false_employment_case_has_protection_flow():
    client = TestClient(app)
    payload = {
        "user_name": "Dona Lucia",
        "age_group": "elderly",
        "trusted_contact_name": "Gabriel",
        "trusted_contact_relation": "neto",
        "action_type": "taxa",
        "channel": "whatsapp",
        "message": "Disseram que preciso pagar uma taxa para conseguir o emprego. E urgente.",
        "already_acted": False,
    }
    response = client.post("/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["scam_type"] == "falso emprego pedindo taxa"
    assert data["risk_level"] in {"medium", "high", "critical"}
    assert "intervention_playbook" in data
    assert data["trust_evidence"]["confidence"] == 94
