import json
from pathlib import Path

KB_PATH = Path(__file__).parent.parent / "data" / "error_kb.json"

def load_kb() -> list[dict]:
    with open(KB_PATH) as f:
        return json.load(f)

def lookup_issue(keyword: str) -> dict | None:
    kb = load_kb()
    key = keyword.lower()
    for entry in kb:
        if entry["keyword"].lower() == key:
            return entry
    return None

