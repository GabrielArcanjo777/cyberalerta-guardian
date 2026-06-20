from fastapi.testclient import TestClient

from app.repositories import (
    AuditEventRecord,
    InMemoryOperationalStateRepository,
    InboundMessageRecord,
    InboundProcessingStatus,
    StateCase,
    get_operational_state_repository,
    message_preview,
    stable_hash,
)
from main import app

client = TestClient(app)


def test_memory_repository_saves_case_and_audit_event():
    repository = InMemoryOperationalStateRepository()

    case = repository.cases.save(
        StateCase(
            case_id="case-memory-1",
            user_name="Maria",
            channel="whatsapp",
            risk_score=88,
            risk_level="high",
            n8n_action="reply_and_alert_guardian",
            ruleset_version="ruleset-test",
            risk_engine_version="risk-test",
        )
    )
    event = repository.audit_events.append(
        AuditEventRecord(
            case_id=case.case_id,
            request_id="req-memory-1",
            n8n_execution_id="exec-memory-1",
            event_type="N8NInboundProcessed",
            metadata={"risk_score": case.risk_score},
        )
    )

    assert repository.cases.get("case-memory-1") == case
    assert repository.cases.list_all()[0].case_id == "case-memory-1"
    assert repository.audit_events.list_by_case(case.case_id)[0] == event


def test_memory_repository_reserves_inbound_message_idempotently():
    repository = InMemoryOperationalStateRepository()
    record = InboundMessageRecord(
        message_id="msg-memory-1",
        channel="whatsapp",
        from_number_hash=stable_hash("+5511999990001"),
        message_hash=stable_hash("Mensagem suspeita com Pix urgente"),
        message_preview=message_preview("Mensagem suspeita com Pix urgente"),
        n8n_execution_id="exec-memory-1",
    )

    first, first_reserved = repository.inbound_messages.reserve(record)
    second, second_reserved = repository.inbound_messages.reserve(record)

    assert first_reserved is True
    assert first.processing_status == InboundProcessingStatus.PROCESSING
    assert second_reserved is False
    assert second.message_id == first.message_id
    assert second.from_number_hash == stable_hash("+5511999990001")
    assert "+5511999990001" not in second.from_number_hash


def test_memory_repository_marks_inbound_message_processed_with_last_response():
    repository = InMemoryOperationalStateRepository()
    record = InboundMessageRecord(
        message_id="msg-memory-processed",
        channel="whatsapp",
        from_number_hash=stable_hash("masked-contact"),
        message_hash=stable_hash("Pix urgente"),
        message_preview=message_preview("Pix urgente"),
    )

    repository.inbound_messages.reserve(record)
    processed = repository.inbound_messages.mark_processed(
        "msg-memory-processed",
        case_id="case-memory-processed",
        response_json={"case_id": "case-memory-processed", "risk_score": 90},
    )

    assert processed.processing_status == InboundProcessingStatus.PROCESSED
    assert processed.case_id == "case-memory-processed"
    assert processed.last_response_json == {"case_id": "case-memory-processed", "risk_score": 90}


def test_privacy_helpers_hash_phone_and_store_short_preview():
    phone_hash = stable_hash("+5511999990001")
    preview = message_preview("Pix urgente " * 30)

    assert len(phone_hash) == 64
    assert "+5511999990001" not in phone_hash
    assert len(preview) <= 120
    assert len(preview) < len("Pix urgente " * 30)


def test_n8n_endpoint_uses_memory_idempotency_and_returns_previous_response():
    message_id = "n8n-memory-idempotent-1"
    payload = {
        "message_id": message_id,
        "from": "+5511999990001",
        "to": "sandbox-number",
        "body": "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.",
        "channel": "whatsapp",
        "provider": "webhook_test",
        "protected_person_alias": "Maria",
        "guardian_alias": "Gabriel",
        "guardian_address": "guardian-masked",
        "dry_run": True,
    }

    first = client.post(
        "/integrations/n8n/whatsapp/inbound",
        json=payload,
        headers={"X-Request-ID": "req-memory-n8n-1", "X-N8N-Execution-ID": "exec-memory-n8n-1"},
    )
    second = client.post(
        "/integrations/n8n/whatsapp/inbound",
        json={**payload, "body": "Mensagem duplicada que nao deve reprocessar"},
        headers={"X-Request-ID": "req-memory-n8n-2", "X-N8N-Execution-ID": "exec-memory-n8n-2"},
    )

    assert first.status_code == 200
    assert second.status_code == 200
    assert second.json() == first.json()

    stored = get_operational_state_repository().inbound_messages.get(message_id)
    assert stored is not None
    assert stored.processing_status == InboundProcessingStatus.PROCESSED
    assert stored.case_id == first.json()["case_id"]
    assert stored.last_response_json == first.json()
    assert stored.from_number_hash != "+5511999990001"
    assert "+5511999990001" not in stored.message_preview
