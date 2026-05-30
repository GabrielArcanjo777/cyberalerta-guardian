from fastapi.testclient import TestClient
from main import app


def test_examples_endpoint():
    client = TestClient(app)
    response = client.get("/examples")
    assert response.status_code == 200
    examples = response.json().get("examples", [])
    assert "falso filho pedindo Pix" in examples
    assert "falso banco com link" in examples
    assert "pedido de codigo SMS" in examples
    assert "falso suporte com app remoto" in examples
    assert "falso emprego pedindo taxa" in examples
