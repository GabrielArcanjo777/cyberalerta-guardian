from typing import List, Optional

from pydantic import BaseModel, Field


class RecoveryRequest(BaseModel):
    paid: bool = False
    clicked_link: bool = False
    shared_documents: bool = False
    shared_password: bool = False
    installed_app: bool = False
    shared_sms_code: bool = False
    incident_type: Optional[str] = Field(default=None, max_length=80)
    already_paid: Optional[bool] = None
    amount: Optional[float] = Field(default=None, ge=0)
    payment_method: Optional[str] = Field(default=None, max_length=80)
    bank_name: Optional[str] = Field(default=None, max_length=120)
    has_shared_password: Optional[bool] = None
    has_installed_remote_app: Optional[bool] = None
    has_clicked_link: Optional[bool] = None
    has_sent_code: Optional[bool] = None
    source: Optional[str] = Field(default=None, max_length=120)
    n8n_execution_id: Optional[str] = Field(default=None, max_length=180)
    case_id: Optional[str] = Field(default=None, max_length=180)


class RecoveryPlanStep(BaseModel):
    priority: str
    title: str
    description: str
    category: str


class RecoveryResponse(BaseModel):
    checklist: List[str]
    incident_type: str
    severity: str
    summary: str
    immediate_steps: List[str]
    next_24h_steps: List[str]
    evidence_to_collect: List[str]
    contacts_to_notify: List[str]
    do_not_do: List[str]
    whatsapp_summary_message: str
    whatsapp_step_messages: List[str]
    trusted_contact_message: str
    report_summary: str
    disclaimer: str
    n8n_action: str
    case_id: Optional[str] = None
    n8n_execution_id: Optional[str] = None
    recovery_plan: List[RecoveryPlanStep]
    evidence_to_save: List[str]
    accounts_to_secure: List[str]
    what_not_to_do: List[str]
