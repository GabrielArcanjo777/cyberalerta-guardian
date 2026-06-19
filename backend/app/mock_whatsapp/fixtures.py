from __future__ import annotations

from app.mock_whatsapp.models import MockWhatsAppFixture, MockWhatsAppInboundRequest


MOCK_WHATSAPP_FIXTURES: tuple[MockWhatsAppFixture, ...] = (
    MockWhatsAppFixture(
        fixture_id="false_relative_pix",
        title="Falso parente pedindo Pix",
        description="Numero novo, urgencia, Pix e pedido para nao ligar.",
        request=MockWhatsAppInboundRequest(
            providerMessageId="mock-fixture-false-relative-001",
            body="Mae, troquei de numero. Preciso de um Pix urgente. Nao liga agora.",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
        ),
        expected="Score alto, caso criado e responsavel alertado no mock.",
    ),
    MockWhatsAppFixture(
        fixture_id="suspicious_link_urgency",
        title="Link suspeito com urgencia",
        description="Link desconhecido combinado com urgencia para criar caso.",
        request=MockWhatsAppInboundRequest(
            providerMessageId="mock-fixture-link-001",
            body="Urgente: clique neste link https://regularizacao-conta.invalid para regularizar sua conta.",
            protected_person_alias="Seu Joao",
            guardian_alias="Gabriel",
        ),
        expected="Score medio, caso criado e alerta simulado.",
    ),
    MockWhatsAppFixture(
        fixture_id="code_password_pressure",
        title="Codigo/senha com pressao",
        description="Pedido de codigo com urgencia e sigilo.",
        request=MockWhatsAppInboundRequest(
            providerMessageId="mock-fixture-code-001",
            body="Me manda o codigo que chegou no seu celular. E urgente e nao conte para ninguem.",
            protected_person_alias="Maria Helena",
            guardian_alias="Ana",
            guardian_address="+5511888880002",
        ),
        expected="Score alto, caso criado e responsavel alertado no mock.",
    ),
    MockWhatsAppFixture(
        fixture_id="normal_message",
        title="Mensagem normal",
        description="Mensagem cotidiana sem sinais fortes.",
        request=MockWhatsAppInboundRequest(
            providerMessageId="mock-fixture-normal-001",
            body="Oi, tudo bem?",
            protected_person_alias="Dona Lucia",
            guardian_alias="Gabriel",
        ),
        expected="Baixo risco, sem caso e sem alerta.",
    ),
)


def get_fixture(fixture_id: str) -> MockWhatsAppFixture:
    for fixture in MOCK_WHATSAPP_FIXTURES:
        if fixture.fixture_id == fixture_id:
            return fixture
    raise KeyError(f"Fixture not found: {fixture_id}")
