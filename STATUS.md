# 맑은소프트 블로그 (교육운영 노트)
> 갱신: 2026-07-22 · 배포: **자체 웹서버(Rocky 9.5 / Apache 2.4.62 / Resin 4.0.67)** — 서버 반입 준비 완료, 담당자 설치 대기

## 자체서버 대응 완료 (2026-07-22)
- **확정 환경**: Rocky Linux 9.5 + Apache 2.4.62 + Resin 4.0.67. git 루트 `/home/blog` · 웹루트 `/home/blog/public_html` · 데이터 `/home/blog/data`
- **배포 경로 확정**: `main` push → Actions 빌드 → `deploy` 브랜치(`public_html/` 아래) → 서버 cron 2분마다 `git fetch && git reset --hard`. **rsync 불필요**(브랜치 트리 = `/home/blog` 모양)
- **조회수/`admin` 통계 부활**: Netlify Functions+Blobs 종속을 끊고 **Resin JSP로 재구현**(`server/WEB-INF/`). `/api/track`·`/api/stats`, 저장은 웹루트 밖 `/home/blog/data/stats.tsv`. 대시보드 응답 형태는 그대로라 `/admin` 코드 무수정
- **산출물**: `deploy/apache-blog.conf`(vhost·WEB-INF 차단·/api → Resin 프록시) · `deploy/resin-blog.xml`(host/web-app) · `deploy/서버담당자-설치가이드.md`(SELinux·권한·cron 포함). nginx 설정은 폐기
- **남은 것**: ① 레포 공개 전환 + `deploy` 브랜치 최초 생성 ② 서버 담당자 설치 ③ DNS를 호스트잇에서 자체서버 A레코드로 + SSL

## 배포 이전 결정 (2026-07-16, 이력)
- **결정**: Netlify·Cloudflare 둘 다 버리고 **회사 자체 웹서버로 이전.** 작업일 **2026-07-21(화).**
- **배경**: Netlify 무료 크레딧 소진(이번주 가입, 리셋 ~1개월) → 프로덕션 배포 동결. Cloudflare는 외부 DNS(호스트잇) 커스텀도메인 검증 벽(과거 2차도메인 연결 실패 원인).
- **화요일까지 방침**: 아무것도 손대지 않고 **Netlify에 그대로 얹어만 둔다.** 추가 배포·크레딧 조치·수선 없음. 최신 반영은 07-21 자체서버 이전 때 한 번에.
  - `blog.malgnsoft.com` → **Netlify(merry-snickerdoodle-74abba.netlify.app)** CNAME, **07-14 옛 빌드에 동결**된 채 유지(의도된 방치).
  - 최신본(23편·메뉴개편·에듀테크 새글+커버)은 **https://malgnblog.freerahn6.workers.dev (Cloudflare Workers)** 에 미리보기로만 존재 — 유지보수 안 함.
- **이전 시 체크리스트(화요일 준비물)**: ① 자체서버 정적 서빙 경로(빌드 산출물 `_deploy/public` 업로드) ② `blog.malgnsoft.com` DNS를 호스트잇에서 자체서버 **A레코드**로 변경 + SSL(Let's Encrypt 등) ③ 조회수/`admin` 통계는 Netlify Functions+Blobs 종속 → 자체서버용으로 재구현 필요(또는 무료 분석 대체) ④ 네이버/구글 인증 메타·robots·sitemap 도메인 그대로 유지.

## 지금 진행 중
- 무엇: 총 23편 발행 — 자체서버 설치 대기 + 캘린더 잔여편 집필 + 구글·네이버 색인 안착 대기
- 다음 게이트: ① **서버 담당자 설치 + DNS 전환** ② 캘린더 잔여편 완성 ③ 서치콘솔/네이버 색인 확인

## 최근 완료 (5~7개만)
- 신규 발행(07-16): 「2026 에듀테크 트렌드 5가지와 운영자 대응 전략」(edutech·TOFU, 이채영) — TOFU 배합 보강
- 상단 메뉴 링크 수정(홈/카테고리 href="#" 깨짐) + 홈/전체보기 분리(전체보기 `/all/` 리스트·20개 페이징)
- 신규 10편 발행 완성(q3 검수 반영, 1~3차)
- 게시일 재배정: 22편 전체 하루 1편으로(2026-06-23~07-14)
- 관리자 통계 대시보드 `/admin` + 조회수 집계(Netlify Functions+Blobs)
- 네이버 대응: RSS 피드 + robots에 Yeti 명시 + 서치어드바이저 인증
- 구글 서치콘솔 사이트 소유권 확인 메타 태그(홈)

## 열린 이슈
- **자체서버 설치 대기** — 담당자에게 `deploy/` 3종(설치가이드·apache-blog.conf·resin-blog.xml) 전달 필요. 그 전까지 blog.malgnsoft.com은 Netlify 07-14 옛 빌드로 동결(의도된 방치)
- **Apache↔Resin 연결 방식 미확인** — 기본은 mod_proxy(127.0.0.1:8080). 서버가 mod_caucho를 쓰고 있거나 Resin 포트가 다르면 `apache-blog.conf`에서 조정 필요(주석에 대안 명시)
- **JSP 실측 미완(JDK 없음)** — 로컬에 Java가 없어 컴파일·기동 검증 불가. 설치 시 `curl -X POST /api/track` → 204 확인이 첫 실측. 404면 `<jsp-file>`의 WEB-INF 경로 매핑 문제이므로 JSP를 `/api/` 아래로 옮기는 폴백 필요
- **`/admin` 비밀번호 기본값(`gamma`)이 공개 저장소에 노출** — 설치 시 서버의 `/home/blog/data/admin.pw`로 반드시 교체(가이드에 명시)
- **누적 조회수 0부터 재시작** — Netlify Blobs 데이터는 이관하지 않음(의도)
- README.md "현재 상태" 문구가 실제 진척(23편)보다 뒤처짐 → 다음 정리 시 동기화
- 콘텐츠 배합 현황(23편): TOFU 10(43%)/MOFU 10(43%)/BOFU 3(13%) — 목표 50/35/15 대비 여전히 TOFU 부족·MOFU 과다. 다음 발행도 TOFU 우선 권장
