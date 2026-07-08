export type UserRole = 'admin' | 'analyst' | 'viewer'

export type AuthUser = {
  id: string
  email: string
  full_name: string
  role: UserRole
  is_active: boolean
  is_admin: boolean
  mfa_enabled: boolean
}

export type LoginPayload = {
  email: string
  password: string
}

export type RegisterPayload = {
  email: string
  full_name: string
  password: string
}

export type LoginResponse = {
  authenticated: boolean
  mfa_required: boolean
  temporary_token?: string | null
  mfa_setup_required?: boolean
  user?: AuthUser | null
}

export type GoogleAuthStatusResponse = {
  enabled: boolean
  configured: boolean
  auto_create_users: boolean
  redirect_uri: string
}

export type MeResponse = {
  authenticated: boolean
  user?: AuthUser | null
}

export type MFASetupResponse = {
  otpauth_uri: string
  qr_code_base64: string
  manual_secret: string
}

export type MFAStatusResponse = {
  status: string
  mfa_enabled: boolean
}

export type RecoveryCodesResponse = {
  status: string
  mfa_enabled: boolean
  recovery_codes: string[]
}

export type AuthAuditLog = {
  id: string
  user_id?: string | null
  email?: string | null
  event_type: string
  ip_address?: string | null
  user_agent?: string | null
  success: boolean
  reason?: string | null
  created_at: string
}

export type AdminUsersResponse = {
  users: AuthUser[]
}

export type AdminAuditLogsResponse = {
  logs: AuthAuditLog[]
}

export type SimpleChannelSubmitPayload = {
  protected_person_alias: string
  channel: 'whatsapp_mock'
  content_type: 'text'
  content: string
  consent: boolean
  trusted_contact_alias?: string
}

export type ProtectedResponseGeneratePayload = {
  risk_level: string
  category: string
  signals: string[]
  trusted_contact_alias?: string
}

export type ProtectedResponseGenerateResponse = {
  short_reply: string
  tone: string
  do_not_do: string[]
  next_step: string
  __mock?: boolean
}

export type SimpleChannelSubmitResponse = {
  channel_case_id: string
  risk_level: string
  simple_reply: string
  admin_case_created: boolean
  trust_lock_recommended: boolean
  __mock?: boolean
}

export type AdminCaseTraceStep = {
  step: string
  detail: string
}

export type AdminCaseStatus =
  | 'open'
  | 'reviewing'
  | 'verified_safe'
  | 'confirmed_scam'
  | 'resolved'
  | 'recovery_needed'

export type AdminCase = {
  case_id: string
  protected_person_alias: string
  guardian_alias: string
  source_channel: string
  received_content_summary: string
  risk_score: number
  risk_level: string
  scam_category: string
  detected_signals: string[]
  agent_decision: string
  agent_decision_trace: AdminCaseTraceStep[]
  trust_lock_status: string
  trusted_circle_status: string
  proof_of_trust_status: string
  recovery_status: string
  recommended_action: string
  protected_person_short_reply?: string
  status: AdminCaseStatus
  created_at: string
  updated_at: string
}

export type GuardianConsoleStatusResponse = {
  service: string
  mode: string
  storage: string
  case_count: number
  auth_enabled: boolean
  notifications_enabled: boolean
  demo_note: string
  __mock?: boolean
}

export type AdminCaseListResponse = {
  cases: AdminCase[]
  total: number
  __mock?: boolean
}

export type GuardianConsoleBotState = {
  name: string
  active: boolean
  provider: string
  mode: string
  last_event?: string | null
}

export type GuardianConsoleActivationState = {
  protected_bot: GuardianConsoleBotState
  responsible_bot: GuardianConsoleBotState
  channel_provider: string
  backend_state: string
  simulated: boolean
}

export type GuardianConsoleTimelineEvent = {
  event_id: string
  event_type: string
  label: string
  description: string
  aggregate_type: string
  aggregate_id: string
  occurred_at: string
  status?: string | null
  metadata: Record<string, unknown>
}

