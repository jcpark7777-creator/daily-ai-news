from __future__ import annotations

import json
import logging
import os
from datetime import datetime, timedelta, timezone
from pathlib import Path
from zoneinfo import ZoneInfo

import yaml

from collector.google_news import search_google_news
from collector.gdelt import search_gdelt
from processor.deduplicator import deduplicate
from processor.article_parser import extract_article_text
from ai.analyzer import summarize_articles, create_overall_analysis
from reporter.markdown import render_markdown, render_index, render_report_html

BASE = Path(__file__).resolve().parents[1]
logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("daily-news")


def load_config():
    with open(BASE / "config/topics.yaml", encoding="utf-8") as f:
        return yaml.safe_load(f)


def main():
    cfg = load_config()
    hours = int(os.getenv("LOOKBACK_HOURS", cfg.get("lookback_hours", 24)))
    max_articles = int(os.getenv("MAX_ARTICLES", cfg.get("max_articles", 30)))
    topics = cfg["topics"]

    collected = []
    for topic in topics:
        try:
            found = search_google_news(
                topic, hours,
                cfg["google_news"]["hl"],
                cfg["google_news"]["gl"],
                cfg["google_news"]["ceid"],
            )
            log.info("Google News '%s': %d건", topic, len(found))
            collected.extend(found)
        except Exception as exc:
            log.warning("Google News 검색 실패 (%s): %s", topic, exc)

        if cfg.get("gdelt", {}).get("enabled", True):
            try:
                found = search_gdelt(
                    topic, hours,
                    int(cfg["gdelt"].get("max_records_per_query", 75)),
                )
                log.info("GDELT '%s': %d건", topic, len(found))
                collected.extend(found)
            except Exception as exc:
                log.warning("GDELT 검색 실패 (%s): %s", topic, exc)

    unique = deduplicate(collected)
    # 최신 기사 우선 정렬. 날짜가 없는 기사는 뒤쪽으로 배치합니다.
    unique.sort(key=lambda x: x.get("published_at") or "", reverse=True)
    selected = unique[:max_articles]
    log.info("중복 제거 후 %d건, 분석 대상 %d건", len(unique), len(selected))

    article_cfg = cfg.get("article", {})
    for idx, article in enumerate(selected, 1):
        log.info("본문 추출 %d/%d: %s", idx, len(selected), article["title"][:80])
        article["article_text"] = extract_article_text(
            article["url"],
            int(article_cfg.get("request_timeout_seconds", 20)),
            int(article_cfg.get("max_text_chars", 18000)),
        )
        if not article["article_text"]:
            article["article_text"] = ""
            article["limitation"] = "원문 본문을 자동 추출하지 못해 검색 설명으로 분석"
        # Gemini 입력 길이와 API 비용/한도 제어를 위한 상한
        article["article_text"] = article["article_text"][:18000]

    if not selected:
        log.warning("수집된 기사가 없습니다. 빈 보고서를 생성합니다.")

    summaries = summarize_articles(selected) if selected else []
    overall = create_overall_analysis(summaries) if summaries else {
        "executive_summary": "최근 검색 기간에 분석할 기사가 수집되지 않았습니다.",
        "major_trends": [], "company_updates": [], "technology_trends": [],
        "market_implications": {"positive": [], "negative": []},
        "risks_and_uncertainties": ["검색 결과가 없거나 뉴스 제공처에 일시적인 문제가 있을 수 있습니다."],
        "watchlist": [], "conclusion": "검색 키워드와 뉴스 수집 상태를 확인하세요."
    }

    now = datetime.now(ZoneInfo("Asia/Seoul"))
    date_key = now.strftime("%Y-%m-%d")
    reports_dir = BASE / "reports" / "daily"
    site_daily = BASE / "site" / "daily"
    data_dir = BASE / "data"
    reports_dir.mkdir(parents=True, exist_ok=True)
    site_daily.mkdir(parents=True, exist_ok=True)
    data_dir.mkdir(parents=True, exist_ok=True)

    markdown = render_markdown(date_key, summaries, overall)
    report_path = reports_dir / f"{date_key}.md"
    report_path.write_text(markdown, encoding="utf-8")
    (site_daily / f"{date_key}.md").write_text(markdown, encoding="utf-8")
    (site_daily / f"{date_key}.html").write_text(
        render_report_html(markdown, f"{date_key} 반도체 뉴스 분석"), encoding="utf-8"
    )

    (data_dir / f"{date_key}.json").write_text(
        json.dumps({"date": date_key, "articles": summaries, "overall": overall},
                   ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    existing = sorted(reports_dir.glob("*.md"), reverse=True)
    links = [(p.stem, f"daily/{p.stem}.html") for p in existing]
    (BASE / "site" / "index.html").write_text(render_index(links), encoding="utf-8")

    log.info("보고서 생성 완료: %s", report_path)


if __name__ == "__main__":
    main()
