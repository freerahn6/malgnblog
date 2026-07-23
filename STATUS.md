# 맑은소프트 블로그 (교육운영 노트)
> 갱신: 2026-07-23 · 24편 발행 · 배포: **자체 웹서버(Rocky 9.5 / Apache 2.4.62 / Resin 4.0.67)** — 코드·문서 준비 완료, 담당자 설치 대기

## 신규 콘텐츠 배치 (2026-07-22 확정, 팀장 안기범 큐레이션)

07-15 '추가주제 10선'은 **10편 전량 발행 완료**. 아래가 다음 5선이다. 배합은 취향이 아니라 산수로 결정됐다 — 28편 시점에 목표(50/35/15)에 닿으려면 **TOFU 4 + BOFU 1**이 유일해에 가깝다.

| 순위 | 주제 | 카테고리·퍼널 | 상태 |
|---|---|---|---|
| 1 | 민간자격증 등록 방법, 협회·기관이 처음 해야 하는 일 | certification·TOFU | **발행 완료(07-22)** |
| 2 | 서버 없이 자체 교육 영상 플랫폼 구축하기 (업로드→진도율 연동) | video·BOFU | 집필 중 |
| 3 | 신입사원 온보딩 교육, LMS로 설계하는 법 | hrd·TOFU | 대기 — **시즌성 7~9월** |
| 4 | 블렌디드 러닝 설계 가이드 (집합 출결 + 온라인 진도) | edutech·TOFU | 대기 |
| 5 | 교육 영상, 직접 만들까 사올까 (자체제작·구매·임대) | video·TOFU | 대기 |

- **다음 배치 예약**: news(CSAP·신뢰자산) BOFU 1편 + 「클라우드 LMS 보안·개인정보 심사 통과 가이드」(MOFU). 후자는 근거가 가장 탄탄한데 이번 배합에 자리가 없어 유예한 것이다.
- 5선 근거·카니발라이제이션 판정·내부링크 설계는 대화 이력 기준이며, 재판단이 필요하면 팀장(b1)에게 다시 물을 것.

## 프로그램 갱신 버튼 추가 (2026-07-23)
- **배경**: 회사 환경상 cron 자동 갱신 적용이 어렵다는 COO 판단 → 서버가 최초 1회만 당겨오고 이후 멈춘 상태였음(실측: 홈은 07-16 빌드, 07-22 이후 새 글 404). DNS·서버 설치는 이미 완료돼 있었음(자체서버가 서빙 중)
- **결정**: cron 대신 `/gamma` 대시보드에 **[프로그램 갱신] 버튼** → `POST /api/update` → 서버에서 `git fetch` + `git reset --hard origin/deploy` 실행, 결과를 화면에 표시. 소스 `server/WEB-INF/jsp/update.jsp`
- **d2 적대 검토 반영**: ① pull(merge)은 이 배포모델과 충돌 → fetch+reset로 교정 ② 익명스레드의 non-final 캡처(Java 6/7 컴파일 실패 위험) → 로컬 final ③ 손자 프로세스 잔존 대비 destroyForcibly 2차 종료 ④ 기본 비번 `gamma`가 이제 배포 트리거까지 여는 문제 → 문서에 교체 경고 강화
- **안전장치**: 비번 인증·POST 전용·셸 미경유(인자 배열)·60초 타임아웃·동시 1건·`updateEnabled` 스위치. Apache는 `/api/update`만 timeout=90으로 별도 프록시
- **남은 것**: 서버에서 Resin 계정의 `/home/blog` git 쓰기 권한 확인 + 비번 교체(`admin.pw`). JSP 실측(`curl -X POST /api/update` → 401)은 배포 후 첫 확인

## 자체서버 대응 완료 (2026-07-22)
- **확정 환경**: Rocky Linux 9.5 + Apache 2.4.62 + Resin 4.0.67. git 루트 `/home/blog` · 웹루트 `/home/blog/public_html` · 데이터 `/home/blog/data`
- **배포 경로 확정**: `main` push → Actions 빌드 → `deploy` 브랜치(`public_html/` 아래) → 서버 cron 2분마다 `git fetch && git reset --hard`. **rsync 불필요**(브랜치 트리 = `/home/blog` 모양)
- **조회수/`admin` 통계 부활**: Netlify Functions+Blobs 종속을 끊고 **Resin JSP로 재구현**(`server/WEB-INF/`). `/api/track`·`/api/stats`, 저장은 웹루트 밖 `/home/blog/data/stats.tsv`. 대시보드 응답 형태는 그대로라 `/admin` 코드 무수정
- **산출물**: `deploy/apache-blog.conf`(vhost·WEB-INF 차단·/api → Resin 프록시) · `deploy/resin-blog.xml`(host/web-app) · `deploy/서버담당자-설치가이드.md`(SELinux·권한·cron 포함). nginx 설정은 폐기
- **레포 공개 전환·`deploy` 브랜치 생성 완료(07-22)**: 익명 접근 실측 확인(GitHub API 200, raw 200). 브랜치 최상위는 `public_html/` 하나로 정리됨(옛 평면 구조 잔재 제거)
- **관리자 대시보드 경로 `/admin` → `/gamma`(07-22)**: `build.py`의 `ADMIN_PATH` 상수 한 곳에서 관리. `track.jsp`의 집계 제외 조건은 서버 코드라 하드코딩 — **경로 변경 시 두 곳을 같이 고칠 것.** robots.txt의 `Disallow`는 제거(경로를 광고하는 꼴이라), 색인 차단은 페이지 meta noindex로
- **잠복 결함 3건 동시 수정(07-22)**: ① `deploy.yml`의 `paths-ignore: '**.md'`가 `articles/*.md`까지 걸러 **발행 push가 통째로 무시**되던 문제 → `'*.md'`로 축소 ② 건전성 검사에 WEB-INF 확인 추가(빠지면 `rsync --delete`가 서버 API를 지우고도 초록불) ③ 원고 수 대비 페이지 수 검사로 교체
- **남은 것**: ① 서버 담당자 설치 ② DNS를 호스트잇에서 자체서버 A레코드로 + SSL