export type GuardianConsoleDeliveryView = {
  protected_reply_status?: string | null
  guardian_alert_status?: string | null
  guardian_notified: boolean
  latest_provider_message_id?: string | null
}

export type GuardianConsoleOutboundView = {
  provider_message_id?: string | null
  kind: string
  to_label: string
  body: string
  status?: string | null
  simulated: boolean
}

export type GuardianConsolePatternView = {
  score: number
  level: string
  threat_type: string
  threat_type_label: string
  explanation: string
  reasons: string[]
  recommendation: string
  signals: string[]
  cluster_ids: string[]
  recurrence: Record<string, number>
  similar_message_ids: string[]
  normalized_text_sha1: string
  text_fingerprint: string
  candidate_id?: string | null
  feedback_label?: string | null
}

export type GuardianConsoleProtectedPersonView = {
  protected_person_id: string
  alias: string
  status: string
  created_at: string
  updated_at: string
}

export type GuardianConsoleResponsibleContactView = {
  guardian_id?: string | null
  alias?: string | null
  status?: string | null
  notified: boolean
  last_delivery_status?: string | null
  address_label?: string | null
}

export type GuardianConsoleCaseStateView = {
  case_id: string
  status: string
  source_message_id: string
  risk_assessment_id: string
  open: boolean
  created_at: string
  updated_at: string
}

export type GuardianConsoleMessageView = {
  message_id: string
  provider_message_id?: string | null
  direction: string
  channel: string
  body: string
  summary: string
  status: string
  simulated: boolean
  created_at: string
}

export type GuardianConsoleRiskAssessmentView = {
  risk_assessment_id: string
  score: number
  risk_level: string
  signals: string[]
  explanation: string[]
  case_threshold_reached: boolean
  threshold_label: string
  created_at: string
}

export type GuardianConsoleChannelStatusView = {
  provider: string
  mode: string
  simulated: boolean
  backend_state: string
  protected_bot_active: boolean
  responsible_bot_active: boolean
  protected_reply_status?: string | null
  guardian_alert_status?: string | null
  guardian_notified: boolean
  latest_provider_message_id?: string | null
  environment_label: string
}

export type GuardianConsoleFeedbackView = {
  available_actions: string[]
  latest_action?: string | null
  latest_actor?: string | null
  latest_note?: string | null
  latest_event_id?: string | null
  latest_event_at?: string | null
  guardian_confirmed: boolean
  false_positive: boolean
  resolved: boolean
}

export type GuardianConsoleAuditLogView = {
  audit_log_id: string
  event_id?: string | null
  actor?: string | null
  action: string
  target_type: string
  target_id: string
  payload: Record<string, unknown>
  created_at: string
}

export type GuardianConsoleAgentDecisionView = {
  event_id: string
  agent: string
  summary: string
  recommended_action: string
  fallback_used: boolean
  guardrails: string[]
  occurred_at: string
}

export type GuardianConsoleConsentView = {
  consent_id: string
  status: string
  bot_active: boolean
  scopes: string[]
  accepted_at?: string | null
  revoked_at?: string | null
  retention_message_body_days: number
  retention_event_audit_days: number
  delete_after_revocation_days: number
  latest_event?: string | null
  limitation_notice: string
}

export type GuardianConsoleRealCaseSummary = {
  case_id: string
  status: string
  protected_person_alias: string
  guardian_alias?: string | null
  source_channel: string
  risk_score: number
  risk_level: string
  risk_signals: string[]
  pattern_score?: number | null
  pattern_level?: string | null
  message_summary: string
  recommended_action: string
  alert_delivered: boolean
  guardian_confirmed: boolean
  false_positive: boolean
  resolved: boolean
  created_at: string
  updated_at: string
}

