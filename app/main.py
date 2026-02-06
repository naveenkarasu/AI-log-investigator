from fastapi import FastAPI
from pydantic import BaseModel, Field
from typing import List
from app.analyzer.heuristics import detect_issues, rank_issues

app = FastAPI(title="AI Log Investigator", version="0.2.0")


class AnalyzeRequest(BaseModel):
    log_text: str = Field(..., description="Raw log text to analyze")
    app_name: str | None = None
    environment: str | None = None


class Issue(BaseModel):
    category: str
    reason: str
    evidence: List[str]
    keyword_hits: List[str]


class AnalyzeResponse(BaseModel):
    summary: str
    top_category: str
    confidence: float
    issues: List[Issue]


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_logs(req: AnalyzeRequest):
    issues = detect_issues(req.log_text)

    # Pick the first issue as "top" (we'll improve ranking soon)
    top = issues[0]

    # Simple confidence: higher if not unknown
    confidence = 0.45 if top["category"] != "unknown" else 0.15

    summary = f"{top['reason']} Evidence lines: {min(len(top['evidence']), 3)} shown."

    return AnalyzeResponse(
        summary=summary,
        top_category=top["category"],
        confidence=confidence,
        issues=issues
    )

