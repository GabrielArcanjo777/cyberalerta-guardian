from app.agents.risk_scoring_agent import RiskScoringAgent


def test_risk_scoring_agent_calculates_critical_score():
    agent = RiskScoringAgent()
    manipulations = ["vinculo familiar", "urgencia", "numero novo", "pedido para nao ligar"]
    score = agent.analyze("pix", manipulations, "whatsapp", False)
    level = agent.determine_level(score)
    assert score >= 81
    assert level == "critical"