export type GuardianConsoleRealCaseDetail = GuardianConsoleRealCaseSummary & {
  source_message: string
  activation: GuardianConsoleActivationState
  delivery: GuardianConsoleDeliveryView
  protected_reply: GuardianConsoleOutboundView
  guardian_alert: GuardianConsoleOutboundView
  protected_person: GuardianConsoleProtectedPersonView
  responsible_contact: GuardianConsoleResponsibleContactView
  case: GuardianConsoleCaseStateView
  message: GuardianConsoleMessageView
  risk_assessment: GuardianConsoleRiskAssessmentView
  channel_status: GuardianConsoleChannelStatusView
  feedback: GuardianConsoleFeedbackView
  audit_log: GuardianConsoleAuditLogView[]
  bot_events: GuardianConsoleTimelineEvent[]
  agent_decisions: GuardianConsoleAgentDecisionView[]
  consent: GuardianConsoleConsentView
  environment_label: string
  next_step: string
  pattern?: GuardianConsolePatternView | null
  timeline: GuardianConsoleTimelineEvent[]
  feedback_actions: string[]
}

export type GuardianConsoleRealStatusResponse = {
  service: string
  mode: string
  storage: string
  channel_provider: string
  case_count: number
  open_case_count: number
  protected_people_count: number
  guardians_count: number
  delivery_status_available: boolean
  activation: GuardianConsoleActivationState
  consent: GuardianConsoleConsentView
  demo_note: string
}

export type GuardianConsoleRealCaseListResponse = {
  cases: GuardianConsoleRealCaseSummary[]
  total: number
}

export type GuardianFeedbackAction =
  | 'confirm_scam'
  | 'false_alarm'
  | 'needs_review'
  | 'mark_resolved'

export type GuardianFeedbackPayload = {
  action: GuardianFeedbackAction
  guardian_alias?: string
  note?: string
}

export type GuardianFeedbackResponse = {
  case_id: string
  action: GuardianFeedbackAction
  previous_status: string
  new_status: string
  event_id: string
  audit_event: string
}

export type DualBotInboundPayload = {
  providerMessageId?: string
  from?: string
  to?: string
  body: string
  protected_person_alias?: string
  guardian_alias?: string
  guardian_address?: string
  language?: string
}

export type DualBotFlowResponse = {
  provider: string
  duplicate: boolean
  provider_message_id: string
  message_id?: string | null
  risk_assessment_id?: string | null
  risk_score?: number | null
  risk_level?: string | null
  risk_signals: string[]
  case_id?: string | null
  case_created: boolean
  protected_reply?: GuardianConsoleOutboundView | null
  guardian_alert?: GuardianConsoleOutboundView | null
  events: string[]
}

export type ConsentScope =
  | 'protected_bot'
  | 'responsible_alerts'
  | 'pattern_analysis'
  | 'case_history'
  | 'demo_channel'

export type ConsentRecord = {
  consent_id: string
  protected_person_id: string
  protected_person_alias: string
  guardian_id?: string | null
  guardian_alias?: string | null
  channel_provider: string
  status: string
  scopes: ConsentScope[]
  bot_active: boolean
  accepted_at?: string | null
  revoked_at?: string | null
  created_at: string
  updated_at: string
  retention_policy: {
    policy_id: string
    message_body_days: number
    event_audit_days: number
    delete_after_revocation_days: number
    minimal_storage: boolean
    policy_note: string
  }
  legal_basis: string
  limitation_notice: string
}

export type ConsentEvent = {
  consent_event_id: string
  consent_id: string
  event_type: string
  actor: string
  scopes: ConsentScope[]
  reason?: string | null
  occurred_at: string
}

export type ConsentStatusResponse = {
  record: ConsentRecord
  latest_event?: ConsentEvent | null
  events: ConsentEvent[]
  can_activate_bot: boolean
  production_whatsapp_enabled: boolean
  demo_notice: string
}

export type ConsentAcceptPayload = {
  protected_person_id?: string
  protected_person_alias?: string
  guardian_id?: string | null
  guardian_alias?: string | null
  channel_provider?: string
  scopes?: ConsentScope[]
  actor?: string
  reason?: string | null
}

export type ConsentActionPayload = {
  protected_person_id?: string
  actor?: string
  reason?: string | null
}

