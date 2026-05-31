export type SimpleChannelSubmitPayload = {
  protected_person_alias: string
  channel: 'whatsapp_mock'
  content_type: 'text'
  content: string
  consent: boolean
}

export type SimpleChannelSubmitResponse = {
  channel_case_id: string
  risk_level: string
  simple_reply: string
  admin_case_created: boolean
  trust_lock_recommended: boolean
  __mock?: boolean
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
  analysis:any
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
  metadata:Record<string,any>
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
  metadata:Record<string,any>
  __mock?:boolean
}
