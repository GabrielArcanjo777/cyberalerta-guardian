from app.schemas.recovery import RecoveryRequest, RecoveryResponse
from app.services.recovery_playbooks import build_recovery_response


class RecoveryAgent:
    def analyze(self, request: RecoveryRequest) -> RecoveryResponse:
        normalized = request if isinstance(request, RecoveryRequest) else self._legacy_request(request)
        return build_recovery_response(normalized)

    def _legacy_request(self, request) -> RecoveryRequest:
        return RecoveryRequest(
            paid=bool(getattr(request, "paid", False)),
            clicked_link=bool(getattr(request, "clicked_link", False)),
            shared_documents=bool(getattr(request, "shared_documents", False)),
            shared_password=bool(getattr(request, "shared_password", False)),
            installed_app=bool(getattr(request, "installed_app", False)),
            shared_sms_code=bool(getattr(request, "shared_sms_code", False)),
        )
