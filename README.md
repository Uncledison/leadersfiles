# LEADERS FILES

실패를 넘은 사람들의 1차 기록 아카이브. 위대한 사람들의 성공담이 아니라, 가장 아팠던 하루를 날짜와 숫자, 그날 남긴 말로 기록하는 정적 매거진입니다.

- 라이브(예정): https://readersfiles.com
- 저장소: https://github.com/oraclekidz/readersfiles

## 구조

```
index.html                 매거진 홈 (대표 기록, 발행 목록, 구독, 에디토리얼 원칙)
stories/edison-1914.html   에디슨 · 1914년 12월 9일 웨스트오렌지 화재
stories/lincoln-1858.html  링컨 · 1858년 상원 낙선과 1860년
stories/tesla-1895.html    테슬라 · 1895년 3월 13일 실험실 화재
leaders/index.html         후보 30인 라인업 (분류 필터)
about/index.html           에디토리얼 원칙
privacy/index.html         개인정보 처리방침
terms/index.html           이용약관
404.html                   오류 페이지
assets/css/site.css        디자인 시스템 (다크 시네마틱)
assets/js/site.js          타임라인, 라인업 필터, 공유, 구독 폼
assets/img/                초상(WebP/JPG)과 공유 이미지
sitemap.xml, robots.txt
```

빌드 도구나 패키지는 필요 없습니다. 정적 파일 그대로 배포합니다.

## 로컬 확인

```bash
python3 -m http.server 8080 --directory .
# http://localhost:8080
```

## 배포

Cloudflare Pages 또는 정적 호스팅에 저장소를 연결하고, 빌드 명령 없이 출력 디렉터리를 저장소 루트로 지정합니다. GitHub Pages로 배포할 경우 프로젝트 경로(`/readersfiles/`)에서도 동작하도록 모든 내부 링크는 상대 경로입니다. 다만 `canonical`, `og:url`, `sitemap.xml`은 `https://readersfiles.com` 기준이므로, 실제 도메인이 다르면 아래처럼 바꿉니다.

```bash
grep -rl 'https://readersfiles.com' --include='*.html' --include='*.xml' . | xargs sed -i 's#https://readersfiles.com#https://실제도메인#g'
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
