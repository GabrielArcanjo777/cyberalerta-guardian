import re

from fastapi.testclient import TestClient

from app.protected_response.response_policy import count_sentences, enforce_safe_reply
from app.protected_response.response_schemas import ProtectedResponseGenerateRequest
from app.protected_response.response_service import ProtectedPersonResponseService
from main import app

client = TestClient(app)
service = ProtectedPersonResponseService()


def test_generate_pix_high_risk_with_contact():
    response = service.generate(
        ProtectedResponseGenerateRequest(
            risk_level="alto",
            category="golpe_pix",
            signals=["urgencia", "numero_novo", "pedido_pix"],
            trusted_contact_alias="Gabriel",
        )
    )
    assert "Pix" in response.short_reply
    assert "golpe" in response.short_reply.lower()
    assert "Gabriel" in response.short_reply
    assert count_sentences(response.short_reply) <= 2
    assert "confront" not in response.short_reply.lower()


def test_generate_link_suspeito():
    response = service.generate(
        ProtectedResponseGenerateRequest(
            risk_level="alto",
            category="link_suspeito",
            signals=["link"],
        )
    )
    assert "link" in response.short_reply.lower()
    assert count_sentences(response.short_reply) <= 2


def test_generate_codigo_senha():
    response = service.generate(
        ProtectedResponseGenerateRequest(
            risk_level="critico",
            category="codigo_senha",
            signals=["pedido_codigo"],
            trusted_contact_alias="Gabriel",
        )
    )
    lowered = response.short_reply.lower()
    assert "código" in lowered or "codigo" in lowered or "senha" in lowered
    assert count_sentences(response.short_reply) <= 2


def test_generate_low_risk():
    response = service.generate(
        ProtectedResponseGenerateRequest(
            risk_level="baixo",
            category="risco_baixo",
            signals=[],
        )
    )
    assert "Recebi sua mensagem" in response.short_reply
    assert count_sentences(response.short_reply) <= 2


def test_never_suggests_confrontation():
    samples = [
        ("alto", "golpe_pix", ["urgencia"]),
        ("alto", "link_suspeito", ["link"]),
        ("critico", "codigo_senha", ["codigo"]),
        ("baixo", "risco_baixo", []),
    ]
    for risk, category, signals in samples:
        response = service.generate(
            ProtectedResponseGenerateRequest(
                risk_level=risk,
                category=category,
                signals=signals,
                trusted_contact_alias="Gabriel",
            )
        )
        lowered = response.short_reply.lower()
        assert "confront" not in lowered
        assert "responda ao" not in lowered
        assert count_sentences(response.short_reply) <= 2


def test_simple_channel_uses_protected_response_agent():
    response = client.post(
        "/simple-channel/submit",
        json={
            "protected_person_alias": "Dona Lucia",
            "channel": "whatsapp_mock",
            "content_type": "text",
            "content": "Mae, troquei de numero. Preciso fazer um Pix urgente.",
            "consent": True,
            "trusted_contact_alias": "Gabriel",
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert "Gabriel" in body["simple_reply"]
    assert count_sentences(body["simple_reply"]) <= 2


def test_enforce_safe_reply_limits_sentences():
    long_text = "Frase um. Frase dois. Frase tres."
    trimmed = enforce_safe_reply(long_text)
    assert count_sentences(trimmed) <= 2
    assert not re.search(r"Frase tres", trimmed)
