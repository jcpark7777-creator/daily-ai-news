from __future__ import annotations

import requests
import trafilatura


def extract_article_text(url: str, timeout: int = 20, max_chars: int = 18000) -> str:
    if not url:
        return ""
    headers = {
        "User-Agent": "Mozilla/5.0 (compatible; DailyNewsResearchBot/1.0; +https://github.com/)"
    }
    try:
        response = requests.get(url, headers=headers, timeout=timeout)
        response.raise_for_status()
        text = trafilatura.extract(
            response.text,
            include_comments=False,
            include_tables=False,
            favor_precision=True,
        )
        return (text or "").strip()[:max_chars]
    except requests.RequestException:
        return ""
    except Exception:
        return ""
