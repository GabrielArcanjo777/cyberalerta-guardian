from app.services.risk_signal_detector import RiskSignalDetector
from app.services.text_normalization import normalize_text, tokenize_text


def _codes(text: str, **kwargs) -> set[str]:
    return {signal.code for signal in RiskSignalDetector().detect(text, **kwargs)}


def _by_code(text: str, **kwargs) -> dict[str, str]:
    return {signal.code: signal.category for signal in RiskSignalDetector().detect(text, **kwargs)}


def test_text_normalization_removes_accents_and_collapses_spaces():
    assert normalize_text("  Mãe,  PIX   urgente!  ") == "mae, pix urgente!"
    assert tokenize_text("Código SMS: 123") == ["codigo", "sms", "123"]


def test_detects_false_relative_pix_critical_signals():
    codes = _codes("Mae, troquei de numero. Preciso de Pix urgente. Nao liga agora.")

    assert {"false_relative", "new_number", "pix_or_payment", "urgency", "do_not_call"} <= codes


def test_detects_fake_bank_link_and_credential_request():
    categories = _by_code(
        "Central do banco: acesse https://seguranca-conta.xyz e informe o codigo SMS para desbloquear."
    )

    assert categories["fake_bank"] == "impersonation"
    assert categories["suspicious_link"] == "suspicious_link"
    assert categories["sms_token"] == "credential_request"


def test_detects_sms_token_without_link():
    codes = _codes("Me envia o codigo SMS que chegou no seu celular para validar agora.")

    assert "sms_token" in codes
    assert "urgency" in codes


def test_detects_remote_support_access():
    categories = _by_code("Sou do suporte. Instale o app AnyDesk para eu fazer acesso remoto.")

    assert categories["fake_bank"] == "impersonation"
    assert categories["remote_access"] == "remote_access"


def test_detects_job_fee():
    categories = _by_code("Para liberar a vaga de emprego, voce precisa pagar uma taxa hoje.")

    assert categories["job_fee"] == "job_fee"
    assert categories["urgency"] == "urgency"


def test_low_risk_message_has_no_main_risk_signals():
    signals = RiskSignalDetector().detect("Oi, tudo bem? Vamos almocar domingo?")

    assert signals == []


def test_already_acted_adds_status_signal():
    categories = _by_code("Cliquei no link e enviei o codigo.", already_acted=True)

    assert categories["already_acted"] == "already_acted"
    assert categories["sms_token"] == "credential_request"


def test_action_type_adds_signal_without_text_keyword():
    categories = _by_code("Pode fazer isso para mim?", action_type="pix")

    assert categories["pix_or_payment"] == "financial_request"
