from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List
from uuid import uuid4

from app.channel_adapters import (
    ChannelIngressService,
    DeliveryStatus,
    InMemoryDeliveryStatusRegistry,
    InMemoryProviderMessageRegistry,
    MockWhatsAppAdapter,
    OutboundMessageKind,
    OutboundMessageRequest,
)
from app.event_model import BotEventType, EventModelService
from app.mock_whatsapp.fixtures import MOCK_WHATSAPP_FIXTURES, get_fixture
from app.mock_whatsapp.models import (
    MockOutboundRecord,
    MockWhatsAppFixture,
    MockWhatsAppInboundRequest,
    MockWhatsAppSimulationResponse,
)


class MockWhatsAppSimulatorService:
    def __init__(self, event_model: EventModelService | None = None) -> None:
        self.event_model = event_model or EventModelService.in_memory()
        self.adapter = MockWhatsAppAdapter()
        self.provider_messages = InMemoryProviderMessageRegistry()
        self.delivery_statuses = InMemoryDeliveryStatusRegistry()
        self.ingress = ChannelIngressService(
            event_model=self.event_model,
            provider_message_registry=self.provider_messages,
        )
        self._simulations: Dict[str, MockWhatsAppSimulationResponse] = {}

    def list_fixtures(self) -> List[MockWhatsAppFixture]:
        return list(MOCK_WHATSAPP_FIXTURES)

    def simulate_fixture(self, fixture_id: str) -> MockWhatsAppSimulationResponse:
        return self.simulate_inbound(get_fixture(fixture_id).request)

    def simulate_inbound(self, request: MockWhatsAppInboundRequest) -> MockWhatsAppSimulationResponse:
        simulation_id = f"mock-sim-{uuid4().hex}"
        before_events = len(self.event_model.repositories.events.list_all())
        payload = request.model_dump(by_alias=True, exclude_none=True)
        if request.provider_message_id is None:
            payload["providerMessageId"] = f"mock-in-{uuid4().hex}"

        ingress_result = self.ingress.ingest_inbound(
            adapter=self.adapter,
            payload=payload,
            protected_person_alias=request.protected_person_alias,
            guardian_alias=request.guardian_alias,
        )
        outbound_messages: List[MockOutboundRecord] = []

        if ingress_result.case_id and not ingress_result.duplicate:
            outbound_messages.append(
                self._send_guardian_alert(
                    request=request,
                    case_id=ingress_result.case_id,
                    message_id=ingress_result.message_id,
                )
            )

        events = self.event_model.repositories.events.list_all()[before_events:]
        risk_score = None
        risk_level = None
        if ingress_result.risk_assessment_id:
            assessment = self.event_model.repositories.risk_assessments.get(ingress_result.risk_assessment_id)
            if assessment:
                risk_score = assessment.score
                risk_level = assessment.risk_level.value

        response = MockWhatsAppSimulationResponse(
            simulation_id=simulation_id,
            duplicate=ingress_result.duplicate,
            provider_message_id=ingress_result.inbound.provider_message_id,
            message_id=ingress_result.message_id,
            risk_assessment_id=ingress_result.risk_assessment_id,
            risk_score=risk_score,
            risk_level=risk_level,
            case_id=ingress_result.case_id,
            case_created=ingress_result.case_id is not None,
            guardian_notified=bool(outbound_messages),
            outbound_messages=outbound_messages,
            events=[event.event_type.value for event in events],
        )
        self._simulations[simulation_id] = response
        return response

    def list_simulations(self) -> List[MockWhatsAppSimulationResponse]:
        return list(self._simulations.values())

    def _send_guardian_alert(
        self,
        *,
        request: MockWhatsAppInboundRequest,
        case_id: str,
        message_id: str | None,
    ) -> MockOutboundRecord:
        alert = self.adapter.send_guardian_alert(
            OutboundMessageRequest(
                provider=self.adapter.provider,
                to=request.guardian_address,
                body=(
                    f"Alerta simulado Guardian: {request.protected_person_alias} enviou "
                    f"uma mensagem suspeita. Caso {case_id} aguardando revisao."
                ),
                kind=OutboundMessageKind.GUARDIAN_ALERT,
                relatedCaseId=case_id,
                relatedMessageId=message_id,
                metadata={"guardian_alias": request.guardian_alias, "simulated": True},
            )
        )
        self.delivery_statuses.record_outbound(alert, updated_at=datetime.now(timezone.utc))
        delivered_callback = self.adapter.parse_status_callback(
            {
                "providerMessageId": alert.provider_message_id,
                "status": DeliveryStatus.DELIVERED.value,
                "timestamp": datetime.now(timezone.utc),
            }
        )
        delivered = self.delivery_statuses.update_from_callback(delivered_callback)
        case = self.event_model.repositories.cases.get(case_id)
        self.event_model.event_bus.publish_type(
            BotEventType.RESPONSIBLE_NOTIFIED,
            aggregate_type="case",
            aggregate_id=case_id,
            source="channel_adapter",
            case_id=case_id,
            protected_person_id=case.protected_person_id if case else None,
            payload={
                "provider": alert.provider.value,
                "provider_message_id": alert.provider_message_id,
                "guardian_alias": request.guardian_alias,
                "to": alert.to_address,
                "status": delivered.status.value,
                "simulated": True,
            },
        )
        self.event_model.event_bus.publish_type(
            BotEventType.DELIVERY_STATUS_UPDATED,
            aggregate_type="outbound_message",
            aggregate_id=alert.provider_message_id,
            payload={
                "provider": alert.provider.value,
                "provider_message_id": alert.provider_message_id,
                "status": delivered.status.value,
                "retryable": delivered.retryable,
                "simulated": True,
            },
        )
        return MockOutboundRecord(
            provider_message_id=alert.provider_message_id,
            to_address=alert.to_address,
            body=str(alert.raw.get("body", "")) if isinstance(alert.raw, dict) else "",
            kind=OutboundMessageKind.GUARDIAN_ALERT.value,
            status=delivered.status.value,
            simulated=alert.simulated,
            related_case_id=case_id,
        )
