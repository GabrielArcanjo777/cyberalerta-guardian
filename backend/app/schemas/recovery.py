from pydantic import BaseModel
from typing import List


class RecoveryRequest(BaseModel):
    paid: bool
    clicked_link: bool
    shared_documents: bool
    shared_password: bool
    installed_app: bool
    shared_sms_code: bool


class RecoveryResponse(BaseModel):
    checklist: List[str]
