# AI Log Investigator 🔎🤖

Analyze application logs and get:
- Detected issue categories (timeout, database, memory, auth, network, etc.)
- Evidence lines + keyword hits
- A concise root-cause summary with actionable fix steps
- Reliable fallback when LLM is unavailable (local knowledge base + heuristics)

## Features
- ✅ FastAPI API: `/analyze`, `/health`
- ✅ CLI: analyze single file or a directory of logs
- ✅ Free LLM integration (Hugging Face Inference Providers)
- ✅ Fallbacks: Local KB → Heuristics
- ✅ JSON output (easy to integrate into other tools)

## Project Structure
app/
main.py
analyzer/
heuristics.py
kb_lookup.py
llm_free.py
data/
error_kb.json
cli.py
requirements.txt

## Setup (Ubuntu)
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt

Create '.env'
HF_TOKEN=hf_your_token_here

Run API

uvicorn app.main:app --reload

Open:

    http://127.0.0.1:8000/docs

CLI usage
Analyze one log file

.venv/bin/python cli.py analyze test.log

Analyze a directory (all .log/.txt)

.venv/bin/python cli.py analyze-dir logs --out reports

Notes

    If LLM fails or rate-limits, tool falls back to KB + heuristics automatically.


Save and exit.

---

### Step 2 — Add example logs + example output (for screenshots)
Create sample folder:

```bash
mkdir -p examples/logs examples/reports

Create 3 sample logs:

echo "Connection timed out after 30s" > examples/logs/timeout.log
echo "ERROR: database connection refused" > examples/logs/database.log
echo "java.lang.OutOfMemoryError: Java heap space" > examples/logs/memory.log

Generate reports:

.venv/bin/python cli.py analyze-dir examples/logs --out examples/reports

Step 3 — Add GitHub-friendly housekeeping files
.gitignore

nano .gitignore

Paste:

.venv/
__pycache__/
*.pyc
.env
reports/
logs/
.DS_Store

Step 4 — Add a simple test (so repo looks serious)

Install pytest:

pip install pytest
pip freeze > requirements.txt

Create tests folder:

mkdir -p tests
nano tests/test_heuristics.py

Paste:

from app.analyzer.heuristics import detect_issues, rank_issues

def test_timeout_detection():
    issues = detect_issues("Connection timed out after 30s")
    issues = rank_issues(issues)
    assert issues[0]["category"] == "timeout"
    assert "timed out" in issues[0]["keyword_hits"][0].lower()

Run:

pytest -q

Step 5 — Add GitHub Actions CI (auto test on every push)

Create:

mkdir -p .github/workflows
nano .github/workflows/ci.yml

Paste:

name: CI

on:
  push:
  pull_request:

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Install deps
        run: |
          python -m pip install --upgrade pip
          pip install -r requirements.txt

      - name: Run tests
        run: pytest -q
