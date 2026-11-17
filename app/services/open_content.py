"""Attribution data for texts from open sources (content/open/n*.json, I34/I35).

The attribution is read from the content files (not stored in the DB), so the
database schema does not change; it is keyed by the text slug.
"""
import json
from functools import lru_cache
from pathlib import Path
from typing import Dict, Optional

OPEN_DIR = Path(__file__).resolve().parents[2] / "content" / "open"
PUBLIC_FIELDS = ("source", "work", "author", "url", "license", "license_url")


@lru_cache(maxsize=1)
def _attributions() -> Dict[str, dict]:
    out: Dict[str, dict] = {}
    for p in sorted(OPEN_DIR.glob("n*.json")):
        try:
            records = json.loads(p.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for rec in records:
            attr = rec.get("attribution") or {}
            if rec.get("slug") and attr.get("url"):
                out[rec["slug"]] = {k: attr.get(k) for k in PUBLIC_FIELDS}
    return out


def attribution_for(slug: Optional[str]) -> Optional[dict]:
    if not slug:
        return None
    attr = _attributions().get(slug)
    return dict(attr) if attr else None
