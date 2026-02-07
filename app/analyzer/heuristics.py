def _top_evidence_lines(log_text: str, keywords: list[str], limit: int = 8) -> list[str]:
    """
    Return up to 'limit' lines that contain any of the keywords.
    """
    lines = log_text.splitlines()
    hits = []
    for line in lines:
        low = line.lower()
        if any(k in low for k in keywords):
            hits.append(line.strip())
        if len(hits) >= limit:
            break
    return hits


def detect_issues(log_text: str) -> list[dict]:
    """
    Detect multiple possible issues from the logs.
    Returns a list of issues with category, reason, keywords, and evidence lines.
    """
    text = log_text.lower()

    patterns = [
        {
            "category": "memory",
            "reason": "The application likely ran out of memory (OOM).",
            "keywords": ["outofmemoryerror", "out of memory", "heap space", "oomkilled", "oom"],
        },
        {
            "category": "timeout",
            "reason": "Timeout detected (service call, DB, or network).",
            "keywords": ["timeout", "timed out", "read timeout", "connect timeout"],
        },
        {
            "category": "database",
            "reason": "Database-related failure detected (connect/query/lock).",
            "keywords": ["database", "jdbc", "sql", "deadlock", "connection refused", "too many connections"],
        },
        {
            "category": "authentication",
            "reason": "Authentication/authorization failure detected.",
            "keywords": ["unauthorized", "forbidden", "invalid token", "access denied", "permission denied"],
        },
        {
            "category": "network",
            "reason": "Network/DNS/connectivity issue detected.",
            "keywords": ["dns", "no route to host", "network is unreachable", "connection reset", "name or service not known"],
        },
        {
            "category": "disk",
            "reason": "Disk/storage issue detected (space, IO).",
            "keywords": ["no space left on device", "disk full", "i/o error", "filesystem", "read-only file system"],
        },
    ]

    issues = []
    for p in patterns:
        if any(k in text for k in p["keywords"]):
            issues.append(
                {
                    "category": p["category"],
                    "reason": p["reason"],
                    "evidence": _top_evidence_lines(log_text, p["keywords"], limit=8),
                    "keyword_hits": [k for k in p["keywords"] if k in text],
                }
            )

    # If nothing matched, return unknown
    if not issues:
        issues.append(
            {
                "category": "unknown",
                "reason": "No known error pattern detected. Need more context or different logs.",
                "evidence": _top_evidence_lines(log_text, ["error", "exception", "failed", "fatal"], limit=8),
                "keyword_hits": [],
            }
        )

    return issues

def rank_issues(issues: list[dict]) -> list[dict]:
    """
    Rank issues by:
    1) number of keyword hits (more matches = more likely)
    2) number of evidence lines
    """
    def score(issue: dict) -> int:
        return len(issue.get("keyword_hits", [])) * 2 + len(issue.get("evidence", []))

    return sorted(issues, key=score, reverse=True)

