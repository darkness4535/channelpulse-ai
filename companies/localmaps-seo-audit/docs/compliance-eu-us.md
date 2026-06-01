# LocalMaps SEO Audit — Compliance Checklist (EU + US)

## Before any outreach is approved

### Personalization
- [ ] Message references specific business name and at least one audit finding
- [ ] PDF audit matches the lead (correct lead_id / business name)

### United States (CAN-SPAM)
- [ ] Valid sender identity (real business name + reply address)
- [ ] Clear opt-out: "Reply STOP to opt out" or unsubscribe link
- [ ] Non-deceptive subject line
- [ ] Physical mailing address available if required for bulk email

### European Union (GDPR)
- [ ] Lawful basis documented: B2B legitimate interest OR prior consent
- [ ] Data minimization: only business contact data needed for outreach
- [ ] Right to object: include "Reply to opt out" / deletion request path
- [ ] Record of processing if scaling (maintain outreach log)

### WhatsApp / Telegram
- [ ] First message identifies sender and purpose
- [ ] Easy opt-out if user declines
- [ ] No unsolicited bulk messaging without local law review

### Forbidden (from config)
- [ ] No guaranteed #1 Local Pack ranking
- [ ] No mass spam templates
- [ ] No unauthorized personal data collection

## Approval workflow

1. Head of Sales → `memory/outreach/drafts_{date}.json`
2. Compliance review → `memory/outreach/approved/approved_{date}.json`
3. **Human approval required** before `send_outreach`
