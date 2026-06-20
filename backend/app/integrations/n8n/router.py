from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request, status

from app.core.request_context import get_n8n_execution_id, get_request_id
from app.core.security import check_rate_limit

from .schemas import N8nHealthResponse, N8nWhatsAppInboundRequest, N8nWhatsAppInboundResponse
from .security import require_n8n_webhook_secret
from .service import N8nIntegrationService, N8nMessageAlreadyProcessingError


def create_n8n_router(service: N8nIntegrationService) -> APIRouter:
    router = APIRouter(prefix="/integrations/n8n", tags=["integrations:n8n"])

    @router.get("/health", response_model=N8nHealthResponse)
    def n8n_health() -> N8nHealthResponse:
        return service.health()

    @router.post(
        "/whatsapp/inbound",
        response_model=N8nWhatsAppInboundResponse,
        dependencies=[Depends(require_n8n_webhook_secret)],
    )
    def n8n_whatsapp_inbound(
        payload: N8nWhatsAppInboundRequest,
        request: Request,
    ) -> N8nWhatsAppInboundResponse:
        check_rate_limit(request, bucket="n8n_whatsapp_inbound")
        try:
            return service.handle_whatsapp_inbound(
                payload,
                request_id=get_request_id(request),
                n8n_execution_id=get_n8n_execution_id(request),
            )
        except N8nMessageAlreadyProcessingError as exc:
            raise HTTPException(
                status_code=status.HTTP_409_CONFLICT,
                detail="Inbound message is already being processed.",
            ) from exc

    return router
