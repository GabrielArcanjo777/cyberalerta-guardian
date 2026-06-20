import json
import logging

from app.core.logging import get_logger, structured_log
from app.core.masking import mask_mapping, mask_message, mask_phone, mask_secret
from app.core.request_context import build_n8n_execution_id, build_request_id


def test_request_context_sanitizes_headers_and_generates_request_id():
    assert build_request_id("req-ok-123") == "req-ok-123"
    assert build_request_id("req\r\nbad") == "req--bad"
    assert build_request_id().startswith("req-")
    assert build_n8n_execution_id("exec\r\nbad") == "exec--bad"


def test_masking_never_returns_full_sensitive_values():
    phone = "+55 11 99999-0001"
    message = "Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora."
    secret = "super-secret-token"

    masked_phone = mask_phone(phone)
    masked_message = mask_message(message)
    masked_secret = mask_secret(secret)

    assert phone not in masked_phone
    assert "99999" not in masked_phone
    assert masked_phone.startswith("[phone:")
    assert message not in masked_message
    assert "sha256:" in masked_message
    assert secret not in masked_secret
    assert masked_secret.startswith("[secret:")


def test_mask_mapping_masks_nested_sensitive_fields():
    payload = {
        "from": "+5511999990001",
        "body": "Mensagem completa que nao deve aparecer inteira no log",
        "token": "real-token-value",
        "nested": {"phone_number": "+5511888887777", "message": "Outro texto sensivel"},
    }

    masked = mask_mapping(payload)
    serialized = json.dumps(masked)

    assert "+5511999990001" not in serialized
    assert "+5511888887777" not in serialized
    assert "real-token-value" not in serialized
    assert "Mensagem completa que nao deve aparecer inteira no log" not in serialized
    assert "Outro texto sensivel" not in serialized


def test_structured_log_outputs_json_with_masked_metadata(caplog):
    logger = get_logger("test_observability")
    caplog.set_level(logging.INFO, logger=logger.name)

    structured_log(
        logger,
        "observability_test",
        request_id="req-observability-1",
        n8n_execution_id="exec-observability-1",
        from_number="+5511999990001",
        message="Mensagem completa que nao deve aparecer inteira no log",
        provided_secret="secret-value",
    )

    record = caplog.records[-1]
    payload = json.loads(record.getMessage())
    serialized = json.dumps(payload)

    assert payload["event"] == "observability_test"
    assert payload["request_id"] == "req-observability-1"
    assert payload["n8n_execution_id"] == "exec-observability-1"
    assert "+5511999990001" not in serialized
    assert "Mensagem completa que nao deve aparecer inteira no log" not in serialized
    assert "secret-value" not in serialized
