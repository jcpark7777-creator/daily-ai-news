from __future__ import annotations

from datetime import datetime, timezone

import requests

ENDPOINT = "https://api.gdeltproject.org/api/v2/doc/doc"


def search_gdelt(query: str, hours: int = 24, max_records: int = 75):
    params = {
        "query": query,
        "mode": "ArtList",
        "format": "json",
        "sort": "HybridRel",
        "timespan": f"{hours}h",
        "maxrecords": max_records,
    }
    response = requests.get(ENDPOINT, params=params, timeout=25)
    response.raise_for_status()
    payload = response.json()

    results = []
    for item in payload.get("articles", []):
        seen = item.get("seendate", "")
        published = None
        if seen:
            try:
                published = datetime.strptime(seen, "%Y%m%dT%H%M%SZ").replace(
                    tzinfo=timezone.utc
                ).isoformat()
            except ValueError:
                published = None
        results.append({
            "title": (item.get("title") or "").strip(),
            "url": (item.get("url") or "").strip(),
            "published_at": published,
            "source": item.get("domain", ""),
            "description": "",
            "provider": "GDELT",
            "matched_query": query,
        })
    return results
