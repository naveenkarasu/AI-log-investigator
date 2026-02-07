import json
import logging

from fastapi import FastAPI
from pydantic import BaseModel, Field

from app.analyzer.heuristics import detect_issues, rank_issues
from app.analyzer.kb_lookup import lookup_issue
from app.analyzer.llm_free import free_llm_analyze

log = logging.getLogger(__name__)

app = FastAPI(title="AI Log Investigator", version="0.6.0")

MAX_LOG_SIZE = 1_000_000  # 1 MB


class AnalyzeRequest(BaseModel):
    log_text: str = Field(
        ...,
        description="Raw log text to analyze",
        max_length=MAX_LOG_SIZE,
    )


class Issue(BaseModel):
    category: str
    reason: str
    evidence: list[str]
    keyword_hits: list[str]


class AnalyzeResponse(BaseModel):
    summary: str
    top_category: str
    confidence: float
    issues: list[Issue]


@app.get("/health")
def health_check():
    return {"status": "ok"}


def _safe_json_parse(text: str) -> dict | None:
    """
    Try to extract a JSON object from the model output.
    Returns dict if successful, else None.
    """
    if not text:
        return None

    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to extract JSON block between first { and last }
    start = text.find("{")
    end = text.rfind("}")
    if start != -1 and end != -1 and end > start:
        candidate = text[start : end + 1]
        try:
            return json.loads(candidate)
        except json.JSONDecodeError:
            return None

    return None


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_logs(req: AnalyzeRequest):

    # 1) Detect and rank issues
    issues = detect_issues(req.log_text)
    issues = rank_issues(issues)
    top = issues[0]

    # 2) Base fallback summary
    heuristic_summary = f"{top['reason']} Evidence lines: {len(top['evidence'])}."

    # 3) Ask LLM for STRICT JSON only
    prompt = f"""
You are a log analysis assistant.
Return ONLY valid JSON. No extra text. No explanations.

JSON schema:
{{
  "root_cause": "string",
  "fix_steps": ["string", "string", "string"],
  "confidence": 0.0
}}

Detected issues (from rules):
{issues}

Now output JSON:
"""

    llm_output = free_llm_analyze(prompt)

    # 4) If LLM works and returns JSON, use it
    parsed = _safe_json_parse(llm_output) if llm_output else None
    if parsed and "root_cause" in parsed and "fix_steps" in parsed:
        fix_steps = parsed.get("fix_steps", [])
        if isinstance(fix_steps, list):
            fix_text = " | ".join([str(x) for x in fix_steps if x])
        else:
            fix_text = str(fix_steps)

        final_summary = f"Root cause: {parsed['root_cause']}. Fix: {fix_text}"
        confidence = float(parsed.get("confidence", 0.65))
        confidence = max(0.0, min(confidence, 1.0))

        return AnalyzeResponse(
            summary=final_summary,
            top_category=top["category"],
            confidence=confidence,
            issues=issues
        )

    # 5) If LLM fails or output is messy -> KB fallback
    log.info("LLM unavailable or returned bad output, falling back to KB")
    kb = lookup_issue(top["category"])
    if kb:
        description = kb["description"]
        fixes = " ; ".join(kb["fixes"])
        final_summary = f"{description}. Suggested fixes: {fixes}"
        confidence = 0.50
    else:
        final_summary = heuristic_summary + " (LLM output not usable)"
        confidence = 0.25

    return AnalyzeResponse(
        summary=final_summary,
        top_category=top["category"],
        confidence=confidence,
        issues=issues
    )
