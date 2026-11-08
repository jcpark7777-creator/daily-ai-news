from __future__ import annotations

import re
from urllib.parse import urlsplit, urlunsplit, parse_qsl, urlencode


TRACKING_KEYS = {"utm_source", "utm_medium", "utm_campaign", "utm_term",
                 "utm_content", "gclid", "fbclid"}


def canonical_url(url: str) -> str:
    if not url:
        return ""
    try:
        parts = urlsplit(url.strip())
        query = [(k, v) for k, v in parse_qsl(parts.query)
                 if k.lower() not in TRACKING_KEYS]
        return urlunsplit((parts.scheme.lower(), parts.netloc.lower(),
                           parts.path.rstrip("/"), urlencode(query), ""))
    except Exception:
        return url.strip()


def title_key(title: str) -> str:
    return re.sub(r"[\W_]+", "", (title or "").lower())


def deduplicate(items):
    seen_urls, seen_titles, output = set(), set(), []
    for item in items:
        url = canonical_url(item.get("url", ""))
        title = title_key(item.get("title", ""))
        if not item.get("title") or not url:
            continue
        if url in seen_urls or (title and title in seen_titles):
            continue
        item["canonical_url"] = url
        seen_urls.add(url)
        if title:
            seen_titles.add(title)
        output.append(item)
    return output
