from typing import List
from app.services.scoring_rules import compute_score, determine_level


class RiskScoringAgent:
    def analyze(self, action_type: str, manipulations: List[str], channel: str, already_acted: bool) -> int:
        return compute_score(action_type, manipulations, channel, already_acted)

    def determine_level(self, score: int) -> str:
        return determine_level(score)
