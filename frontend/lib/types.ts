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

export type RecoveryPayload = {
  paid:boolean
  clicked_link:boolean
  shared_documents:boolean
  shared_password:boolean
  installed_app:boolean
  shared_sms_code:boolean
}
