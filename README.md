# LEADERS FILES

실패를 넘은 사람들의 1차 기록 아카이브. 위대한 사람들의 성공담이 아니라, 가장 아팠던 하루를 날짜와 숫자, 그날 남긴 말로 기록하는 정적 매거진입니다.

- 라이브: https://readersfiles.pages.dev
- 저장소: https://github.com/oraclekidz/readersfiles

## 구조

```
data/s01_edison.py …       스토리 원고 (STORY 한국어 · STORY_EN 영문, publish_date 포함, 빌드의 유일한 원본)
data/lineup.py             후보 30인 라인업 (LINEUP 한국어 · LEADERS_EN 영문)
tools/build_site.py        빌더 — 발행일이 지난 원고만 한국어판과 영문판(/en/)에 동시 생성
tools/story_template.html  스토리 페이지 템플릿
tools/index_template.html  홈 템플릿
tools/leaders_template.html 라인업 템플릿
tools/en_story_template.html   영문 스토리 템플릿
tools/en_index_template.html   영문 홈 템플릿
tools/en_leaders_template.html 영문 라인업 템플릿
tools/build_en_docs.py     영문 원칙·개인정보·이용약관(/en/about/, /en/privacy/, /en/terms/) 생성
.github/workflows/publish-daily.yml  매일 KST 09:00 자동 발행 (한국어 + 영문)
index.html                 매거진 홈 (빌드 산출물)
en/index.html              영문 홈 (빌드 산출물)
stories/edison-1914.html   에디슨 · 1914년 12월 9일 웨스트오렌지 화재 (빌드 산출물)
en/stories/edison-1914.html 같은 편의 영문판 (빌드 산출물)
stories/lincoln-1858.html  링컨 · 1858년 상원 낙선과 1860년 (빌드 산출물)
stories/tesla-1895.html    테슬라 · 1895년 3월 13일 실험실 화재 (빌드 산출물)
leaders/index.html         후보 30인 라인업 (분류 필터)
en/leaders/index.html      영문 라인업
about/index.html           에디토리얼 원칙 (수동 관리)
privacy/index.html         개인정보 처리방침 (수동 관리)
terms/index.html           이용약관 (수동 관리)
en/about · en/privacy · en/terms   영문 대응 페이지 (build_en_docs.py 산출물)
404.html                   오류 페이지
assets/css/site.css        디자인 시스템 (다크 시네마틱)
assets/js/site.js          타임라인, 라인업 필터, 공유, 구독 폼 (한국어·영문 문구 분기)
assets/img/                초상(WebP/JPG)과 공유 이미지
functions/_middleware.js   /data/·/tools/·README 등 원본 경로를 404로 막는 Pages 미들웨어
sitemap.xml, robots.txt
```

`index.html`, `leaders/index.html`, `stories/*.html`, `en/**`, `sitemap.xml`은 손으로 고치지 않습니다. `data/`의 원고를 고친 뒤 빌더를 돌립니다.

## 예약발행

```bash
python3 tools/build_site.py                   # KST 오늘 이전 원고만 발행
python3 tools/build_site.py --today=2026-12-05 # 특정 날짜 기준으로 확인
python3 tools/build_site.py --include-future  # 전체 원고 빌드 (로컬 검증)
python3 tools/build_site.py --check-numbers   # 한글 수사(개수·나이) 전수 검사
```

- 원고는 `data/sNN_slug.py`에 `STORY = {...}`(한국어)와 `STORY_EN = {...}`(영문)로 두고 `publish_date`(YYYY-MM-DD)를 적습니다. 구조 필드(`slug`, `publish_date`, `img`, `birth`, `death`, `category`, `sources_count`)는 두 판이 공유하고, 문장·제목·타임라인·사료 노트는 언어별로 따로 씁니다. 빌더는 `STORY_EN`에 빠진 필드가 있으면 실패합니다.
- 빌더는 `publish_date <= 오늘(KST)`인 원고만 `stories/<slug>.html`와 `en/stories/<slug>.html`로 **동시에** 만들고, 미래 원고의 HTML은 만들지 않으며 이미 있던 파일은 양쪽에서 지웁니다. 홈·라인업·사이트맵도 발행분만 반영합니다. 미발행 원고의 slug는 영문 라인업 클라이언트 데이터에도 싣지 않습니다.
- 나이·연도·횟수·개수는 모두 아라비아 숫자로 적습니다. 빌더가 한국어 원고의 한글 수사를 검사해 1건이라도 있으면 실패합니다.
- `.github/workflows/publish-daily.yml`이 매일 KST 09:00에 빌드하고 변경분을 `main`에 커밋·푸시합니다. Cloudflare Pages는 `main` 푸시로 자동 배포됩니다.
- `data/`, `tools/`는 공개되면 안 되므로 `functions/_middleware.js`가 `/data/*`, `/tools/*`, `*.py`, `README.md` 요청을 404로 돌려보냅니다. (`.assetsignore`는 Cloudflare Workers 정적 자산용이며 Pages에서는 적용되지 않습니다.)

