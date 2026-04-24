from __future__ import annotations

import json
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any


@dataclass
class LeadInput:
    name: str | None
    email: str | None
    business_type: str | None
    company_size: str | None
    budget: int | None
    urgency: str | None
    goal: str | None
    message: str | None


def safe_int(value: Any) -> int | None:
    if value is None or value == "":
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def normalize_lead(raw: dict[str, Any]) -> LeadInput:
    return LeadInput(
        name=raw.get("name"),
        email=raw.get("email"),
        business_type=raw.get("business_type"),
        company_size=raw.get("company_size"),
        budget=safe_int(raw.get("budget")),
        urgency=raw.get("urgency"),
        goal=raw.get("goal"),
        message=raw.get("message"),
    )


def lead_completeness(lead: LeadInput) -> tuple[list[str], list[str]]:
    missing = []
    unclear = []

    if not lead.name:
        missing.append("name")
    if not lead.email:
        missing.append("email")
    if not lead.business_type:
        missing.append("business_type")
    if lead.budget is None:
        missing.append("budget")
    if not lead.urgency:
        missing.append("urgency")
    if not lead.message:
        missing.append("message")

    if lead.message and len(lead.message.strip()) < 12:
        unclear.append("message_too_short")
    if lead.goal and len(lead.goal.strip()) < 5:
        unclear.append("goal_too_short")

    return missing, unclear


def score_lead(lead: LeadInput) -> tuple[int, list[str]]:
    score = 0
    reasons = []

    urgency = (lead.urgency or "").lower()
    if urgency in {"immediate", "asap", "this week"}:
        score += 35
        reasons.append("high_urgency")
    elif urgency in {"this month", "soon"}:
        score += 20
        reasons.append("medium_urgency")
    elif urgency:
        score += 8
        reasons.append("low_urgency")

    if lead.budget is not None:
        if lead.budget >= 5000:
            score += 30
            reasons.append("strong_budget")
        elif lead.budget >= 2000:
            score += 18
            reasons.append("mid_budget")
        elif lead.budget > 0:
            score += 6
            reasons.append("low_budget")

    company_size = (lead.company_size or "").lower()
    if company_size in {"11-50", "51-200", "200+"}:
        score += 10
        reasons.append("team_with_growth_potential")
    elif company_size in {"1-10", "solo"}:
        score += 4
        reasons.append("small_team")

    signal_text = " ".join(
        filter(None, [lead.goal or "", lead.message or "", lead.business_type or ""])
    ).lower()

    high_intent_terms = [
        "launch",
        "landing page",
        "book calls",
        "generate leads",
        "sales funnel",
        "automation",
        "funnel",
        "webinar",
        "follow-up emails",
        "urgent",
        "ready",
    ]
    for term in high_intent_terms:
        if term in signal_text:
            score += 5
            reasons.append(f"intent:{term}")

    return min(score, 100), reasons


def classify_lead(score: int, missing: list[str], unclear: list[str]) -> str:
    if len(missing) >= 3 or unclear:
        return "needs_review"
    if score >= 75:
        return "hot"
    if score >= 45:
        return "warm"
    return "cold"


def classification_prompt(lead: LeadInput) -> str:
    return f"""You are an AI lead triage assistant for KeaBuilder, a SaaS platform for funnels, lead capture, and automation.

Classify the lead into one of: hot, warm, cold, needs_review.

Rules:
- Hot: urgent timeline, clear commercial intent, sufficient budget, strong purchase signal
- Warm: real interest but moderate urgency or moderate budget
- Cold: vague interest, weak urgency, limited budget, low buying signal
- Needs_review: missing critical inputs or message is too unclear to classify confidently

Return JSON only with:
{{
  "category": "hot|warm|cold|needs_review",
  "confidence": 0-1,
  "reasoning": ["short reason", "short reason"],
  "follow_up_questions": ["question 1", "question 2"]
}}

Lead:
{json.dumps(asdict(lead), ensure_ascii=True)}"""


def response_prompt(lead: LeadInput, category: str) -> str:
    return f"""You are KeaBuilder's AI sales assistant.

Write a short, warm, human reply to this inbound lead.

Guidelines:
- Use the lead's first name if available
- Mention their business type or goal when possible
- Match the urgency without sounding pushy
- Sound like a helpful human, not a template
- Keep it between 50 and 90 words
- If information is missing, ask one clear follow-up question

Lead category: {category}
Lead data:
{json.dumps(asdict(lead), ensure_ascii=True)}

Return JSON only:
{{
  "subject": "email subject",
  "reply": "message body"
}}"""


def fallback_reply(lead: LeadInput, category: str, missing: list[str]) -> dict[str, str]:
    first_name = (lead.name or "there").split()[0]
    business = lead.business_type or "your business"
    goal = lead.goal or "improving your funnel"

    if category == "hot":
        reply = (
            f"Hi {first_name}, thanks for reaching out. It sounds like you want help with "
            f"{goal} for {business}, and your timeline is active. We'd be a great fit to move "
            f"quickly here. If you're available, send your target launch date and current funnel "
            f"status, and we can suggest the fastest next step."
        )
    elif category == "warm":
        reply = (
            f"Hi {first_name}, thanks for sharing your goals for {business}. It sounds like you're "
            f"exploring the right setup for {goal}. A good next step would be to understand your "
            f"main conversion goal and traffic source so we can recommend the most useful funnel "
            f"and automation flow."
        )
    elif category == "cold":
        reply = (
            f"Hi {first_name}, thanks for reaching out. We'd be happy to help with {goal}. To point "
            f"you in the right direction, could you share what outcome you want from KeaBuilder and "
            f"when you'd ideally like to launch?"
        )
    else:
        asked = ", ".join(missing[:2]) if missing else "a bit more detail"
        reply = (
            f"Hi {first_name}, thanks for reaching out. I can help, but I need {asked} before I can "
            f"recommend the right next step. Could you share your goal, timeline, and approximate "
            f"budget so we can guide you properly?"
        )

    return {
        "subject": f"KeaBuilder inquiry for {business}",
        "reply": reply,
    }


def process_lead(raw: dict[str, Any]) -> dict[str, Any]:
    lead = normalize_lead(raw)
    missing, unclear = lead_completeness(lead)
    score, reasons = score_lead(lead)
    category = classify_lead(score, missing, unclear)
    response = fallback_reply(lead, category, missing)

    follow_up_questions = []
    if "budget" in missing:
        follow_up_questions.append("What budget range have you set for this project?")
    if "urgency" in missing:
        follow_up_questions.append("When are you hoping to launch?")
    if "business_type" in missing:
        follow_up_questions.append("What type of business are you running?")
    if unclear:
        follow_up_questions.append("Can you describe the result you want in one or two sentences?")

    return {
        "lead": asdict(lead),
        "score": score,
        "category": category,
        "missing_fields": missing,
        "unclear_signals": unclear,
        "scoring_reasons": reasons,
        "classification_prompt": classification_prompt(lead),
        "response_prompt": response_prompt(lead, category),
        "response": response,
        "follow_up_questions": follow_up_questions,
    }


def load_payload(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return payload
    return [payload]


def main() -> int:
    input_path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("assessment/sample_leads.json")
    results = [process_lead(item) for item in load_payload(input_path)]
    print(json.dumps(results, indent=2, ensure_ascii=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
