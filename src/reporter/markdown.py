from datetime import datetime
from zoneinfo import ZoneInfo


def _bullets(items):
    if not items:
        return "- 해당 사항 없음\n"
    return "".join(f"- {x}\n" for x in items)


def render_markdown(report_date, articles, overall):
    now = datetime.now(ZoneInfo("Asia/Seoul")).strftime("%Y-%m-%d %H:%M KST")
    lines = [
        f"# 반도체 산업 일일 뉴스 분석 ({report_date})",
        "",
        f"> 생성 시각: {now}  ",
        f"> 수집 기사: {len(articles)}건 · 분석 언어: 한국어",
        "",
        "## 1. Executive Summary",
        "",
        overall.get("executive_summary", "종합 요약이 생성되지 않았습니다."),
        "",
        "## 2. 주요 산업 동향",
        "",
    ]

    for trend in overall.get("major_trends", []):
        lines += [f"### {trend.get('topic', '주요 동향')}", "",
                  trend.get("analysis", ""), "",
                  "**근거 기사**", _bullets(trend.get("evidence_headlines", [])), ""]

    lines += ["## 3. 기업별 동향", ""]
    for company in overall.get("company_updates", []):
        lines += [f"### {company.get('company', '기업')}", "",
                  _bullets(company.get("updates", [])),
                  f"**시사점:** {company.get('implications', '')}", ""]

    lines += ["## 4. 기술별 동향", ""]
    for tech in overall.get("technology_trends", []):
        lines += [f"### {tech.get('technology', '기술')}", "",
                  tech.get("analysis", ""), "",
                  "**관찰 항목**", _bullets(tech.get("watch_items", [])), ""]

    impacts = overall.get("market_implications", {})
    lines += ["## 5. 시장 영향", "", "### 긍정 요인", "",
              _bullets(impacts.get("positive", [])),
              "### 부정 요인 및 부담 요인", "",
              _bullets(impacts.get("negative", [])),
              "## 6. 위험 및 불확실성", "",
              _bullets(overall.get("risks_and_uncertainties", [])),
              "## 7. 향후 관찰 항목", "",
              _bullets(overall.get("watchlist", [])),
              "## 8. 종합 결론", "",
              overall.get("conclusion", ""), "",
              "---", "",
              "## 9. 기사별 상세 분석", ""]

    for i, item in enumerate(sorted(articles, key=lambda x: x.get("importance", 0), reverse=True), 1):
        lines += [
            f"### {i}. {item.get('headline', '제목 없음')}",
            "",
            f"- 출처: {item.get('source') or '미상'}",
            f"- 중요도: {item.get('importance', 'N/A')}/5",
            f"- 게시 시각: {item.get('published_at') or '미확인'}",
            f"- 신뢰도: {item.get('confidence', '미확인')}",
            f"- 원문: {item.get('url', '')}",
            "",
            item.get("summary", ""),
            "",
            "**핵심 포인트**",
            _bullets(item.get("key_points", [])),
            f"**관련 기업:** {', '.join(item.get('companies', [])) or '미확인'}",
            "",
            f"**관련 기술:** {', '.join(item.get('technologies', [])) or '미확인'}",
            "",
            f"**산업 영향:** {item.get('impact', '')}",
            "",
            "**긍정 요인**",
            _bullets(item.get("positive_factors", [])),
            "**부정 요인**",
            _bullets(item.get("negative_factors", [])),
            "**후속 관찰 항목**",
            _bullets(item.get("watch_items", [])),
        ]
        if item.get("limitation"):
            lines += [f"> 분석 제한: {item['limitation']}", ""]
        lines.append("---")
        lines.append("")

    lines += [
        "## 분석 유의사항",
        "",
        "- 이 보고서는 공개 뉴스 검색 결과를 기반으로 자동 생성되었습니다.",
        "- 기사 본문 접근 제한, 검색 누락, 언론사 게시 시각 차이로 일부 내용이 빠질 수 있습니다.",
        "- AI 분석은 투자 조언이 아니며, 중요한 판단은 원문과 추가 자료를 확인해야 합니다.",
        "",
    ]
    return "\n".join(lines)


def render_index(report_files):
    rows = []
    for date, path in sorted(report_files, reverse=True):
        rows.append(f'<li><a href="{path}">{date} 반도체 뉴스 분석 보고서</a></li>')
    body = "\n".join(rows) or "<li>아직 생성된 보고서가 없습니다.</li>"
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Daily Semiconductor News Analyzer</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:900px;margin:40px auto;padding:0 20px;line-height:1.65;color:#222}}
h1{{line-height:1.25}}li{{margin:12px 0}}a{{color:#1459a6}}
.note{{color:#666;font-size:.92rem}}
</style></head><body>
<h1>Daily Semiconductor News Analyzer</h1>
<p>반도체 산업 · 삼성전자 · SK하이닉스 · HBM · AI 반도체</p>
<p class="note">매일 자동 수집 · Gemini API 기반 분석 · 한국어 상세 보고서</p>
<h2>일일 보고서</h2><ul>{body}</ul>
</body></html>"""


def render_report_html(markdown_text, title="반도체 산업 일일 뉴스 분석"):
    import markdown
    content = markdown.markdown(
        markdown_text,
        extensions=["tables", "fenced_code", "sane_lists"],
    )
    return f"""<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<style>
body{{font-family:system-ui,sans-serif;max-width:980px;margin:36px auto;padding:0 22px;line-height:1.75;color:#202124}}
h1,h2,h3{{line-height:1.35}}h2{{margin-top:2.2em;border-bottom:1px solid #ddd;padding-bottom:.35em}}
a{{overflow-wrap:anywhere;color:#1459a6}}blockquote{{border-left:4px solid #bbb;margin-left:0;padding-left:1em;color:#555}}
code{{background:#f2f2f2;padding:2px 5px;border-radius:4px}}li{{margin:.35em 0}}
</style></head><body>{content}</body></html>"""
