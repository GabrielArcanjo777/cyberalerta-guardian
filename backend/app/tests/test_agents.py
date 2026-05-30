from app.agents.trust_lock_agent import TrustLockAgent
from app.agents.trust_evidence_agent import TrustEvidenceAgent
from app.agents.recovery_agent import RecoveryAgent
from app.services.safety_policy import SafetyPolicyService


def test_trust_lock_agent_activates_on_high_risk():
    agent = TrustLockAgent()
    trust_lock = agent.analyze(85, "falso familiar pedindo Pix")
    assert trust_lock.activated is True
    assert "TRUST LOCK ATIVADO" in trust_lock.title
    assert "quarentena" in trust_lock.message.lower()


def test_trust_evidence_agent_returns_confidence_and_evidence():
    agent = TrustEvidenceAgent()
    evidence = agent.analyze("pix", ["vinculo familiar", "urgencia", "numero novo"])
    assert evidence.confidence == 94
    assert "Pedido de Pix" in evidence.evidence
    assert "Urgencia emocional" in evidence.evidence
    assert "Numero novo ou identidade nao verificada" in evidence.evidence


def test_recovery_agent_builds_conditional_checklist():
    agent = RecoveryAgent()
    response = agent.analyze(
        type("Req", (), {
            "paid": True,
            "clicked_link": True,
            "shared_documents": False,
            "shared_password": True,
            "installed_app": False,
            "shared_sms_code": False,
        })
    )
    assert "Contactar instituicao financeira imediatamente." in response.checklist
    assert any("Nao acesse o link novamente" in item for item in response.checklist)
    assert any("Altere senhas" in item for item in response.checklist)


def test_safety_policy_service_blocks_forbidden_terms():
    policy = SafetyPolicyService()
    policy.check_text("Esta mensagem e segura.")
    try:
        policy.check_text("Isso contem phishing e fraude.")
    except ValueError as exc:
        assert "blocked by safety policy" in str(exc)
    else:
        assert False, "SafetyPolicyService did not block forbidden text"
