from pydantic import BaseModel
from typing import List, Optional


class RecoveryRequest(BaseModel):
    paid: bool = False
    clicked_link: bool = False
    shared_documents: bool = False
    shared_password: bool = False
    installed_app: bool = False
    shared_sms_code: bool = False
    incident_type: Optional[str] = None
    already_paid: bool = False
    amount: Optional[float] = None
    payment_method: Optional[str] = None
    bank_name: Optional[str] = None
    has_shared_password: bool = False
    has_installed_remote_app: bool = False
    has_clicked_link: bool = False
    has_sent_code: bool = False
    source: str = "whatsapp"
    n8n_execution_id: Optional[str] = None
    case_id: Optional[str] = None


class RecoveryResponse(BaseModel):
    checklist: List[str] = []
    incident_type: Optional[str] = None
    summary: str = ""
    whatsapp_summary_message: str = ""
    immediate_steps: List[str] = []
    disclaimer: str = ""
    n8n_action: str = "start_recovery"
    case_id: Optional[str] = None
