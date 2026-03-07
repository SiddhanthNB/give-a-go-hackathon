from lib.agentic_ai.models.insights import CommercialJudgment


def format_reply(data: CommercialJudgment) -> str:
    print("[DEBUG][format] format_reply start")
    if hasattr(data, "model_dump"):
        payload = data.model_dump()
        lines = []
        if "headline" in payload:
            lines.append(f"**Headline:** {payload['headline']}")
        if "analysis" in payload:
            lines.append(f"**Analysis:** {payload['analysis']}")
        if payload.get("risks"):
            lines.append("**Risks:**")
            for item in payload["risks"]:
                lines.append(f"- {item}")
        if payload.get("opportunities"):
            lines.append("**Opportunities:**")
            for item in payload["opportunities"]:
                lines.append(f"- {item}")
        if payload.get("recommendations"):
            lines.append("**Recommended Next Step:**")
            for rec in payload["recommendations"]:
                action = rec.get("action", "")
                rationale = rec.get("rationale", "")
                impact = rec.get("expected_impact", "")
                parts = [p for p in (action, rationale, impact) if p]
                lines.append(f"- {' — '.join(parts)}")
        if payload.get("priority_score") is not None:
            lines.append(f"**Priority Score:** {payload['priority_score']}/10")
        if lines:
            result = "\n".join(lines)
            print("[DEBUG][format] format_reply complete (structured)")
            return result
        print("[DEBUG][format] format_reply complete (payload)")
        return str(payload)
    print("[DEBUG][format] format_reply complete (raw)")
    return str(data)