export type TrustedCircleEscalatePayload = {
  case_id: string
  risk_level: string
  protected_person_alias: string
  trusted_contacts: string[]
  reason: string
}

export type TrustedCircleEscalateResponse = {
  escalation_id: string
  status: 'simulated_notified' | 'review_suggested' | 'not_escalated'
  message_to_guardian: string
  trusted_contacts: string[]
  proof_of_trust_recommended: boolean
  sent_real_notification: boolean
  demo_note: string
  case_id?: string
  risk_level?: string
  escalation_recommended?: boolean
  __mock?: boolean
}

export type TrustedCircleStatusResponse = {
  service: string
  mode: string
  real_notifications_enabled: boolean
  escalation_count: number
  demo_note: string
  __mock?: boolean
}

export type ProofTrustStepItem = {
  id: string
  title: string
  status: 'pending' | 'completed' | 'skipped'
  guidance?: string
  note?: string
}

export type AssistedProofFinalDecision =
  | 'verified_safe'
  | 'confirmed_scam'
  | 'inconclusive'
  | 'blocked'

export type AssistedProofSessionStatus =
  | 'not_started'
  | 'in_progress'
  | 'verified_safe'
  | 'confirmed_scam'
  | 'inconclusive'
  | 'blocked'

export type AssistedProofSessionCreatePayload = {
  case_id: string
  protected_person_alias: string
  guardian_alias: string
  risk_level: string
  suspected_request: string
  trusted_contact_alias: string
}

export type AssistedProofStepUpdatePayload = {
  step_id: string
  status?: 'pending' | 'completed' | 'skipped'
  note?: string
  final_decision?: AssistedProofFinalDecision
}

export type AssistedProofSessionResponse = {
  session_id: string
  case_id: string
  status: AssistedProofSessionStatus
  current_step: string
  steps: ProofTrustStepItem[]
  final_decision: AssistedProofFinalDecision | null
  guardian_note?: string | null
  protected_person_alias?: string
  guardian_alias?: string
  trusted_contact_alias?: string
  suspected_request?: string
  demo_note: string
  __mock?: boolean
}

export type TrustedCircleEscalationRecord = {
  escalation_id: string
  case_id: string
  risk_level: string
  protected_person_alias: string
  trusted_contacts: string[]
  reason: string
  status: TrustedCircleEscalateResponse['status']
  message_to_guardian: string
  proof_of_trust_recommended: boolean
  sent_real_notification: boolean
  created_at: string
}

export type SimpleChannelStatusResponse = {
  service: string
  mode: string
  channels: string[]
  whatsapp_real_enabled: boolean
  monitoring_enabled: boolean
  privacy_note: string
  demo_note: string
  __mock?: boolean
}

export type AnalyzePayload = {
  user_name:string
  age_group:string
  trusted_contact_name:string
  trusted_contact_relation:string
  action_type:string
  channel:string
  message:string
  already_acted:boolean
}

export type AgentDecisionTraceItem = {
  agent:string
  input_summary:string
  decision:string
  confidence:number
  evidence:string[]
  next_action:string
}

export type DecisionLedger = {
  final_decision:string
  decision_reason:string
  safety_level:string
  escalation_required:boolean
  audit_summary:string
}

export type AIMode = {
  use_llm:boolean
  provider:string
  fallback_enabled:boolean
  safety_policy:string
  llm_enrichment_applied:boolean
}

export type MLAnalysis = {
  classe:string
  confianca:number
  categoria:string
  risco:string
  score:number
  sinais_detectados:string[]
  explicacao:string
  ml_used:boolean
  rules_used:boolean
  url_analysis_used?:boolean
  __mock?:boolean
}

export type BrandImpersonation = {
  brand_impersonation_detected:boolean
  brand:string | null
  message:string
  matched_term?:string | null
}

export type UrlAnalysis = {
  url:string
  risco:string
  score:number
  categoria:string
  sinais_detectados:string[]
  brand_impersonation:BrandImpersonation
  explicacao:string
  rules_used:boolean
  external_api_used:boolean
  __mock?:boolean
}

