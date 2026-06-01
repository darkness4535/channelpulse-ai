"""GBP / local SEO audit scoring and PDF generation."""

from __future__ import annotations

import json
import re
from pathlib import Path

GBP_CHECKLIST = [
    "business_name_consistent",
    "primary_category_set",
    "additional_categories",
    "description_filled",
    "website_link_valid",
    "phone_listed",
    "hours_complete",
    "service_area_defined",
    "photos_count_adequate",
    "owner_posts_recent",
    "reviews_count_healthy",
    "review_responses",
    "rating_above_competitors",
    "attributes_complete",
    "social_links_present",
]

CHECKLIST_LABELS = {
    "business_name_consistent": "Business name matches brand",
    "primary_category_set": "Primary category set correctly",
    "additional_categories": "Additional categories added",
    "description_filled": "Business description filled (150+ chars)",
    "website_link_valid": "Website link present and valid",
    "phone_listed": "Phone number listed",
    "hours_complete": "Opening hours complete",
    "service_area_defined": "Service area / address defined",
    "photos_count_adequate": "Enough photos (10+)",
    "owner_posts_recent": "Recent owner posts (30 days)",
    "reviews_count_healthy": "Healthy review count (20+)",
    "review_responses": "Owner responds to reviews",
    "rating_above_competitors": "Rating competitive in niche",
    "attributes_complete": "Relevant attributes filled",
    "social_links_present": "Social / booking links present",
}


def _slugify(value: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", value.lower()).strip("-")
    return slug or "lead"


def audit_lead(lead: dict) -> dict:
    """Score a Maps lead and produce audit JSON."""
    lead_id = lead.get("lead_id") or _slugify(lead.get("name", "unknown"))
    rating = float(lead.get("rating") or 0)
    reviews = int(lead.get("review_count") or 0)
    pains = list(lead.get("pain_signals") or [])

    checklist: dict[str, bool] = {}
    for item in GBP_CHECKLIST:
        checklist[item] = _infer_check(item, lead, rating, reviews, pains)

    passed = sum(1 for v in checklist.values() if v)
    visibility_score = round(passed / len(GBP_CHECKLIST) * 100)

    quick_wins = _quick_wins(checklist, lead, pains)

    return {
        "lead_id": lead_id,
        "business_name": lead.get("name"),
        "city": lead.get("city"),
        "country": lead.get("country"),
        "maps_url": lead.get("maps_url"),
        "visibility_score": visibility_score,
        "checklist": checklist,
        "checklist_passed": passed,
        "checklist_total": len(GBP_CHECKLIST),
        "quick_wins": quick_wins,
        "competitor_note": lead.get(
            "competitor_note",
            "Competitors in Local Pack have stronger profiles — see quick wins.",
        ),
        "offer_cta": "Book a full audit + 90-day roadmap ($299)",
    }


def _infer_check(
    item: str,
    lead: dict,
    rating: float,
    reviews: int,
    pains: list[str],
) -> bool:
    pain_text = " ".join(pains).lower()
    if item == "business_name_consistent":
        return bool(lead.get("name"))
    if item == "primary_category_set":
        return "no category" not in pain_text
    if item == "additional_categories":
        return "categories" not in pain_text
    if item == "description_filled":
        return "empty description" not in pain_text and "no description" not in pain_text
    if item == "website_link_valid":
        return bool(lead.get("website")) and "broken" not in pain_text
    if item == "phone_listed":
        return bool(lead.get("phone")) or "no phone" not in pain_text
    if item == "hours_complete":
        return "hours" not in pain_text
    if item == "service_area_defined":
        return bool(lead.get("city"))
    if item == "photos_count_adequate":
        return "few photos" not in pain_text and "no photos" not in pain_text
    if item == "owner_posts_recent":
        return "no posts" not in pain_text
    if item == "reviews_count_healthy":
        return reviews >= 20
    if item == "review_responses":
        return "no responses" not in pain_text
    if item == "rating_above_competitors":
        return rating >= 4.0
    if item == "attributes_complete":
        return "attributes" not in pain_text
    if item == "social_links_present":
        return "no social" not in pain_text
    return False


def _quick_wins(checklist: dict[str, bool], lead: dict, pains: list[str]) -> list[dict]:
    wins: list[dict] = []
    if not checklist.get("description_filled"):
        wins.append(
            {
                "title": "Complete your GBP description",
                "impact": "high",
                "effort": "low",
                "detail": "Add 150+ chars with services, area, and keywords.",
            }
        )
    if not checklist.get("reviews_count_healthy"):
        wins.append(
            {
                "title": "Launch a review request campaign",
                "impact": "high",
                "effort": "medium",
                "detail": "Target 5 new reviews/month via email/SMS after service.",
            }
        )
    if not checklist.get("photos_count_adequate"):
        wins.append(
            {
                "title": "Upload 10+ quality photos",
                "impact": "medium",
                "effort": "low",
                "detail": "Exterior, interior, team, and top services.",
            }
        )
    if not checklist.get("owner_posts_recent"):
        wins.append(
            {
                "title": "Post weekly GBP updates",
                "impact": "medium",
                "effort": "low",
                "detail": "Offers, events, or tips — signals activity to Google.",
            }
        )
    if not wins and pains:
        wins.append(
            {
                "title": f"Fix: {pains[0]}",
                "impact": "high",
                "effort": "medium",
                "detail": "Address the top pain signal found in your profile.",
            }
        )
    return wins[:3]


def save_audit_json(audit: dict, path: Path) -> Path:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(audit, ensure_ascii=False, indent=2), encoding="utf-8")
    return path


