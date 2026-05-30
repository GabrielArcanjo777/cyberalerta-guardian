from typing import List


class SafetyPolicyService:
    blocked_terms: List[str] = ["offensive", "hate", "violence", "phishing", "fraud"]

    def check_text(self, text: str) -> None:
        normalized = (text or "").lower()
        for term in self.blocked_terms:
            if term in normalized:
                raise ValueError("Request blocked by safety policy.")
