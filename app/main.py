from fastapi import FastAPI
from pydantic import BaseModel
from app.analyzer.heuristics import detect_issue

app = FastAPI(title="AI Log Investigator", version="0.1.0")


class AnalyzeRequest(BaseModel):
    log_text: str
    app_name: str | None = None
    environment: str | None = None


class AnalyzeResponse(BaseModel):
    summary: str
    category: str
    confidence: float


@app.get("/health")
def health_check():
    return {"status": "ok"}


@app.post("/analyze", response_model=AnalyzeResponse)
def analyze_logs(req: AnalyzeRequest):

    result = detect_issue(req.log_text)

    return AnalyzeResponse(
        summary=result["reason"],
        category=result["category"],
        confidence=0.40 if result["category"] != "unknown" else 0.10
    )

