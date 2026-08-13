# malgnblog — 프로젝트 규칙

맑은소프트 구글 SEO 비즈니스 블로그(blog.malgnsoft.com). 기업교육·HRD 담당자 타깃.

## 빌드 / 배포
- 빌드: `pip install -r requirements.txt && python build.py` → 산출물 `_deploy/public`
- 배포: **자체 웹서버** (Rocky Linux 9.5 / Apache 2.4.62 / Resin 4.0.67)
  - `main` push → GitHub Actions 빌드 → `deploy` 브랜치(`public_html/` 아래) → 서버 cron이 2분마다 `git reset`
  - 서버: git 루트 `/home/blog` · 웹루트 `/home/blog/public_html` · 데이터 `/home/blog/data`
  - 설정·설치문서는 `deploy/` (`apache-blog.conf` · `resin-blog.xml` · 서버담당자-설치가이드)
- 조회수 집계는 **Resin JSP** — 소스 `server/WEB-INF/`, 빌드가 웹루트 `WEB-INF/`로 복사.
  `/api/track`(수집) · `/api/stats`(대시보드용 JSON) · 저장 `/home/blog/data/stats.tsv`
- `netlify/`·`netlify.toml`·`.netlify/`는 **폐기된 옛 배포 잔재** — 참조·수정 금지

## 예약 발행
- 원고 front matter 에 `publish_at: 2026-08-10 09:00` (KST, 시각 생략 시 00:00). 그 시각 전까지는
  **사이트 출력에서 통째로 빠진다** — 페이지·홈·목록·카테고리·sitemap·RSS 어디에도 없다(draft 와 같은 취급)
- **`date` 는 적지 않아도 된다.** publish_at 이 있으면 발행일은 예약일로 자동 정렬된다(다르게 적으면 빌드가 덮어쓰고 경고)
- 예약이 풀리는 건 **예약 시각 이후 빌드가 한 번 돌 때**다. `deploy.yml` 의 `schedule`(10분마다)이 그 역할 →
  실제 노출은 **예약 시각 + 최대 15분**(GitHub schedule 은 정시를 보장하지 않는다)
- `draft: true` 는 예약보다 우선한다(항상 숨김). 예약을 취소하려면 publish_at 을 지우거나 미래로 미룬다
- publish_at 형식이 틀리면 **빌드가 멈춘다.** 오타를 무시하면 예약 글이 즉시 공개되기 때문
- 서버 반영: 저장소 Secret `BLOG_ADMIN_PW`(= 서버 `/home/blog/data/admin.pw`)가 등록돼 있으면
  Actions 가 배포 후 `/api/update` 를 호출해 자동 반영. 없으면 `/gamma` 의 [프로그램 갱신] 버튼을 눌러야 뜬다
- 예약 글은 **관리자 콘솔 `/gamma2`** 에서 `🕘 예약` 상태로 보인다(사이트에는 없음)

## 공개 갱신 페이지 `/refresh`
- 로그인 없이 **[프로그램 갱신]만** 있는 페이지. 관리자 로그인이 막혀도 사이트 반영을 되살리려는 장치
  (2026-08-12 장애: 갱신 버튼이 로그인 뒤에 있어 서버 담당자를 찾아야 했다)
- 서버쪽 짝은 `web.xml` 의 **`refreshOpen=true`** — `update.jsp` 가 이 값이 true 면 비밀번호 없이 실행한다.
  잠그려면 false. `/api/stats`(통계·글목록)는 **여전히 비밀번호가 필요하다** — 열린 건 갱신 하나뿐
- **`web.xml` 을 고친 배포는 곧바로 듣지 않는다.** git reset 으로 파일이 내려가도 Resin 이 웹앱을
  다시 배치하기 전까지는 **옛 context-param 이 살아 있다**(신설 스위치가 401·무시로 보인다).
  몇 초~수십 초 뒤 다시 시도할 것 — 코드가 틀린 게 아니다

## 관리자 콘솔에서 글쓰기 (`/gamma2`)
- **새 글 / 수정**: 콘솔 → `POST /api/stats?write=1`(write.jsp) → **GitHub `main` 에 커밋** →
  Actions 빌드 → `deploy` 브랜치 → **[프로그램 갱신]** 을 눌러야 사이트에 뜬다(저장 = 발행 아님)
- **서버에 직접 쓰지 않는 이유**: `update.jsp` 의 `git reset --hard` 가 워킹트리를 원격에 맞추므로
  서버 로컬 변경은 다음 갱신 때 소멸한다. 원고의 진실은 원격 `main` 이다
- **서버 준비물**: `/home/blog/data/github.token`(fine-grained PAT, Contents:write, 0600).
  없으면 저장이 `503 no_token` 으로 막힌다 — 절차는 `deploy/서버담당자-설치가이드.md` 3-7
- **front matter 는 통째로 다시 쓰지 않는다.** 콘솔이 아는 키의 '그 줄만' 갈아끼운다
  (`fmSet`). `faq`·`tags`·`cluster`·`thumbnail` 처럼 build.py 가 안 읽는 필드를
  재직렬화하다 잃는 사고를 막기 위해서다. 새 필드를 폼에 추가할 때도 이 방식을 지킬 것
- **본문에 표·인라인 SVG 가 있으면 콘솔이 마크다운 탭으로 고정한다**(`hasRawHtml`).
  위지윅 모드가 그 블록을 다시 써서 글을 조용히 깨뜨리기 때문
- 저자를 고르면 **네임택이 자동으로 따라온다** — 붙이는 주체는 빌드다(`NAMECARDS[author]`).
  그래서 콘솔 선택지는 `namecards.json` 에 실제로 있는 저자로 한정한다
- 에디터(TOAST UI)는 CDN 을 못 써서 `admin-console/vendor/` 에 벤더링 → 빌드가 `/gamma2/vendor/` 로 복사
- **JSP 를 고쳤으면 `web.xml` 의 `deployRev` 를 반드시 올린다** — 안 올리면 서버가 구 컴파일본을 계속 쓴다

## 단일 출처(SSOT) — 충돌 시 이게 최우선
- **사실·수치** = `_facts.md` (모든 글의 팩트 SSOT)
- **제품 기능·사양 인용** = `_product-lms.md`(맑은이러닝 LMS) · `_product-wecandeo.md`(위캔디오). 이 둘 밖의 제품 스펙 서술 금지
- **집필 기준** = `_writing-guide.md` 10원칙 통과해야 발행 후보. 톤 = `04_홍보_톤앤매너.md`

## 콘텐츠 규칙
- 배합: 정보(TOFU) 50 / 실무(MOFU) 35 / 제품·홍보(BOFU) 15
- 시각요소 3종만: HTML `<table>`(데이터·비교, 이미지 금지) / 인라인 SVG(`<title>`·`<desc>` 필수) / 지정 이미지. 그 외 금지
- 링크: 내부링크·이미지 **상대경로**, canonical·JSON-LD는 **절대경로**

## 상태
- 진행 현황은 `STATUS.md`가 단일 소스 (README "현재 상태" 아님)