def generate_audit_pdf(audit: dict, path: Path, *, company_name: str = "LocalMaps SEO Audit") -> Path:
    """Generate a mini-audit PDF report."""
    from fpdf import FPDF

    path.parent.mkdir(parents=True, exist_ok=True)

    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_margins(15, 15, 15)
    pdf.add_page()
    content_w = pdf.w - pdf.l_margin - pdf.r_margin

    pdf.set_font("Helvetica", "B", 20)
    pdf.cell(content_w, 12, company_name, new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 11)
    pdf.cell(content_w, 8, "Google Business Profile Mini-Audit", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    name = audit.get("business_name") or "Your Business"
    location = ", ".join(filter(None, [audit.get("city"), audit.get("country")]))
    pdf.set_font("Helvetica", "B", 14)
    pdf.cell(content_w, 10, name, new_x="LMARGIN", new_y="NEXT")
    if location:
        pdf.set_font("Helvetica", "", 11)
        pdf.cell(content_w, 8, location, new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    score = audit.get("visibility_score", 0)
    pdf.set_font("Helvetica", "B", 16)
    pdf.cell(content_w, 10, f"Visibility Score: {score}/100", new_x="LMARGIN", new_y="NEXT")
    passed = audit.get("checklist_passed", 0)
    total = audit.get("checklist_total", len(GBP_CHECKLIST))
    pdf.set_font("Helvetica", "", 11)
    pdf.cell(content_w, 8, f"Checklist: {passed}/{total} items passed", new_x="LMARGIN", new_y="NEXT")
    pdf.ln(6)

    pdf.set_font("Helvetica", "B", 13)
    pdf.cell(content_w, 10, "Top 3 Quick Wins", new_x="LMARGIN", new_y="NEXT")
    for i, win in enumerate(audit.get("quick_wins") or [], 1):
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 11)
        pdf.multi_cell(content_w, 7, f"{i}. {win.get('title', 'Improvement')}")
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "", 10)
        pdf.multi_cell(content_w, 6, win.get("detail", ""))
        pdf.ln(2)

    pdf.ln(4)
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "B", 12)
    pdf.cell(content_w, 10, "Next Step", new_x="LMARGIN", new_y="NEXT")
    pdf.set_x(pdf.l_margin)
    pdf.set_font("Helvetica", "", 11)
    pdf.multi_cell(content_w, 7, audit.get("offer_cta", "Contact us for a full audit."))

    pdf.output(str(path))
    return path


def audit_leads_file(leads_path: Path, audits_dir: Path, *, company_name: str) -> list[dict]:
    """Process all qualifying leads from a leads JSON file."""
    data = json.loads(leads_path.read_text(encoding="utf-8"))
    results: list[dict] = []
    for lead in data.get("leads", []):
        if int(lead.get("score", 0)) < 6:
            continue
        audit = audit_lead(lead)
        lead_id = audit["lead_id"]
        save_audit_json(audit, audits_dir / f"{lead_id}.json")
        generate_audit_pdf(audit, audits_dir / f"{lead_id}.pdf", company_name=company_name)
        results.append(audit)
    return results
