from typing import List, Optional

from pydantic import BaseModel, Field


class ProtectedResponseGenerateRequest(BaseModel):
    risk_level: str = Field(description="baixo | medio | alto | critico")
    category: str = Field(description="golpe_pix | link_suspeito | codigo_senha | falso_banco | risco_baixo | generico")
    signals: List[str] = Field(default_factory=list)
    trusted_contact_alias: Optional[str] = None


class ProtectedResponseGenerateResponse(BaseModel):
    short_reply: str
    tone: str = "calm_clear"
    do_not_do: List[str]
    next_step: str
