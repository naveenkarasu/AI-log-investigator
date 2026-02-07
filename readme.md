# AI Log Investigator

Analyze application logs and get:
- Detected issue categories (timeout, database, memory, auth, network, disk)
- Evidence lines + keyword hits
- A concise root-cause summary with actionable fix steps
- Reliable fallback when LLM is unavailable (local knowledge base + heuristics)

## Features

- FastAPI API with `/analyze` and `/health` endpoints
- CLI to analyze single files or entire directories of logs
- Free LLM integration (Hugging Face Inference API)
- Three-tier fallback: LLM -> Knowledge Base -> Heuristics
- Structured JSON output for easy integration
- Docker support for containerized deployment

## Project Structure

```
app/
  main.py                 # FastAPI application
  analyzer/
    heuristics.py         # Pattern-based issue detection and ranking
    kb_lookup.py          # Knowledge base fallback lookup
    llm_free.py           # Hugging Face free LLM client
  data/
    error_kb.json         # Knowledge base entries
cli.py                    # Typer CLI interface
Dockerfile                # Container build
requirements.txt          # Python dependencies
```

## Setup

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create a `.env` file:

```
HF_TOKEN=hf_your_token_here
```

## Usage

### Run the API

```bash
uvicorn app.main:app --reload
```

Open the interactive docs at [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)

### CLI

Analyze a single log file:

```bash
python cli.py analyze test.log
```

Analyze all logs in a directory:

```bash
python cli.py analyze-dir logs/ --out reports/
```

Check API health:

```bash
python cli.py health
```

### Docker

```bash
docker build -t ai-log-investigator .
docker run -p 8000:8000 --env-file .env ai-log-investigator
```

## How It Works

1. **Heuristics** detect issue categories by pattern-matching keywords in log text
2. **Ranking** scores issues by keyword hits and evidence count
3. **LLM** (Hugging Face) generates root cause analysis and fix steps as JSON
4. If LLM fails, **Knowledge Base** provides fallback descriptions and fixes
5. If KB has no match, **heuristic summary** is returned as a last resort

## Detected Issue Categories

| Category | Example Keywords |
|----------|-----------------|
| Memory | OutOfMemoryError, heap space, OOM |
| Timeout | timed out, connection timeout |
| Database | JDBC, SQL, deadlock, connection refused |
| Authentication | unauthorized, forbidden, access denied |
| Network | DNS, no route to host, connection reset |
| Disk | no space left, disk full, I/O error |

## API Reference

### POST /analyze

**Request:**

```json
{
  "log_text": "java.lang.OutOfMemoryError: Java heap space",
  "app_name": "my-service",
  "environment": "production"
}
```

**Response:**

```json
{
  "summary": "Root cause: ...",
  "top_category": "memory",
  "confidence": 0.75,
  "issues": [
    {
      "category": "memory",
      "reason": "The application likely ran out of memory (OOM).",
      "evidence": ["java.lang.OutOfMemoryError: Java heap space"],
      "keyword_hits": ["outofmemoryerror", "heap space"]
    }
  ]
}
```

### GET /health

Returns `{"status": "ok"}` when the API is running.

## Notes

- If the LLM fails or hits rate limits, the tool falls back to KB + heuristics automatically
- No API key is required for basic heuristic analysis
- The HF_TOKEN enables enhanced LLM-powered root cause analysis