export type TrustedCircleAlert = {
  should_alert:boolean
  contact_name:string
  relationship:string
  urgency:string
  person_at_risk:string
  risk_summary:string
  scam_type:string
  recommended_action:string
  suggested_message:string
  status:string
  is_simulated:boolean
  message:string
}

export type TrustLock = {
  activated:boolean
  title:string
  reason:string
  message:string
}

export type InterventionPlaybook = {
  immediate_action:string
  verification:string
  family_escalation:string
  recovery_fallback:string
}

export type GuardianReport = {
  title:string
  summary:string
  agent_decision:string
  recommended_next_step:string
}

export type TrustEvidence = {
  confidence:number
  evidence:string[]
}

export type AnalyzeResponse = {
  risk_score:number
  risk_level:string
  dangerous_action:string
  scam_type:string
  scam_stage:string
  manipulations:string[]
  trust_evidence:TrustEvidence
  agent_decision_trace:AgentDecisionTraceItem[]
  decision_ledger:DecisionLedger
  ai_mode:AIMode
  ml_analysis:MLAnalysis
  url_analysis:UrlAnalysis | null
  trust_lock:TrustLock
  proof_of_trust:string[]
  intervention_playbook:InterventionPlaybook
  trusted_circle_alert:TrustedCircleAlert
  user_message:string
  report:GuardianReport
  __mock?:boolean
}

export type RecoveryPayload = {
  paid:boolean
  clicked_link:boolean
  shared_documents:boolean
  shared_password:boolean
  installed_app:boolean
  shared_sms_code:boolean
}

export type RecoveryPlanStep = {
  priority:string
  title:string
  description:string
  category:string
}

export type RecoveryResponse = {
  severity:string
  summary:string
  recovery_plan:RecoveryPlanStep[]
  evidence_to_save:string[]
  accounts_to_secure:string[]
  what_not_to_do:string[]
  disclaimer:string
  __mock?:boolean
}

export type IntakeChannel =
  | 'manual_text'
  | 'screenshot_upload'
  | 'email_forward'
  | 'browser_extension'
  | 'share_sheet'
  | 'whatsapp_business_opt_in'
  | 'microsoft_graph_opt_in'

export type IntakePayload = {
  channel:IntakeChannel
  content:string
  user_consent:boolean
  contains_sensitive_data:boolean
  redaction_requested:boolean
  metadata_minimal:boolean
  user_name:string
  trusted_contact_name:string
  action_type:string
}

export type RedactPreviewPayload = {
  content:string
}

export type RedactPreviewResponse = {
  original_length:number
  redacted_content:string
  items_masked:string[]
  __mock?:boolean
}

export type PrivacyReport = {
  consent_verified:boolean
  redaction_applied:boolean
  channel:IntakeChannel
  data_minimization:boolean
  sensitive_items_masked:string[]
  monitoring:boolean
  message:string
}

export type IntakeAnalysisResponse = {
  analysis:AnalyzeResponse
  privacy_report:PrivacyReport
  redacted_content:string
  __mock?:boolean
}

export type ConnectorResult = {
  provider:string
  status:string
  risk_signals:string[]
  raw_summary:string
  safe_to_display:boolean
  privacy_note:string
  confidence:number
  metadata:Record<string,unknown>
  __mock?:boolean
}

export type ConnectorStatus = {
  name:string
  provider:string
  mode:string
  enabled:boolean
  privacy:string
}

export type OCRPreviewResponse = {
  provider:string
  status:string
  extracted_text:string
  risk_signals:string[]
  raw_summary:string
  safe_to_display:boolean
  privacy_note:string
  confidence:number
  metadata:Record<string,unknown>
  __mock?:boolean
}

export type EvolutionConnectionState = {
  provider:string
  official:boolean
  configured:boolean
  instance:string|null
  state:'not_configured'|'unreachable'|'close'|'connecting'|'open'|'unknown'
  connected:boolean
  qr_base64:string|null
  pairing_code:string|null
  detail:string|null
  limitation_notice:string
}
