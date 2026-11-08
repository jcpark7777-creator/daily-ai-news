# Daily Semiconductor News Analyzer

반도체 산업, 삼성전자, SK하이닉스, HBM, AI 반도체 관련 뉴스를 최근 24시간 기준으로 수집하고 Gemini API로 기사별·종합 분석 보고서를 생성하는 GitHub Actions 프로젝트입니다.

## 1. 기능

- Google News RSS + GDELT 검색
- 최근 24시간 기사 수집
- URL/제목 기반 중복 제거
- 기사 본문 추출 시도 (접근 제한 시 RSS/GDELT 설명으로 대체)
- Gemini API로 기사별 요약 및 중요도 평가
- 전체 기사 종합 분석
- Markdown / JSON / HTML 보고서 생성
- GitHub Actions 매일 07:10 Asia/Seoul 실행
- GitHub Pages로 보고서 게시
- 수동 실행 지원

## 2. 사전 준비

1. GitHub 계정: https://github.com/signup
2. Google AI Studio: https://aistudio.google.com/
3. Gemini API Key 생성: AI Studio의 API keys 메뉴
4. 로컬 테스트를 하려면 Python 3.12 및 Git 설치 권장

Gemini API Key는 코드에 직접 입력하지 않습니다.

## 3. GitHub Repository 생성

1. GitHub에서 `New repository`를 선택합니다.
2. Repository 이름을 `daily-semiconductor-news`로 지정합니다.
3. 초기에는 `Private`를 권장합니다.
4. 이 프로젝트 파일 전체를 저장소 루트에 업로드하거나 Git으로 push합니다.

## 4. GitHub Secrets 등록

Repository → Settings → Secrets and variables → Actions → New repository secret

필수:
- Name: `GEMINI_API_KEY`
- Secret: Google AI Studio에서 발급한 키

선택:
- `GROQ_API_KEY`: Groq 대체 모델을 쓸 때만 등록

Repository → Settings → Secrets and variables → Actions → Variables에서 선택적으로 등록:
- `GEMINI_MODEL`: 기본값은 `gemini-3.8-flash`
- `GROQ_MODEL`: Groq 콘솔에서 현재 사용 가능한 모델 ID

모델 ID와 무료 등급/호출 한도는 변경될 수 있으므로 AI Studio의 Models 및 Usage 화면에서 확인하세요. 모델 오류가 나면 `GEMINI_MODEL` 변수에 사용 가능한 Flash 모델 ID를 지정합니다.

## 5. GitHub Pages 설정

1. Repository → Settings → Pages
2. Build and deployment의 Source를 `GitHub Actions`로 설정
3. `.github/workflows/daily_news.yml`이 기본 브랜치에 올라가 있는지 확인

Workflow에는 Pages 배포에 필요한 `pages: write`, `id-token: write` 권한이 포함되어 있습니다.

## 6. 자동 실행 및 수동 실행

- 자동 실행: 매일 오전 7시 10분, Asia/Seoul
- 수동 실행: Repository → Actions → Daily Semiconductor News → Run workflow

GitHub Actions의 예약 실행은 부하 상황에 따라 지연될 수 있습니다.

## 7. 로컬에서 실행

Windows PowerShell 예시:

```powershell
py -3.12 -m venv .venv
.venv\\Scripts\\Activate.ps1
pip install -r requirements.txt

$env:GEMINI_API_KEY="발급받은_API_KEY"
python src/main.py
```

실행 결과:
- `reports/daily/YYYY-MM-DD.md`
- `data/YYYY-MM-DD.json`
- `site/index.html`
- `site/daily/YYYY-MM-DD.md`
- `site/daily/YYYY-MM-DD.html` (GitHub Pages에서 보는 HTML 보고서)

## 8. 검색 주제 변경

`config/topics.yaml`의 `topics` 목록을 수정하면 됩니다.

현재 기본값:
- 반도체 산업
- 삼성전자 반도체
- SK하이닉스
- HBM
- AI 반도체
- semiconductor
- Samsung Electronics semiconductor
- SK hynix
- AI chip

수집 기사 수는 `max_articles: 30` 또는 GitHub Actions의 `MAX_ARTICLES`로 조정할 수 있습니다.

## 9. 무료 사용량과 비용 관리

- Google News RSS와 GDELT 공개 검색 API를 사용합니다.
- Gemini API 무료 등급은 모델별 일일/분당 호출 제한이 있습니다.
- 프로젝트는 기사 5개를 한 번의 AI 요청으로 묶어 기본 요청 수를 줄입니다.
- 하루 30개 기사면 기사별 분석은 대략 6회, 종합 분석은 1회 요청합니다.
- 무료 한도 초과 시 실행이 실패할 수 있으므로 Actions 로그와 AI Studio Usage를 확인하세요.
- Groq는 선택 사항이며 별도 무료 한도가 적용됩니다.
- 무료 사용 가능 여부와 모델 ID는 시점에 따라 달라집니다.

## 10. 주의사항

- Google News RSS 및 GDELT 검색 결과가 전체 뉴스의 완전한 목록을 보장하지 않습니다.
- 언론사 유료 구독벽, robots 정책, 요청 제한 등으로 본문 추출이 실패할 수 있습니다.
- 본문이 없으면 검색 설명만으로 분석하며 보고서에 한계를 표시합니다.
- 기사 원문을 무단으로 재배포하지 않고 링크와 요약 중심으로 사용하세요.
- 공개 Repository에는 API Key, `.env`, 비공개 데이터가 올라가지 않도록 주의하세요.
- AI 보고서는 투자 조언이 아닙니다. 중요한 사실은 원문으로 재확인하세요.

## 11. 문제 해결

### Gemini API 인증 오류
- `GEMINI_API_KEY` Secret 이름과 값 확인
- 키가 활성 프로젝트에 속하는지 확인

### 모델을 찾을 수 없음
- AI Studio에서 현재 사용 가능한 모델 확인
- Repository Variables의 `GEMINI_MODEL` 변경

### 429 / quota 오류
- AI Studio Usage에서 RPM/RPD 제한 확인
- 수집 기사 수 또는 배치 크기를 줄이고 재실행

### Pages가 게시되지 않음
- Settings → Pages → Source가 GitHub Actions인지 확인
- Actions 로그의 `Configure Pages`, `Deploy to GitHub Pages` 단계 확인

### 기사 본문이 비어 있음
- 해당 언론사의 유료 구독벽/봇 차단 가능성 확인
- 보고서의 검색 설명과 원문 링크를 확인

## 12. 프로젝트 구조

```text
config/topics.yaml
src/
  collector/       # Google News RSS, GDELT
  processor/       # 본문 추출, 중복 제거
  ai/              # Gemini, Groq, 분석 로직
  reporter/        # Markdown, HTML 보고서
  main.py
.github/workflows/daily_news.yml
reports/daily/
data/
site/
```