## 배포 이전 결정 (2026-07-16, 이력)
- **결정**: Netlify·Cloudflare 둘 다 버리고 **회사 자체 웹서버로 이전.** 작업일 **2026-07-21(화).**
- **배경**: Netlify 무료 크레딧 소진(이번주 가입, 리셋 ~1개월) → 프로덕션 배포 동결. Cloudflare는 외부 DNS(호스트잇) 커스텀도메인 검증 벽(과거 2차도메인 연결 실패 원인).
- **화요일까지 방침**: 아무것도 손대지 않고 **Netlify에 그대로 얹어만 둔다.** 추가 배포·크레딧 조치·수선 없음. 최신 반영은 07-21 자체서버 이전 때 한 번에.
  - `blog.malgnsoft.com` → **Netlify(merry-snickerdoodle-74abba.netlify.app)** CNAME, **07-14 옛 빌드에 동결**된 채 유지(의도된 방치).
  - 최신본(23편·메뉴개편·에듀테크 새글+커버)은 **https://malgnblog.freerahn6.workers.dev (Cloudflare Workers)** 에 미리보기로만 존재 — 유지보수 안 함.
- **이전 시 체크리스트(화요일 준비물)**: ① 자체서버 정적 서빙 경로(빌드 산출물 `_deploy/public` 업로드) ② `blog.malgnsoft.com` DNS를 호스트잇에서 자체서버 **A레코드**로 변경 + SSL(Let's Encrypt 등) ③ 조회수/`admin` 통계는 Netlify Functions+Blobs 종속 → 자체서버용으로 재구현 필요(또는 무료 분석 대체) ④ 네이버/구글 인증 메타·robots·sitemap 도메인 그대로 유지.

## 지금 진행 중
- 무엇: 총 **24편** 발행 — 신규 5선 중 2번(위캔디오 BOFU) 집필 중 + 자체서버 설치 대기 + 색인 안착 대기
- 다음 게이트: ① **서버 담당자 설치 + DNS 전환** ② 5선 잔여 4편 완성 ③ 서치콘솔/네이버 색인 확인

## 최근 완료 (5~7개만)
- 신규 발행(07-22): 「민간자격증 등록 방법, 협회·기관이 처음 해야 하는 일」(certification·TOFU, 한다현). 제도가 본체인 글이라 **감마가 1차 출처 대조 검증**(PQI 통계·자격기본법 제17·33조·공인 요건 전부 일치). 근거 없는 등록면허세·접수창 규정·체감 소요기간은 미기재. 커버는 지정 이미지 사용
- 자체서버 이전 대응 일체(07-22): Apache/Resin 설정·설치가이드·조회수 JSP 재구현·배포 파이프라인 구조 변경 (위 섹션 참조)
- 관리자 경로 `/admin` → `/gamma`(07-22)
- 신규 발행(07-16): 「2026 에듀테크 트렌드 5가지와 운영자 대응 전략」(edutech·TOFU, 이채영)
- 상단 메뉴 링크 수정 + 홈/전체보기 분리(`/all/` 20개 페이징)
- 네이버 대응: RSS 피드 + robots에 Yeti 명시 + 서치어드바이저 인증 / 구글 서치콘솔 소유권 확인

## 열린 이슈
- **자체서버 설치 대기** — 담당자에게 `deploy/` 3종(설치가이드·apache-blog.conf·resin-blog.xml) 전달 필요. 그 전까지 blog.malgnsoft.com은 Netlify 07-14 옛 빌드로 동결(의도된 방치)
- **Apache↔Resin 연결 방식 미확인** — 기본은 mod_proxy(127.0.0.1:8080). 서버가 mod_caucho를 쓰고 있거나 Resin 포트가 다르면 `apache-blog.conf`에서 조정 필요(주석에 대안 명시)
- **JSP 실측 미완(JDK 없음)** — 로컬에 Java가 없어 컴파일·기동 검증 불가. 설치 시 `curl -X POST /api/track` → 204 확인이 첫 실측. 404면 `<jsp-file>`의 WEB-INF 경로 매핑 문제이므로 JSP를 `/api/` 아래로 옮기는 폴백 필요
- **대시보드 비밀번호 기본값(`gamma`)이 공개 저장소에 노출** — 설치 시 서버의 `/home/blog/data/admin.pw`로 반드시 교체. **경로도 `gamma`라 비밀번호는 경로와 다른 값으로 할 것**(가이드에 명시)
- **누적 조회수 0부터 재시작** — Netlify Blobs 데이터는 이관하지 않음(의도)
- README.md "현재 상태" 문구가 실제 진척(24편)보다 뒤처짐 → 다음 정리 시 동기화
- 콘텐츠 배합 현황(24편): TOFU 11(46%)/MOFU 10(42%)/BOFU 3(12%) — 목표 50/35/15에 한 걸음 접근. 5선 잔여 4편(BOFU 1 + TOFU 3)을 마치면 28편에서 **14/10/4 = 50.0/35.7/14.3%**로 세 축 모두 오차 1%p 이내
- 발행글 24편 중 `/contact/` 링크는 빌드가 문의 URL로 치환(`build.py`) — 깨진 링크 아님. 점검 시 오인 주의
