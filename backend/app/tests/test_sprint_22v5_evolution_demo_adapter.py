from __future__ import annotations

from typing import Any, Mapping

from fastapi.testclient import TestClient

from app.channel_adapters import ChannelProvider, DeliveryStatus
from app.channel_adapters.evolution_demo_adapter import (
    EvolutionDemoAdapter,
    EvolutionDemoConfig,
)
from app.event_model import BotEventType, EventModelService
from app.evolution_demo import EvolutionDemoService
from main import app


class FakeEvolutionTransport:
    def __init__(self) -> None:
        self.calls: list[dict[str, str]] = []

    def send_text(
        self,
        *,
        api_url: str,
        api_key: str,
        instance_name: str,
        to_address: str,
        body: str,
    ) -> Mapping[str, Any]:
        self.calls.append(
            {
                "api_url": api_url,
                "api_key": api_key,
                "instance_name": instance_name,
                "to_address": to_address,
                "body": body,
            }
        )
        return {"messageId": f"EVOOUT{len(self.calls):03d}", "status": "sent"}


def _config() -> EvolutionDemoConfig:
    return EvolutionDemoConfig(
        api_url="http://evolution.local",
        api_key="local-demo-key",
        instance_name="guardian-demo",
        guardian_address="5511888880001",
    )


def _messages_upsert(message_id: str = "EVOIN001") -> dict[str, Any]:
    return {
        "event": "MESSAGES_UPSERT",
        "instance": "guardian-demo",
        "data": {
            "key": {
                "id": message_id,
                "remoteJid": "5511999990001@s.whatsapp.net",
                "fromMe": False,
            },
            "pushName": "Dona Lucia",
            "messageTimestamp": 1780000000,
            "message": {
                "conversation": (
                    "Mae, troquei de numero. Preciso de um Pix urgente. "
                    "Nao liga agora."
                )
            },
        },
    }


def test_evolution_demo_adapter_parses_messages_upsert_to_inbound_message():
    adapter = EvolutionDemoAdapter(config=_config(), transport=FakeEvolutionTransport())

    inbound = adapter.parseProviderPayload(_messages_upsert())

    assert inbound.provider == ChannelProvider.EVOLUTION_DEMO
    assert inbound.external_message_id == "EVOIN001"
    assert inbound.from_address == "5511999990001"
    assert inbound.to_address == "guardian-demo"
    assert inbound.profile_name == "Dona Lucia"
    assert "Pix urgente" in inbound.body
    assert inbound.raw_payload["event"] == "MESSAGES_UPSERT"


def test_evolution_demo_service_creates_case_and_sends_demo_messages():
    transport = FakeEvolutionTransport()
    service = EvolutionDemoService(
        adapter=EvolutionDemoAdapter(config=_config(), transport=transport),
        event_model=EventModelService.in_memory(),
    )

    response = service.handle_webhook(_messages_upsert("EVOIN002"))

    assert response.accepted is True
    assert response.duplicate is False
    assert response.case_created is True
    assert response.risk_level == "high"
    assert response.protected_reply_sent is True
    assert response.guardian_notified is True
    assert len(transport.calls) == 2
    assert transport.calls[0]["to_address"] == "5511999990001"
    assert transport.calls[1]["to_address"] == "5511888880001"
    assert response.events == [
        BotEventType.MESSAGE_RECEIVED.value,
        BotEventType.SUSPICIOUS_MESSAGE_RECEIVED.value,
        BotEventType.RISK_ASSESSMENT_CREATED.value,
        BotEventType.CASE_CREATED.value,
        BotEventType.RESPONSIBLE_ALERT_QUEUED.value,
        BotEventType.DELIVERY_STATUS_UPDATED.value,
        BotEventType.SAFE_REPLY_SENT.value,
        BotEventType.PROTECTED_PERSON_REPLIED.value,
        BotEventType.DELIVERY_STATUS_UPDATED.value,
        BotEventType.RESPONSIBLE_NOTIFIED.value,
    ]


def test_evolution_demo_idempotency_uses_message_id():
    service = EvolutionDemoService(
        adapter=EvolutionDemoAdapter(config=_config(), transport=FakeEvolutionTransport()),
        event_model=EventModelService.in_memory(),
    )

    first = service.handle_webhook(_messages_upsert("EVOIDEMPOTENT001"))
    duplicate = service.handle_webhook(_messages_upsert("EVOIDEMPOTENT001"))

    assert first.case_created is True
    assert duplicate.duplicate is True
    assert duplicate.case_created is False
    assert len(service.event_model.repositories.messages.list_all()) == 1
    assert len(service.event_model.repositories.cases.list_all()) == 1


def test_evolution_demo_without_guardian_env_simulates_responsible_notification():
    service = EvolutionDemoService(
        adapter=EvolutionDemoAdapter(config=_config(), transport=FakeEvolutionTransport()),
        event_model=EventModelService.in_memory(),
        guardian_address="",
    )

    response = service.handle_webhook(_messages_upsert("EVOSIM001"))

    assert response.guardian_notified is True
    assert response.outbound_messages[-1].simulated is True
    assert response.outbound_messages[-1].status == DeliveryStatus.DELIVERED.value
    assert BotEventType.RESPONSIBLE_NOTIFIED.value in response.events


def test_evolution_demo_maps_delivery_status():
    adapter = EvolutionDemoAdapter(config=_config(), transport=FakeEvolutionTransport())

    status = adapter.mapDeliveryStatus(
        {
            "event": "MESSAGES_UPDATE",
            "data": {
                "key": {"id": "EVOOUT001"},
                "status": "delivery_ack",
                "timestamp": 1780000001,
            },
        }
    )

    assert status.external_message_id == "EVOOUT001"
    assert status.status == DeliveryStatus.DELIVERED


def test_evolution_webhook_endpoint_accepts_mocked_payload_without_real_network():
    client = TestClient(app)

    health = client.get("/webhook/evolution/health")
    assert health.status_code == 200
    assert health.json()["provider"] == ChannelProvider.EVOLUTION_DEMO.value
    assert health.json()["production"] is False

    response = client.post("/webhook/evolution", json=_messages_upsert("EVOAPI001"))

    assert response.status_code == 200
    body = response.json()
    assert body["provider"] == ChannelProvider.EVOLUTION_DEMO.value
    assert body["accepted"] is True
    assert body["case_created"] is True
    assert body["provider_message_id"] == "EVOAPI001"
