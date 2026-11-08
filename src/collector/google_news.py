from __future__ import annotations

from datetime import datetime, timedelta, timezone
from urllib.parse import urlencode

import feedparser
import requests


def _iso_from_struct_time(value):
    if not value:
        return None
    return datetime(*value[:6], tzinfo=timezone.utc).isoformat()


def search_google_news(query: str, hours: int, hl="ko", gl="KR", ceid="KR:ko"):
    # when:1d는 RSS 검색 결과가 오래된 기사로 채워지는 것을 줄이기 위한 필터입니다.
    q = f'{query} when:1d'
    params = {"q": q, "hl": hl, "gl": gl, "ceid": ceid}
    url = "https://news.google.com/rss/search?" + urlencode(params)
    feed = feedparser.parse(url)

    results = []
    cutoff = datetime.now(timezone.utc) - timedelta(hours=hours)
    for entry in feed.entries:
        published = _iso_from_struct_time(
            getattr(entry, "published_parsed", None)
            or getattr(entry, "updated_parsed", None)
        )
        if published:
            dt = datetime.fromisoformat(published)
            if dt < cutoff:
                continue
        source = getattr(entry, "source", {}) or {}
        results.append({
            "title": getattr(entry, "title", "").strip(),
            "url": getattr(entry, "link", "").strip(),
            "published_at": published,
            "source": source.get("title", "") if hasattr(source, "get") else "",
            "description": getattr(entry, "summary", ""),
            "provider": "Google News RSS",
            "matched_query": query,
        })
    return results
