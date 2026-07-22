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