## 영문판(/en/)

같은 원고를 두 언어로 낸다. 한국어와 영문판은 같은 발행일 조건으로 함께 공개된다.

- 경로: `/en/`, `/en/leaders/`, `/en/stories/<slug>.html`, `/en/about/`, `/en/privacy/`, `/en/terms/`
- 상단 내비게이션의 `KR | EN` 버튼이 같은 편의 다른 언어 페이지로 바로 이동한다(홈·라인업·스토리·문서 페이지 모두).
- SEO: `<html lang="en">`, `og:locale`(en_US) + `og:locale:alternate`(ko_KR), `hreflang`(ko/en/x-default), 언어별 `canonical`, `sitemap.xml`의 `xhtml:link` 대응 URL.
- 영문 디자인은 한국어판과 같은 다크 시네마틱 시스템(`#121316` + `#E8A84C`)을 그대로 쓴다.
- 인용은 영문판에서 영어 원문을 본문에 두고, 원문이 영어가 아닌 경우(이순신·유관순)에만 작은 글씨로 원문을 덧붙인다.
- 원칙·개인정보·이용약관 영문판은 `python3 tools/build_en_docs.py`로 만든다(한국어판은 수동 관리).

## 로컬 확인

```bash
python3 -m http.server 8080 --directory .
# http://localhost:8080
```

## 배포

Cloudflare Pages 또는 정적 호스팅에 저장소를 연결하고, 빌드 명령 없이 출력 디렉터리를 저장소 루트로 지정합니다. GitHub Pages로 배포할 경우 프로젝트 경로(`/readersfiles/`)에서도 동작하도록 모든 내부 링크는 상대 경로입니다. 다만 `canonical`, `og:url`, `sitemap.xml`은 `https://readersfiles.pages.dev` 기준이므로, 실제 도메인이 다르면 아래처럼 바꿉니다.

```bash
grep -rl 'https://readersfiles.pages.dev' --include='*.html' --include='*.xml' . | xargs sed -i 's#https://readersfiles.pages.dev#https://실제도메인#g'
```

## 이메일 구독

홈과 모든 스토리 하단의 구독 카드는 `POST /api/subscribe`로 JSON을 보냅니다.

```json
{ "email": "reader@example.com", "consent": true, "source": "/stories/edison-1914.html" }
```

- 활성화: `assets/js/site.js`의 `SUBSCRIBE_ENDPOINT`를 `"/api/subscribe"`로 바꾸면 실제 요청을 보냅니다. 비어 있는 동안에는 요청 없이 준비 중 안내만 표시합니다.
- 성공: `2xx` 응답. 화면에 접수 안내를 표시합니다.
- 실패·미설정(404 포함): "구독 기능을 준비하고 있습니다" 안내를 표시하고 입력값을 전송하지 않습니다. 콘솔 오류를 던지지 않습니다.
- 서버 예시(Cloudflare Pages Functions + KV/D1 + Resend/Brevo): 이메일 형식 검증 → 동의 값 확인 → 저장 → 발송 대기열 등록 → `202` 응답.

## 콘텐츠 원칙

- 인물의 발언과 날짜는 공개 도메인 사료로 확인하고, 각 글의 `사료 노트`에 근거를 밝힙니다.
- 확인되지 않은 명언은 "널리 인용되는 말"로 표시합니다.
- 나이·연도·개수·횟수는 모두 아라비아 숫자로 적습니다. (67세, 13동, 10,000명)
- 인물 초상은 AI로 생성한 에디토리얼 이미지이며, 실제 사료 사진이 아닙니다. 모든 이미지 아래에 이 사실을 표기합니다.

## 라이선스

글과 편집 디자인 © 2026 LEADERS FILES. 인용은 출처와 링크를 밝혀 2~3문장까지 허용합니다. 초상 이미지는 사료 사진으로 재사용할 수 없습니다.
