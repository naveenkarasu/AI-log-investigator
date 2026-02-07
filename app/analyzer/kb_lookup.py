import json
import logging
from pathlib import Path

log = logging.getLogger(__name__)

KB_PATH = Path(__file__).parent.parent / "data" / "error_kb.json"

_kb_cache: list[dict] | None = None


def load_kb() -> list[dict]:
    global _kb_cache
    if _kb_cache is None:
        with open(KB_PATH) as f:
            _kb_cache = json.load(f)
        log.info("Loaded %d KB entries from %s", len(_kb_cache), KB_PATH)
    return _kb_cache


def lookup_issue(keyword: str) -> dict | None:
    kb = load_kb()
    key = keyword.lower()
    for entry in kb:
        if entry["keyword"].lower() == key:
            return entry
    return None
