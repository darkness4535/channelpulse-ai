# LocalMaps SEO Audit — PDF Mini-Audit Template Spec

> Issue: CHA-11 · Company: localmaps-seo-audit · Version: 1

## Purpose

Professional one-page PDF for cold outreach — proves value before the sales call.

## Layout (A4, portrait)

| Section | Content |
|---------|---------|
| Header | LocalMaps SEO Audit logo text + tagline |
| Business block | Business name, city/country |
| Score | Visibility Score 0–100 (large), checklist X/15 |
| Quick Wins | 3 numbered items: title + 1-2 sentence detail |
| CTA | "Book full audit + 90-day roadmap ($299)" + contact placeholder |
| Footer | "Prepared by LocalMaps SEO Audit · Not affiliated with Google" |

## Brand

- Primary: `#1a56db` (blue)
- Text: `#111827` (dark gray)
- Font: Helvetica (PDF) / system sans-serif (HTML)

## Implementation

- Generator: `company/audit.py` → `generate_audit_pdf()` using fpdf2
- Input: audit JSON from `memory/audits/{lead_id}.json`
- Output: `memory/audits/{lead_id}.pdf`

## Demo lead

See mock cycle output: `brew-corner-berlin.pdf` (Berlin coffee shop, score ~47/100).

## Future (UXDesigner)

- HTML/CSS template for richer branding
- Localized variants (DE/FR/ES cover pages)
