"""Evolution API instance client — QR pairing, connection state and reconnect.

Evolution API pairs a WhatsApp number the same way WhatsApp Web does: it exposes
a QR code that the user scans from their phone. This client wraps the small set
of Evolution instance endpoints needed to drive that flow from our own backend:

- ``GET  /instance/connectionState/{instance}`` — is the session open?
- ``GET  /instance/connect/{instance}``          — fetch the pairing QR code
- ``POST /instance/restart/{instance}``          — force a reconnect

PORTFOLIO / NON-OFFICIAL: Evolution API talks to WhatsApp Web via Baileys. It is
free and great for demos, but it is NOT the official WhatsApp Business API. The
number can be blocked by Meta and the session can drop and require re-pairing.
Do not treat this as production messaging.
"""

from __future__ import annotations

from typing import Any, Mapping, Protocol, Tuple

from pydantic import BaseModel

from app.channel_adapters.evolution_demo_adapter import EvolutionDemoConfig
from app.core.logging import get_logger

logger = get_logger("evolution_instance")

_DEFAULT_TIMEOUT = 10.0


class EvolutionConnectionState(BaseModel):
    """Normalized view of the Evolution instance status for the setup UI."""

    provider: str = "evolution"
    official: bool = False
    configured: bool
    instance: str | None = None
    state: str  # not_configured | unreachable | close | connecting | open
    connected: bool
    qr_base64: str | None = None
    pairing_code: str | None = None
    detail: str | None = None
    limitation_notice: str = (
        "Canal não-oficial (WhatsApp Web/Baileys). Risco de bloqueio do número e de "
        "queda de sessão exigindo novo pareamento. Uso de portfólio/demo, não produção."
    )


class EvolutionInstanceTransport(Protocol):
    def request(
        self, *, method: str, url: str, api_key: str, timeout: float
    ) -> Tuple[int, Mapping[str, Any]]: ...


class HttpxInstanceTransport:
    """Default transport using httpx. Kept behind a Protocol so tests inject a fake."""

    def request(
        self, *, method: str, url: str, api_key: str, timeout: float
    ) -> Tuple[int, Mapping[str, Any]]:
        import httpx

        response = httpx.request(method, url, headers={"apikey": api_key}, timeout=timeout)
        try:
            data = response.json()
        except Exception:
            data = {}
        return response.status_code, data if isinstance(data, Mapping) else {"raw": data}


def _parse_state(data: Mapping[str, Any]) -> str:
    instance = data.get("instance")
    if isinstance(instance, Mapping) and instance.get("state"):
        return str(instance["state"]).strip().lower()
    if data.get("state"):
        return str(data["state"]).strip().lower()
    return "unknown"


class EvolutionInstanceClient:
    def __init__(
        self,
        config: EvolutionDemoConfig | None = None,
        *,
        transport: EvolutionInstanceTransport | None = None,
        timeout: float = _DEFAULT_TIMEOUT,
    ) -> None:
        self._cfg = config or EvolutionDemoConfig.from_env()
        self._transport = transport or HttpxInstanceTransport()
        self._timeout = timeout

    def _url(self, path: str) -> str:
        return f"{str(self._cfg.api_url).rstrip('/')}{path}"

    def _not_configured(self) -> EvolutionConnectionState:
        return EvolutionConnectionState(
            configured=False,
            instance=self._cfg.instance_name,
            state="not_configured",
            connected=False,
            detail="Configure EVOLUTION_API_URL, EVOLUTION_API_KEY e EVOLUTION_INSTANCE_NAME no .env.",
        )

    def _call(self, method: str, path: str) -> Tuple[int, Mapping[str, Any]] | None:
        try:
            return self._transport.request(
                method=method,
                url=self._url(path),
                api_key=str(self._cfg.api_key),
                timeout=self._timeout,
            )
        except Exception as exc:  # connection refused, timeout, DNS, etc.
            logger.warning("Evolution instance request failed: %s", exc.__class__.__name__)
            return None

    def connection_state(self) -> EvolutionConnectionState:
        if not self._cfg.can_send:
            return self._not_configured()
        result = self._call("GET", f"/instance/connectionState/{self._cfg.instance_name}")
        if result is None:
            return EvolutionConnectionState(
                configured=True,
                instance=self._cfg.instance_name,
                state="unreachable",
                connected=False,
                detail="Evolution API não respondeu. Confirme se o serviço está no ar (Docker).",
            )
        _, data = result
        state = _parse_state(data)
        return EvolutionConnectionState(
            configured=True,
            instance=self._cfg.instance_name,
            state=state,
            connected=state == "open",
        )

    def get_qr(self) -> EvolutionConnectionState:
        base = self.connection_state()
        if not base.configured or base.connected or base.state == "unreachable":
            return base
        result = self._call("GET", f"/instance/connect/{self._cfg.instance_name}")
        if result is None:
            return base.model_copy(update={"state": "unreachable"})
        _, data = result
        qrcode = data.get("qrcode") if isinstance(data.get("qrcode"), Mapping) else {}
        qr_base64 = data.get("base64") or (qrcode or {}).get("base64")
        pairing_code = data.get("pairingCode") or (qrcode or {}).get("pairingCode") or data.get("code")
        return EvolutionConnectionState(
            configured=True,
            instance=self._cfg.instance_name,
            state="connecting",
            connected=False,
            qr_base64=qr_base64,
            pairing_code=pairing_code,
            detail="Abra o WhatsApp > Aparelhos conectados > Conectar aparelho e escaneie o QR.",
        )

    def reconnect(self) -> EvolutionConnectionState:
        """Force a reconnect (restart), then return the fresh QR/status."""
        if not self._cfg.can_send:
            return self._not_configured()
        self._call("POST", f"/instance/restart/{self._cfg.instance_name}")
        return self.get_qr()

    def ensure_connected(self) -> EvolutionConnectionState:
        """Health-check helper: reconnect automatically if the session dropped."""
        state = self.connection_state()
        if state.configured and state.state in {"close", "unreachable"}:
            logger.info("Evolution session '%s' is %s — attempting reconnect.", state.instance, state.state)
            return self.reconnect()
        return state
