# n8n WhatsApp Flow

## Flow Architecture

```
WhatsApp Trigger (webhook)
  -> HTTP Request to /integrations/n8n/whatsapp/inbound
  -> IF safe_to_send == true AND send_mode == real_beta_allowed
     -> WhatsApp Business Cloud: Send Message
  -> IF safe_to_send == false
     -> Log only (do not send)
```

## Step 1: WhatsApp Trigger

Configure your WhatsApp Business Cloud webhook or Twilio webhook to trigger the n8n workflow on incoming messages.

## Step 2: HTTP Request to Backend

**Method**: POST
**URL**: `http://localhost:8000/integrations/n8n/whatsapp/inbound`
**Headers**:
```
Content-Type: application/json
X-N8N-CyberAlerta-Secret: {{$env.N8N_WEBHOOK_SECRET}}
X-N8N-Execution-ID: {{$execution.id}}
```

**Body**:
```json
{
  "message_id": "{{$json.messageId}}",
  "from_number": "{{$json.from}}",
  "user_name": "{{$json.userName || 'Pessoa protegida'}}",
  "message": "{{$json.body}}",
  "channel": "whatsapp",
  "action_type": null,
  "already_acted": false,
  "trusted_contact_name": "{{$json.trustedContactName || ''}}",
  "trusted_contact_relation": "{{$json.trustedContactRelation || ''}}",
  "trusted_contact_phone": "{{$json.trustedContactPhone || ''}}",
  "reply_to_number": "{{$json.from}}"
}
```

## Step 3: Decision

Add an IF node after the HTTP Request:

- **Condition**: `{{$json.safe_to_send}}` equals `true` AND `{{$json.send_mode}}` equals `real_beta_allowed`

### True Branch: Send WhatsApp Message

Use WhatsApp Business Cloud node or Twilio node to send:
- **To**: `{{$json.reply_to_number}}`
- **Message**: `{{$json.user_message}}`

If `trusted_contact_should_alert` is `true`, also send to trusted contact:
- **To**: `{{$json.trusted_contact_phone}}`
- **Message**: `{{$json.trusted_contact_message}}`

### False Branch: Log Only

Log the response for monitoring. Do NOT send any message.

## Step 4: Recovery (Optional)

If `recovery_should_start` is `true`, call:
```
POST /integrations/n8n/recovery
```

With the incident details to get a recovery playbook.
