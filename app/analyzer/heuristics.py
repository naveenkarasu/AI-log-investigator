def detect_issue(log_text: str) -> dict:
    """
    Very simple rule-based detection.
    Returns category and reason.
    """

    text = log_text.lower()

    if "timeout" in text:
        return {
            "category": "timeout",
            "reason": "The logs contain timeout-related errors."
        }

    if "database" in text or "db" in text:
        return {
            "category": "database",
            "reason": "The logs indicate a database-related failure."
        }

    if "out of memory" in text or "oom" in text or "out of memory" in text or "heap space" in text:
        return {
            "category": "memory",
            "reason": "The application ran out of memory."
        }

    if "unauthorized" in text or "forbidden" in text:
        return {
            "category": "authentication",
            "reason": "Authentication or authorization failure detected."
        }

    if "dns" in text or "network" in text:
        return {
            "category": "network",
            "reason": "Network or DNS resolution issue detected."
        }

    return {
        "category": "unknown",
        "reason": "No known error pattern detected."
    }

