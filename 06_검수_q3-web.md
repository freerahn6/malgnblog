# 06. 웹 정밀 검수 리포트 (q3-web)

- **대상**: https://malgnblog.freerahn6.workers.dev (Cloudflare Worker, static assets)
- **소스**: `C:/job/blog/` — `articles/*.md` 12편, `_deploy/build.py`, `_deploy/img_map.json`, `_preview/*.html`
- **검수일**: 2026-07-13
- **검수자**: q3 (웹 특화 QA)
- **방법**: 소스 정독 + 라이브 13개 URL 전수 curl(상태코드·본문 파싱) + 이미지 참조 12건 개별 HTTP 확인 + WCAG 명도대비 계산

## 판정

**배포 불가 (BLOCKER). 즉시 롤백 또는 noindex 처리 권고.**

현재 상태로 검색엔진에 노출되면 (a) 12편 전편에서 이미지가 깨진 채로, (b) "실제 화면 캡처는 발행 시 삽입"이라는 **미완성 실토 문구가 독자에게 그대로 보이는 채로**, (c) canonical이 404를 가리켜 **색인 자체가 안 되는 채로** 크롤링된다. 구글 SEO 블로그라는 프로젝트 목적이 정면으로 무너진다.

### 심각도별 집계

| 심각도 | 건수 | 항목 |
|---|---|---|
| **치명** | **4** | C-1 본문 이미지 12/12 전량 404 · C-2 canonical이 레거시 사이트/404를 가리킴 · C-3 카테고리 인덱스 부재로 글로벌 내비 전량 404 · C-4 플레이스홀더 실토 문구·내부 경로 프로덕션 노출 |
| **중대** | 11 | M-1~M-11 (홈 내비 무동작, 홈 CTA 부재, featured 미삽입, FAQ 36건 드롭, JSON-LD 전무, og:image 부재, sitemap 부재, 상호링크 7건 404, 커스텀 404 부재, 모바일 내비·목차 소실, 미래 날짜) |
| **경미** | 8 | m-1~m-8 (명도대비, CLS, lazy, 경로 혼용, 캐시 헤더, favicon, 빌드 견고성, 빌드 재현 불가) |

> **표기 규약**: `[확인]` = curl 응답/파일 라인으로 실증함. `[추론]` = 코드 근거에 기반한 판단이나 실물 미확인.

---

# SECTION 1. 이미지 404 (치명 C-1)

## 1.1 깨진 이미지 전체 목록 — 12/12 전량 404 `[확인]`

12편 각각이 본문 이미지 `<img>`를 정확히 1개씩 갖고 있고, **12개 전부 HTTP 404**다. 예외 없다.

| # | 참조 아티클 (slug) | 원고 라인 | 원고의 src | 라이브 기대 경로 (해석 결과) | 상태 |
|---|---|---|---|---|---|
| 1 | certificate-auto-issue | `articles/certificate-auto-issue.md:60` | `./images/certificate-template-html-editor.webp` | `/hrd/certificate-auto-issue/images/certificate-template-html-editor.webp` | **404** |
| 2 | certification-system-build-guide | `:57` | `/assets/img/certification/qualification-flow-diagram.webp` | `/assets/img/certification/qualification-flow-diagram.webp` | **404** |
| 3 | legal-mandatory-training-online | `:106` | `./images/legal-mandatory-training-completion-list.webp` | `/hrd/legal-mandatory-training-online/images/legal-mandatory-training-completion-list.webp` | **404** |
| 4 | lms-case-studies-3 | `:154` | `./images/lms-dashboard-overview.webp` | `/news/lms-case-studies-3/images/lms-dashboard-overview.webp` | **404** |
| 5 | lms-selection-guide-for-corporate-training | `:60` | `./images/lms-checklist-dashboard.webp` | `/lms/lms-selection-guide-for-corporate-training/images/lms-checklist-dashboard.webp` | **404** |
| 6 | lms-vs-lxp | `:132` | `./images/lms-vs-lxp-layers.webp` | `/edutech/lms-vs-lxp/images/lms-vs-lxp-layers.webp` | **404** |
| 7 | online-exam-anti-cheating-setup | `:128` | `./images/online-exam-registration.webp` | `/lms/online-exam-anti-cheating-setup/images/online-exam-registration.webp` | **404** |
| 8 | refund-training-lms-operation-guide | `:29` | `/assets/img/hrd/refund-training-lms-operation-guide/overview.webp` | `/assets/img/hrd/refund-training-lms-operation-guide/overview.webp` | **404** |
| 9 | self-hosted-vs-cloud-lms | `:131` | `./images/self-hosted-vs-cloud-lms-risk-console.webp` | `/lms/self-hosted-vs-cloud-lms/images/self-hosted-vs-cloud-lms-risk-console.webp` | **404** |
| 10 | what-is-lms | `:115` | `./images/lms-dashboard-overview.webp` | `/lms/what-is-lms/images/lms-dashboard-overview.webp` | **404** |
| 11 | what-is-microlearning | `:103` | `./images/microlearning-admin.webp` | `/edutech/what-is-microlearning/images/microlearning-admin.webp` | **404** |
| 12 | why-own-video-platform | `:131` | `./images/wecandeo-callback-setting.webp` | `/video/why-own-video-platform/images/wecandeo-callback-setting.webp` | **404** |

추가로 **front matter `thumbnail:` 12건**도 전부 존재하지 않는 .webp를 가리킨다(단 build.py가 이 필드를 읽지 않으므로 렌더 결과에는 영향 없음 → M-6 참조).

## 1.2 근본 원인 — **단정한다: "실물 파일이 제작된 적 없음"** `[확인]`

두 후보(① 이미지는 있는데 build.py가 복사를 안 함 ② 이미지가 아예 없음) 중 **②가 확정**이다. 근거는 세 겹이다.

**근거 1 — 프로젝트 전체에 이미지 바이너리가 0개.**
```
$ cd C:/job/blog && find . -iname "*.webp" | wc -l
0
```
`.webp`뿐 아니라 `.png/.jpg/.jpeg/.svg/.gif`까지 확장해도 **0건**. 복사할 원본 자체가 존재하지 않는다. (히어로 이미지는 파일이 아니라 `img_map.json` 안의 base64 data URI로만 존재한다.)

**근거 2 — 원고가 스스로 "플레이스홀더"라고 자백하고 있다.**
`articles/what-is-lms.md`의 figure 블록이 라이브에 그대로 출력됨:
```html
<figure>
<!-- placeholder: 실제 관리자 대시보드 스크린샷으로 교체 예정 (C:\job\data\매뉴얼\...\대시보드) -->
<img src="./images/lms-dashboard-overview.webp" alt="LMS 관리자 대시보드에서 …" width="1200" height="675">
<figcaption>… (실제 화면 캡처는 발행 시 삽입)</figcaption>
</figure>
```
집필 시점에 **이미지를 나중에 만들 예정으로 두고 태그만 먼저 박은 것**이다. 6개 페이지에 `<!-- placeholder: … -->` 주석이, 7개 페이지에 "교체 예정/후속 삽입/placeholder"라고 적힌 figcaption이 남아 있다(→ C-4).

**근거 3 — build.py에 이미지 복사 단계가 아예 설계되지 않았다.**
`_deploy/build.py` 전체(171라인)에 `shutil`, `copy`, `copytree` 호출이 없다. 출력은 `{OUT}/index.html`(L168)과 `{OUT}/{cat}/{slug}/index.html`(L115) 두 종류의 HTML **뿐**이다. 정적 자산 파이프라인이 존재하지 않는다.

> 즉 build.py의 "복사 단계 부재"는 **부차적 원인**이다. 복사 단계를 넣어도 복사할 파일이 없다. **1차 원인은 자산 미제작**이며, build.py의 자산 파이프라인 부재는 그 미제작을 배포 전에 잡아내지 못한 **2차 원인(안전망 부재)**이다.

## 1.3 수정안 — 선택지별

### 선택지 A (권장) — 실물 webp 제작 → 절대경로 `/assets/img/` 통일 → build.py에 복사 단계 추가

가장 정공법이고, 원고의 alt·figcaption(이미 고품질로 작성돼 있음)을 살린다.

1. **자산 제작**: 원고 주석이 가리키는 `C:\job\data\매뉴얼\...`의 관리자 화면 캡처 12종을 webp로 변환. 권장 규격 1200×675(원고 width/height와 일치), 품질 80, 개당 60~120KB.
2. **경로 통일**: 전 원고를 `/assets/img/{category}/{slug}/{name}.webp` 절대경로로 변경 (→ 1.4에서 근거 상술).
3. **디렉터리**: `C:/job/blog/assets/img/...`에 실물 배치.
4. **build.py에 복사 + 검증 단계 추가** (핵심: 자산 누락 시 빌드를 실패시켜 다시는 이 사고가 안 나게 함):

```python
import shutil, sys
ASSETS = "C:/job/blog/assets"          # 원본 자산 루트

# ── 빌드 말미에 추가 ──────────────────────────────────
# 1) 정적 자산 통째로 복사
if os.path.isdir(ASSETS):
    shutil.copytree(ASSETS, f"{OUT}/assets", dirs_exist_ok=True)

# 2) 산출 HTML이 참조하는 모든 로컬 이미지가 실제로 있는지 검증 (게이트)
missing = []
for root, _, files in os.walk(OUT):
    for fn in files:
        if not fn.endswith('.html'):
            continue
        page = os.path.join(root, fn)
        html_txt = open(page, encoding='utf-8').read()
        pg_url = '/' + os.path.relpath(root, OUT).replace('\\', '/').strip('./')
        for src in re.findall(r'<img[^>]+src="(?!data:)([^"]+)"', html_txt):
            rel = src[1:] if src.startswith('/') else f"{pg_url}/{src[2:] if src.startswith('./') else src}"
            if not os.path.isfile(os.path.join(OUT, rel.lstrip('/'))):
                missing.append((page, src))
if missing:
    for p, s in missing:
        print(f"MISSING ASSET: {s}  (referenced by {p})")
    sys.exit(f"BUILD FAILED: {len(missing)} broken image reference(s)")
```
> 이 검증 게이트만 있었어도 12건 전량 404가 배포되는 일은 없었다. **A안을 택하든 B안을 택하든 이 게이트는 반드시 넣어라.**

5. **플레이스홀더 흔적 제거**: figcaption의 "(실제 화면 캡처는 발행 시 삽입)" 류 문구 7건과 `<!-- placeholder … -->` 주석 6건 삭제 (→ C-4).

### 선택지 B (임시방편) — 이미지 참조 제거

발행 일정을 못 미루는 경우의 최소 조치. **본문의 `<figure>` 블록 중 `<img>`를 쓰는 것만 통째로 삭제**한다(alt·figcaption도 함께). 인라인 SVG 다이어그램(`<figure><svg role="img" …>`)은 **정상 렌더되므로 절대 지우지 말 것** — self-hosted-vs-cloud-lms·what-is-lms 등에 있는 SVG는 `role="img"`/`<title>`/`<desc>`까지 갖춘 접근성 우수 자산이다 `[확인]`.

- 장점: 즉시 깨진 이미지 0건.
- 단점: 12편 모두 "화면 캡처가 하나도 없는 LMS 소개 글"이 된다. 제품 신뢰도·체류시간·SEO(이미지 검색) 손실. **BOFU 전환 목적에 정면으로 반한다.**
- 판단: **B는 A로 가는 중간 기착지로만 써라.** 최종 상태로 두면 안 된다.

### 선택지 C (비권장) — 히어로처럼 data URI 인라인
img_map.json 방식을 본문 이미지까지 확대하는 것. 페이지 무게가 이미 임계(홈 667KB)라 **더 악화시킬 뿐**이다. 캐시도 안 된다. 채택하지 말 것.

## 1.4 경로 규약: 상대경로 vs 절대경로 — **`/assets/img/` 절대경로로 통일할 것** `[확인]+[추론]`

**현황: 규약 위반이 맞다.** `README.md:18`은 "내부링크·이미지 **상대경로**"를 확정 방향으로 적었는데, 실제로는 10편이 `./images/`(상대), 2편이 `/assets/img/`(절대)로 **혼용**돼 있다. 최소한 일관성 위반이다.

**그런데 통일 방향은 README의 반대여야 한다.** README의 "이미지 상대경로" 지침 자체가 이 사이트 구조에서 **오히려 해롭다.** 근거:

1. **URL이 디렉터리형이라 상대경로가 페이지 경로에 종속된다.** 페이지 URL이 `/lms/what-is-lms/`이므로 `./images/foo.webp`는 `/lms/what-is-lms/images/foo.webp`로 해석된다 `[확인 — 라이브 404 경로가 정확히 이렇게 찍힘]`. 즉 **아티클마다 별도 images 디렉터리를 파야 한다.**
2. **공유 이미지가 물리적으로 중복된다.** `lms-dashboard-overview.webp`는 **what-is-lms와 lms-case-studies-3 두 편이 함께 참조**한다 `[확인]`. 상대경로를 유지하면 동일 바이너리를 `/lms/what-is-lms/images/`와 `/news/lms-case-studies-3/images/` **두 곳에 복제**해야 한다. 절대경로면 `/assets/img/common/lms-dashboard-overview.webp` 하나로 끝난다.
3. **카테고리 이동 시 전량 깨진다.** 아티클의 `category:`를 바꾸면 URL이 바뀌고 → 상대경로 이미지의 실제 경로도 전부 바뀐다. 절대경로는 무영향.
4. 상대경로의 유일한 장점(도메인 이전 시 자유로움)은 **루트 절대경로(`/assets/…`)도 똑같이 갖는다.** 도메인이 바뀌어도 `/assets/…`는 그대로 유효하다. README가 경계한 건 `https://…` 풀 URL일 텐데, 루트 절대경로는 거기 해당하지 않는다.

**결론 및 조치:**
- 전 원고의 이미지 src를 `/assets/img/{category}/{slug}/{name}.webp` (공유 자산은 `/assets/img/common/`)로 통일.
- `README.md:18`을 **"내부링크·이미지 = 루트 절대경로(`/…`) / canonical·JSON-LD = 풀 절대 URL"** 로 개정. 현재 문구는 구현과 어긋날 뿐 아니라 기술적으로도 틀렸다.
- 참고로 **내부링크는 이미 전부 루트 절대경로**(`](/lms/what-is-lms/)`)로 쓰이고 있다 `[확인]`. 즉 README의 "내부링크 상대경로" 지침도 이미 사문화됐다. 실태를 규약으로 정식화하는 게 맞다.

## 1.5 히어로 커버리지 — **문제 없음. 제기된 가설은 반증됨** `[확인]`

의뢰서의 3번 가설("img_map 누락 → `COVERS[1]` 폴백 → 엉뚱한 글에 같은 이미지")은 **사실이 아니다.** 실측 결과:

- `img_map.json` 키 **12개** ↔ 아티클 slug **12개** → **정확히 일치. 차집합 양방향 모두 공집합.**
- 12개 data URI **전부 서로 다름** (중복 0건). 히어로가 재사용되는 글은 없다.
- 따라서 `build.py:110`의 `hero=IMG.get(a['slug'], COVERS[1])` 폴백은 **한 번도 발동하지 않는다.**
- 의뢰서가 지목한 `COVER` 딕셔너리(`build.py:33-36`, `lms-vs-lxp:6`·`certificate-auto-issue:2` 재사용이 보이는 그것)는 **정의만 되고 어디서도 참조되지 않는 dead code**다. 라이브에 영향 없음. (→ 정리 대상, m-7)

**단, 폴백 자체는 위험하다.** 새 아티클을 추가하고 img_map 갱신을 잊으면 조용히 `COVERS[1]`(= what-is-lms의 커버)이 붙는다. 실패가 눈에 안 보인다.
```python
# build.py:110 — 교체 권고
if a['slug'] not in IMG:
    sys.exit(f"BUILD FAILED: img_map.json에 히어로 없음 → {a['slug']}")
hero = IMG[a['slug']]
```

## 1.6 이미지 접근성·CLS·lazy `[확인]`

| 항목 | 결과 |
|---|---|
| **alt 존재** | 본문 이미지 12/12 **모두 있음**. 품질도 우수 — 화면 내용을 구체적으로 서술("맑은이러닝 연수관리의 이수 목록 화면에서 대상자별 필수과정·선택과정·수료합계와 이수 재산정 기능을 확인하는 관리자 화면"). **이 항목은 합격.** |
| **width/height** | 12건 중 **9건만 지정**. **3건 누락** → CLS 유발: `certification-system-build-guide`, `lms-selection-guide-for-corporate-training`, `refund-training-lms-operation-guide` |
| **loading="lazy"** | 본문 이미지 **12건 전부 미지정**. 히어로도 미지정 |
| **홈 카드** | `loading="lazy"` 12건 **있음**. 그러나 **width/height 없음** → 홈에서 카드 12개 CLS |
| **홈 카드 lazy의 함정** | 카드 이미지가 **data URI**라 `loading="lazy"`는 **아무 효과가 없다**. 네트워크 요청이 없으므로 지연할 대상이 없고, 502KB는 HTML에 이미 들어와 있다 `[확인 — img_map 총량 502KB]` |
| **FAB 버튼 아이콘** | `<img src="data:…" alt="">` — 빈 alt. 단 `<button aria-label="맑은소프트 바로가기 메뉴 열기">`가 접근명을 제공하므로 **올바른 처리** `[확인]` |

---

# SECTION 2. 치명 결함 (C-2 ~ C-4)

## C-2. canonical이 **404 또는 무관한 레거시 사이트**를 가리킨다 — SEO 전면 무력화 `[확인]`

### 사실관계: `blog.malgnsoft.com`은 "미연결"이 아니다. **이미 다른 서비스가 점유 중이다.**

의뢰서와 README(`:17`)는 "도메인 추후 연결 / 아직 미연결"을 전제했다. **이 전제가 틀렸다.**

```
$ nslookup blog.malgnsoft.com
Address: 221.143.42.211          ← www.malgnsoft.com과 동일 IP

$ curl -sD- https://blog.malgnsoft.com/
HTTP/1.1 302 Found
Server: Apache/2.4.62 (Rocky Linux) OpenSSL/3.2.2 Resin/4.0.67
Location: https://blog.malgnsoft.com/main/index.jsp     → 200
   <title>국내 1위 맑은소프트 이러닝솔루션</title>       ← 회사 메인 사이트

$ curl -sD- https://blog.malgnsoft.com/lms/what-is-lms/
HTTP/1.1 404 Not Found                                   ← 아티클 canonical 목적지
```

**A 레코드가 이미 존재**하며 레거시 Apache/Resin JSP 서버(회사 대표 홈페이지)로 향한다. 와일드카드가 아니다(임의 서브도메인은 NXDOMAIN) — **의도적으로 등록된 레코드**다.

### 결과: 배포된 13개 페이지 전부가 잘못된 canonical을 선언한다 `[확인]`

| 페이지 | 선언한 canonical | 그 URL의 실제 응답 |
|---|---|---|
| 홈 (`/`) | `https://blog.malgnsoft.com/` | **302 → 회사 메인 홈페이지** (블로그와 무관한 콘텐츠) |
| 아티클 12편 | `https://blog.malgnsoft.com/{cat}/{slug}/` | **404** (전부) |

`build.py:77`이 하드코딩:
```python
<link rel="canonical" href="https://blog.malgnsoft.com/{cat}/{slug}/">
```

### 왜 치명인가
- 구글에 "이 콘텐츠의 정본은 저기다"라고 알려주는데, **저기는 404거나 전혀 다른 회사 홈페이지**다. 유효하지 않은 canonical → 구글은 workers.dev 페이지를 *"Alternate page with proper canonical tag"* 또는 *"Duplicate, Google chose different canonical"* 로 처리해 **색인에서 제외할 가능성이 높다** `[추론 — 구글 문서화된 동작에 근거]`.
- 홈은 더 나쁘다. canonical 목적지가 302로 **회사 대표 홈페이지**를 반환한다 → 블로그 홈의 색인 시그널이 회사 홈으로 흘러간다.
- 즉 **지금 이 사이트는 "구글 SEO 블로그"인데 구글에 안 잡힐 구조**다. 프로젝트 존재 이유가 무너진 상태.
- **robots.txt는 크롤링을 막지 않는다** (Cloudflare 기본 content-signals 파일만 200으로 응답, `Disallow` 없음 `[확인]`). 즉 크롤러는 들어와서 깨진 이미지·플레이스홀더 문구를 다 본 뒤, canonical 때문에 색인은 안 한다. **최악의 조합.**

### 수정안 (택1 — 단, 도메인 충돌 해소가 선행)

> **선행 과제(운영 이슈):** `blog.malgnsoft.com`을 Cloudflare로 넘기려면 **현재 그 이름으로 서비스 중인 레거시 JSP 서버에서 DNS를 떼어내야 한다.** 프로덕션 인프라를 건드리는 작업이므로 인프라 담당과 사전 조율 필수. "그냥 CNAME 걸면 됨"이 아니다. **이 사실이 배포 계획에 반영돼 있지 않다.**

- **(권장) 도메인 확정 후 배포**: DNS를 Cloudflare로 이관 → Worker에 커스텀 도메인 연결 → 그때 canonical이 비로소 참이 된다. **그 전까지는 공개하지 말 것.**
- **(즉시 조치) 지금 당장 해야 할 것**: 도메인 정리 전까지 workers.dev 배포본에 **`<meta name="robots" content="noindex,nofollow">` 삽입**. 미완성 상태가 크롤링되는 것을 막는다.
- **(구조 개선) 베이스 URL 변수화**: 하드코딩을 제거해 환경별로 옳은 canonical이 나오게 한다.
```python
# build.py 상단
BASE = os.environ.get('BLOG_BASE_URL', 'https://malgnblog.freerahn6.workers.dev')
NOINDEX = '<meta name="robots" content="noindex,nofollow">' if 'workers.dev' in BASE else ''
# PAGE 템플릿: <link rel="canonical" href="{base}/{cat}/{slug}/">{noindex}
```

## C-3. 카테고리 인덱스 페이지가 존재하지 않는다 → 글로벌 내비 5개 링크 전량 404 `[확인]`

`build.py`는 **홈 1개 + 아티클 12개, 총 13개 HTML만** 생성한다(L114-115, L167-168). **카테고리 인덱스를 만드는 코드가 없다.** 그런데 아티클 템플릿의 헤더 내비(L83)와 브레드크럼(L89)은 카테고리 URL을 가리킨다.

```
$ for p in /lms/ /hrd/ /certification/ /video/ /edutech/ /news/; do curl -so/dev/null -w "%{http_code} $p\n" $B$p; done
404 /lms/
404 /hrd/
404 /certification/
404 /video/
404 /edutech/
404 /news/
```

- **아티클 12편 × 헤더 내비 5링크 = 60개 링크가 전부 404.** 게다가 브레드크럼 `<a href="/{cat}/">{catlabel}</a>`도 404 (12개 추가).
- 사용자가 상세 글에서 "LMS·이러닝"을 누르면 → **완전한 백지 화면**(커스텀 404 없음, Content-Length: 0 `[확인]`). 돌아갈 링크조차 없다. **막다른 길.**
- 크롤러 입장에서도 사이트 구조가 붕괴 — 카테고리 허브가 없으니 토픽 클러스터 SEO 설계(`03_기획_IA구조.md`의 전제)가 성립하지 않는다.

### 수정안 — build.py에 카테고리 인덱스 생성 추가
```python
# 아티클 루프 뒤에 삽입
from collections import defaultdict
bycat = defaultdict(list)
for a in arts:
    bycat[a['category']].append(a)

for cat, items in bycat.items():
    items.sort(key=lambda a: a.get('date',''), reverse=True)
    cards_c = ''.join(
        '<article class="card">' + card_cover(a) +
        f'<div class="body"><h3>{H.escape(a["title"])}</h3>'
        f'<p class="excerpt">{H.escape(excerpt(a.get("description","")))}</p></div></article>'
        for a in items)
    # 홈과 동일한 셸을 재사용하되 h1/타이틀/canonical만 카테고리용으로 교체
    page = CAT_PAGE.format(catlabel=CATL[cat], cat=cat, cards=cards_c, ...)
    os.makedirs(f"{OUT}/{cat}", exist_ok=True)
    open(f"{OUT}/{cat}/index.html", 'w', encoding='utf-8').write(page)
```
- 6개 카테고리 중 `news`는 아티클이 1편뿐이나(`lms-case-studies-3`), **내비에 노출되지 않으면서 브레드크럼만 `/news/`를 가리키는 상태**라 인덱스는 필요하다.
- 카테고리 인덱스에도 canonical·title·description을 부여할 것.

## C-4. 미완성 실토 문구와 **내부 Windows 경로**가 프로덕션에 노출 `[확인]`

### C-4-a. 독자에게 보이는 figcaption이 "이건 가짜입니다"라고 말하고 있다 — **7개 페이지**

`<figcaption>`은 **화면에 렌더되는 본문 텍스트**다. 다음이 지금 라이브에서 방문자에게 그대로 보인다:

| 페이지 | 노출 중인 figcaption 문구 (발췌) |
|---|---|
| `/lms/what-is-lms/` | "… **(실제 화면 캡처는 발행 시 삽입)**" |
| `/edutech/lms-vs-lxp/` | "… **(실제 화면 캡처는 발행 시 삽입)**" |
| `/hrd/certificate-auto-issue/` | "… **(실제 화면 캡처는 자산 연동 시 교체 예정)**" |
| `/news/lms-case-studies-3/` | "… **(실제 관리 화면 캡처는 자산 연동 시 교체 예정)**" |
| `/hrd/legal-mandatory-training-online/` | "… **(실제 스크린샷은 후속 교체)**" |
| `/lms/self-hosted-vs-cloud-lms/` | "… **(관리자 화면 예시 — 실제 자산 후속 삽입)**" |
| `/edutech/what-is-microlearning/` | "… **(관리자 매뉴얼 화면, placeholder)**" |

깨진 이미지 아이콘 **바로 밑에** "실제 화면은 나중에 넣을 예정"이라고 적혀 있다. B2B 리드젠 블로그에서 **제품 신뢰도를 스스로 파괴**하는 문구다. 이미지 404보다 이쪽이 더 치명적일 수 있다.

### C-4-b. 내부 로컬 경로가 HTML 주석으로 유출 — **3개 페이지**

```
/lms/what-is-lms/                     <!-- placeholder: … (C:\job\data\매뉴얼\...\대시보드) -->
/edutech/lms-vs-lxp/                  <!-- placeholder: … (C:\job\data\매뉴얼\...) -->
/lms/online-exam-anti-cheating-setup/ <!-- placeholder: 실제 자산은 C:\job\data\매뉴얼 시험관리 온라인 시험 등록 화면 … -->
```
추가로 `/hrd/legal-mandatory-training-online/`, `/video/why-own-video-platform/`에도 (경로 없는) placeholder 주석이 남아 있다. **총 6개 페이지에 placeholder 주석.**

- 내부 파일시스템 구조 노출(정보 유출·프로 정신 결여). 소스 보기 한 번이면 드러난다.
- `markdown` 라이브러리가 HTML 주석을 그대로 통과시키므로 build.py는 이를 걸러내지 못한다.

### 수정안
1. 원고 12편에서 `<!-- placeholder … -->` 주석 **전량 삭제**, figcaption의 "교체 예정/후속 삽입/placeholder" 류 문구 **전량 삭제** (이미지를 실제로 넣은 뒤 캡션은 이미지 설명만 남긴다).
2. **build.py에 주석 스트립 + 금칙어 게이트를 넣어 재발을 막는다:**
```python
# md2html() 내부, markdown() 호출 직후
h = re.sub(r'<!--.*?-->', '', h, flags=re.S)          # HTML 주석 전량 제거

# 빌드 게이트 (본문 렌더 후)
BANNED = ['placeholder', '교체 예정', '후속 삽입', '후속 교체', '발행 시 삽입', 'TODO', 'C:\\']
for w in BANNED:
    if w.lower() in body_html.lower():
        sys.exit(f"BUILD FAILED: 미완성 표지 '{w}' 발견 → {a['slug']}")
```

---

# SECTION 3. 중대 결함

## M-1. 홈 내비 5개가 `href="#"` — 무동작. 상세와 **동작이 다르다** `[확인]`

홈은 `_preview/index.html`의 헤더를 그대로 물려받는데, build.py는 "전체" 링크만 `/`로 치환(L124)하고 **나머지 5개는 시안의 `href="#"` 그대로** 둔다.

```
홈:     <a href="/" class="active">전체</a><a href="#">LMS·이러닝</a><a href="#">기업교육·HRD</a> …
아티클: <a href="/">전체</a><a href="/lms/">LMS·이러닝</a><a href="/hrd/">기업교육·HRD</a> …   ← 404 (C-3)
```
- 홈에서 카테고리 클릭 → **페이지 맨 위로 점프할 뿐 아무 일도 안 일어남**.
- 아티클에서 같은 걸 클릭 → **404 백지**.
- **같은 내비가 페이지마다 다르게 고장나 있다.** C-3을 고치면서 홈 내비도 `/{cat}/`로 통일해야 한다(build.py L124 부근에 5개 치환 추가).

## M-2. 홈의 카테고리 필터 칩 6개가 **완전 비작동** — 클릭 가능해 보이는 장식 `[확인]`

```html
<span class="fchip on">전체</span><span class="fchip">LMS·이러닝</span> … (6개)
```
- `<span>`이다. `href` 없음, `role`/`tabindex` 없음, **홈에 `<script>`가 0개** `[확인]` → 필터 로직 자체가 존재하지 않는다.
- CSS는 `cursor:pointer`, `:hover{border-color:accent}`로 **클릭 가능하다고 강하게 시사**한다. 사용자는 누르고, 아무 일도 안 일어난다.
- **접근성**: 키보드 포커스 불가, 스크린리더에 버튼/링크로 노출되지 않음.
- **수정**: C-3의 카테고리 인덱스를 만든 뒤 `<a class="fchip" href="/lms/">…</a>`로 교체하면 링크 하나로 필터·접근성·크롤링이 동시에 해결된다. (JS 필터를 새로 짤 필요 없음.)

## M-3. 홈에 FAB(도입 문의 CTA)가 없다 — 전환 동선 누락 `[확인]`

```
페이지            FAB   <script>
/                  0       0
아티클 12편        1       1
```
`build.py`는 `{fab}`와 `{script}`를 **아티클 PAGE 템플릿에만** 넣는다(L98-99). 홈 조립부(L164-166)에는 FAB 주입이 없다.

- 홈은 유입 1순위 페이지인데 **플로팅 문의 버튼이 없다.** 헤더의 "도입 문의" 버튼만 있고 스크롤하면 사라진다(`.filters`는 sticky지만 header는 아님 → `[추론]`).
- BOFU 15% 배합·리드 확보라는 프로젝트 목표(`00_전략기획서.md`)에 직접 손실.
- **수정**: `home = home + FAB + SCRIPT + '</body></html>'`. 단 SCRIPT의 TOC 스크롤스파이·progress bar 코드는 홈에 해당 DOM이 없어 에러를 낸다 → FAB 토글 부분만 분리하거나 방어 코드(`if(bar)`, `if(fb)`)를 추가할 것.

## M-4. 홈의 **FEATURED 블록이 통째로 사라졌다** — 디자인 의도 미구현 `[확인]`

build.py는 `featured_html`을 정성껏 조립하고(L149-153) **어디에도 쓰지 않는다.**
```python
home = head + '  <div class="grid">\n' + cards + '\n  </div>\n' + tail   # L164 — featured_html 없음
```
라이브 검증:
```
class="featured" 출현: 0
'이번 주 추천'  출현: 0
'FEATURED · 추천' 출현: 0
<!-- FEATURED --> 주석만 남아 있음   ← 시안 헤더 슬라이스에 묻어온 흔적
카드 수: 12 (featured 없이 전편이 균일 카드)
```
- 시안(`_preview/index.html`)의 매거진형 대형 추천 히어로가 **출력물에 존재하지 않는다.** 홈이 밋밋한 12칸 균일 그리드가 됐다.
- `feat = bysl['lms-selection-guide-for-corporate-training']`(L144)와 하드코딩 slug도 **덩달아 dead code**.
- build.py의 종료 로그 `print("HOME:", …, "cards:", len(arts)-1, "+featured")`(L169)는 **사실과 다르다** — 카드는 12개 전부이고 featured는 없다. **로그가 거짓말을 해서 아무도 눈치채지 못했다.**
- **수정**: `home = head + featured_html + '<div class="grid">' + cards + '</div>' + tail`, 그리고 `cards` 루프에서 featured 글은 제외(`for a in arts: if a is feat: continue`)해 중복 노출을 막을 것.

## M-5. FAQ 36개 Q&A가 **전량 드롭** + JSON-LD **전무** `[확인]`

- 12편 **모두** front matter에 `faq:` 블록(각 3문답, **총 36개 Q&A**)을 갖고 있다. 명백히 **FAQPage 리치결과를 노리고 작성된 자산**이다.
- `build.py:45`의 화이트리스트가 `('title','description','category','slug','funnel','date','author')`뿐 → **`faq`·`thumbnail`·`tags`·`updated`를 전부 버린다.**
- 결과: 라이브 페이지에 FAQ 질문 텍스트가 **0건**. `application/ld+json` **0건**. `자주 묻는`/`FAQ` 섹션 **0건** `[확인]`.
- `README.md:18`은 "JSON-LD 절대경로"를 확정 방향으로 적었으나 **JSON-LD가 아예 출력되지 않는다.** 규약 미이행.
- 손실: FAQPage 리치결과 기회 + Article 구조화 데이터 + 본문 콘텐츠 36문답. **집필 공수가 통째로 사장됐다.**

### 수정안 — front matter 확장 파싱 + JSON-LD 출력
```python
# 1) faq 파싱 (현 정규식은 중첩 YAML을 못 읽는다 → PyYAML 권장)
import yaml
d = yaml.safe_load(fm)          # re 기반 라인 파서를 대체

# 2) Article + FAQPage JSON-LD (BASE는 C-2의 변수)
ld = {
  "@context": "https://schema.org",
  "@graph": [
    {"@type": "BlogPosting",
     "headline": a['title'], "description": a.get('description',''),
     "datePublished": a.get('date'), "dateModified": a.get('updated', a.get('date')),
     "author": {"@type":"Organization","name":"맑은소프트"},
     "publisher": {"@type":"Organization","name":"맑은소프트"},
     "image": f"{BASE}{a['thumbnail']}",          # 실물 배치 후
     "mainEntityOfPage": f"{BASE}/{a['category']}/{a['slug']}/"},
    {"@type": "FAQPage",
     "mainEntity": [{"@type":"Question","name":q['q'],
                     "acceptedAnswer":{"@type":"Answer","text":q['a']}} for q in a.get('faq',[])]}
  ]
}
# <script type="application/ld+json">{json.dumps(ld, ensure_ascii=False)}</script>
```
3) FAQ를 **본문 하단에 가시 섹션으로도 렌더**할 것 (구글은 화면에 보이지 않는 FAQPage 마크업을 리치결과로 인정하지 않는다).

## M-6. og:image 없음 + `thumbnail` 12건 무시 → SNS 공유 시 이미지 없음 `[확인]`

- `build.py:78`의 og 태그는 `og:title`·`og:description`·`og:type` **3개뿐**.
- **`og:image` 없음, `og:url` 없음, `twitter:card` 없음** `[확인 — 13페이지 전부 0건]`.
- front matter의 `thumbnail:` 12건은 파싱조차 안 된다(M-5와 동일 원인). 게다가 그 thumbnail들도 **존재하지 않는 .webp**를 가리킨다(§1.1).
- 결과: 카카오톡·링크드인·페이스북·슬랙 공유 시 **썸네일 없는 맨텍스트 카드**. B2B 콘텐츠 유통의 핵심 채널에서 클릭률이 크게 깎인다 `[추론]`.
- **수정**: og:image(절대 URL, 1200×630), og:url, og:site_name, twitter:card=summary_large_image 추가. 히어로 data URI는 og:image로 못 쓴다 → **실물 파일이 반드시 필요**(§1.3 A안과 묶여 있음).

## M-7. sitemap.xml 없음 / robots.txt는 Cloudflare 기본값 `[확인]`

```
/sitemap.xml  → 404
/robots.txt   → 200 (1248B) — Cloudflare content-signals 기본 파일. 
                Sitemap: 지시자 없음, Disallow 없음, 프로젝트가 작성한 게 아님.
```
- build.py에 sitemap/robots 생성 코드 없음.
- **수정**: build.py 말미에 `sitemap.xml`(13+6개 URL, `<lastmod>`는 front matter `updated` 사용) 및 `robots.txt`(`Sitemap: {BASE}/sitemap.xml`) 생성 추가. 단 **C-2 해결 전에는 sitemap을 제출하지 말 것**(404 canonical을 제출하는 꼴).

## M-8. 미작성 아티클로 향하는 내부 상호링크 **7건 404** `[확인]`

원고들이 **아직 집필되지 않은 글**을 링크하고 있다(3개월 24편 캘린더 중 미작성분).

| 링크 대상 | 참조 원고 | 상태 |
|---|---|---|
| `/certification/private-qualification-registration/` | certification-system-build-guide | **404** |
| `/certification/association-member-management/` | certification-system-build-guide | **404** |
| `/edutech/learning-data-analytics/` | what-is-microlearning | **404** |
| `/edutech/blended-learning/` | what-is-microlearning | **404** |
| `/video/streaming-cdn/` | why-own-video-platform | **404** |
| `/video/server-free-ott/` | why-own-video-platform | **404** |
| `/lms/subscription-education/` | why-own-video-platform | **404** |

- `/contact/` 링크(5개 원고)는 build.py L104가 문의 URL로 치환 → **정상** `[확인 — 라이브에 /contact/ 0건]`. 이 처리는 잘 돼 있다.
- **수정**: (a) 해당 글 집필 전까지 링크를 **텍스트로 강등**하거나, (b) build.py에 **내부 링크 존재 검증 게이트**를 넣어 빌드 실패시킬 것.
```python
known = {f"/{a['category']}/{a['slug']}/" for a in arts}
for href in re.findall(r'href="(/[^"]*)"', body_html):
    if href not in known and not href.startswith(('/lms/','/hrd/',...)):  # 카테고리 인덱스 허용
        sys.exit(f"BUILD FAILED: 존재하지 않는 내부 링크 {href} → {a['slug']}")
```

## M-9. 커스텀 404 페이지 없음 — 막다른 길 `[확인]`

```
$ curl -sD- https://malgnblog.freerahn6.workers.dev/lms/
HTTP/1.1 404 Not Found
Content-Length: 0                ← 본문이 비어 있음
```
- C-3(내비 404)·M-8(상호링크 404)로 **사용자가 404에 도달할 경로가 최소 67개**인데, 도착지는 **완전한 백지**다. 로고도, 홈 링크도, 검색도 없다. 이탈 확정.
- **수정**: `public/404.html` 생성 후 `wrangler.toml`에 지정.
```toml
[assets]
directory = "./public"
not_found_handling = "404-page"    # public/404.html 사용
```
> 참고: `single-page-application`으로 두면 안 된다(모든 404가 200 홈을 반환 → SEO 소프트404 대량 발생).

## M-10. 모바일(≤1000px): **내비게이션과 목차가 통째로 사라진다. 대체 UI 없음** `[확인]`

`_preview/article.html:141-145`:
```css
@media (max-width:1000px){
  .article-shell{grid-template-columns:1fr}
  aside.toc{display:none}      /* 목차 소실 */
  nav.main{display:none}       /* 헤더 카테고리 내비 소실 */
}
```
+ `build.py:30` EXTRA_CSS: `@media(max-width:1000px){ aside.rail{display:none} }`

| 뷰포트 | 헤더 내비 | 목차(TOC) | 좌측 배너 | 우측 배너 |
|---|---|---|---|---|
| 데스크톱 >1000px | 표시 | 표시(sticky) | 표시 | 표시 |
| **태블릿/모바일 ≤1000px** | **없음** | **없음** | **없음** | **없음** |

- **햄버거 메뉴가 없다.** 모바일 사용자는 로고(홈)와 "도입 문의" 버튼 외에 **어디로도 갈 수 없다.**
- 아티클은 h2가 3~9개인 장문인데 **모바일에 인페이지 내비가 0**. 접이식 목차 대체재도 없다.
- 3단 그리드는 1단으로 잘 무너진다(`grid-template-columns:1fr`) — 레이아웃 자체는 OK `[추론 — CSS 기준, 실기기 미검증]`.
- 홈 그리드는 3열→(900px)2열→(560px)1열로 정상 `[확인 — HOME_EXTRA]`.
- **수정**: (a) ≤1000px용 햄버거 메뉴 추가, (b) 모바일용 `<details>` 접이식 목차를 본문 상단에 렌더.

## M-11. 전 아티클이 **미래 날짜**로 발행돼 있다 `[확인]`

오늘은 **2026-07-13**. 그런데 12편의 `date:`가 **전부 미래**다.

```
2026-07-14, 07-17, 07-21, 07-24, 07-28, 07-31,
2026-08-04, 08-07, 08-11, 08-14, 08-18, 08-21   ← 12/12 전부 미래 (최대 +39일)
```
- 화면에 `<span class="num">2026-07-24</span>`로 **그대로 노출** `[확인]`.
- 콘텐츠 캘린더의 *예정일*을 그대로 발행일로 쓴 것으로 보인다 `[추론]`. 하지만 **12편이 이미 전부 공개돼 있다.**
- 방문자는 "아직 오지 않은 날짜에 쓰인 글"을 본다. 신뢰도 손상 + 구글이 미래 datePublished를 신뢰하지 않을 수 있음 `[추론]`.
- **수정**: 캘린더대로 순차 발행할 것이면 **미래 날짜 글은 빌드에서 제외**(드래프트 처리)하고, 지금 다 공개할 것이면 **날짜를 실제 발행일로 정정**하라. 양자택일.
```python
from datetime import date
arts = [a for a in arts if a.get('date','') <= date.today().isoformat()]   # 드래프트 제외
```

---

# SECTION 4. 경미 결함

## m-1. 명도 대비 — `--faint`가 WCAG AA 미달 `[확인 — 계산]`

| 토큰 | 값 | 배경 | 대비 | 판정 |
|---|---|---|---|---|
| `--text` | `#131926` | `#FFFFFF` | 17.58:1 | PASS |
| `--muted` | `#5B6577` | `#FFFFFF` | 5.88:1 | PASS |
| **`--faint`** | **`#8B94A5`** | `#FFFFFF` | **3.05:1** | **FAIL** (AA 본문 4.5:1 미달) |
| `--accent` | `#1D4ED8` | `#FFFFFF` | 6.70:1 | PASS |
| **`--faint` (다크)** | **`#6C7688`** | `#0C111B` | **4.12:1** | **FAIL** |

`--faint` 적용 위치(전부 12.5px 이하 소형 텍스트 → 4.5:1 필요):
- `.card .meta` — **홈 카드 12개의 작성자·날짜** (`_preview/index.html:121`)
- `footer.site .wrap` — **푸터 전체 텍스트** (`index.html:131`, `article.html:124`)
- `.toc .lbl` — 목차 "목차" 라벨 (`article.html:47`)
- `.card .mm` (`article.html:121`)

**수정**: `--faint`를 `#6B7385`(≈4.6:1) 이상으로 상향, 다크는 `#8A94A6`(≈5.5:1)로. 라이트/다크 3개 `:root` 블록 모두 수정 필요(`article.html:5,17,19,20` 및 index.html 동일부).

## m-2. CLS — width/height 누락 `[확인]`
- 본문 이미지 3건 누락(§1.6): certification-system-build-guide, lms-selection-guide-for-corporate-training, refund-training-lms-operation-guide
- **홈 카드 12건 전부** `<img class="cover-img" loading="lazy" src="…">`에 width/height 없음(`build.py:146-147`)
- **수정**: `card_cover()`에 `width="1200" height="675"` 추가. 본문 3건은 원고 수정.

## m-3. lazy loading 미적용 / 무의미한 lazy `[확인]`
- 본문 이미지 12건 `loading` 속성 없음.
- 홈 카드는 `loading="lazy"`가 있으나 **src가 data URI라 효과 0** — 지연할 네트워크 요청이 없다.
- **수정**: §1.3 A안으로 실물 파일 전환 시 자동 해결(그때 lazy가 비로소 의미를 갖는다). 히어로는 LCP 요소이므로 `loading="eager" fetchpriority="high"`.

## m-4. 이미지 경로 상대/절대 혼용 `[확인]` → §1.4에서 상술. 절대경로 통일 권고.

## m-5. 페이지 무게 + data URI 구조적 낭비 `[확인]`

| 페이지 | raw | zstd 압축 후 |
|---|---|---|
| **홈** | **667 KB** | **482 KB** |
| 아티클(평균) | 194~242 KB | ~137 KB |

- **홈 482KB(압축 후)** 는 블로그 홈으로선 매우 무겁다. 원인: 히어로 12개 data URI(**502KB**) + 배너 2개(**104KB**) + CSS 전량 인라인.
- **base64는 원본 대비 +33%**이고, **이미 압축된 JPEG는 재압축 이득이 거의 없다** → data URI는 압축의 혜택을 못 받는다.
- **가장 나쁜 구조적 낭비**: 배너 2개(wecandeo 24KB + malgnsoft 80KB = **약 104KB**)가 **13개 페이지 전부에 중복 인라인**된다. 그런데 그 배너는 **≤1000px에서 `display:none`** (M-10) → **모바일 사용자는 104KB를 내려받고 단 한 픽셀도 보지 못한다.** 캐시도 안 된다(페이지마다 새로 내려받음).
- **수정**: data URI를 폐기하고 실제 파일(`/assets/img/…`)로 전환. 그러면 (a) 배너·히어로가 브라우저 캐시에 1회만 저장되고, (b) HTML이 20KB 수준으로 떨어지며, (c) lazy loading이 실효를 갖고, (d) og:image로도 쓸 수 있다(M-6). **§1.3 A안과 동일한 조치로 4개 문제가 한 번에 해결된다.** CSS도 외부 파일로 분리 권고.

## m-6. 캐시 정책 / favicon `[확인]`
- `Cache-Control: public, max-age=0, must-revalidate` — 정적 블로그인데 매 방문 재검증. 자산을 파일로 분리한 뒤 해시 파일명 + `max-age=31536000, immutable` 적용 권고.
- `/favicon.ico` → **404**. 브라우저 탭·북마크·검색결과에 아이콘 없음.

## m-7. build.py 견고성 — 깨질 지점 목록 `[확인 — 코드 근거]`

| # | 위치 | 문제 |
|---|---|---|
| 1 | L110 `IMG.get(slug, COVERS[1])` | **조용한 폴백.** img_map 갱신 누락 시 엉뚱한 커버가 붙고 **아무 경고도 없다**. (현재는 12/12 일치라 미발동 — §1.5) → `sys.exit`으로 교체 |
| 2 | L33-36 `COVER` 딕셔너리 | **dead code.** 정의만 되고 미참조. 삭제 |
| 3 | L144 `bysl['lms-selection-guide-for-corporate-training']` | **하드코딩 slug.** 그 글의 slug가 바뀌면 **KeyError로 빌드 전체 폭사**. 게다가 이 값이 쓰이는 featured_html은 **미삽입**(M-4)이라 지금은 무의미한 폭탄만 남은 셈 |
| 4 | L169 `print(… "cards:", len(arts)-1, "+featured")` | **로그가 거짓.** 실제로는 12개 전부 카드, featured 없음. 이 거짓 로그가 M-4를 은폐했다 |
| 5 | L45 front matter 화이트리스트 | `faq`·`thumbnail`·`tags`·`updated` **무단 폐기**(M-5, M-6). 정규식 라인 파서라 중첩 YAML 불가 → **PyYAML로 교체 권고** |
| 6 | L40 `re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$', raw, re.S)` | front matter 없으면 `m`이 None → **AttributeError로 폭사.** try/except 또는 명확한 에러 메시지 필요 |
| 7 | L16-18 `open('img_map.json')` 등 | ART/PREV/OUT은 절대경로인데 **이 3개만 상대경로** → **`_deploy/`에서 실행하지 않으면 FileNotFoundError.** 절대경로로 통일 |
| 8 | L7-15 시안 정규식 추출 | ACSS/LOGO/MSYM/FAB/COVERS를 `_preview/*.html`에서 **정규식으로 긁어온다.** 디자이너가 시안의 클래스명·속성 순서를 바꾸면 **`.group(1)`에서 AttributeError**로 빌드 폭사. 시안과 빌드가 강결합 |
| 9 | L68 `re.sub(r'<h2>(.*?)</h2>', …)` | **h2에만 앵커 id 부여.** h3(총 24개)에는 앵커가 없어 딥링크 불가 |
| 10 | L49 H1 스트립 | `re.M` 없이 `^\s*#\s+` → 문서 **맨 앞** H1만 제거. 현재 12편 모두 본문 H1이 0개라 무해하나, 의존하면 안 되는 동작 |

## m-8. 빌드 재현 불가 — **검증 사각지대** `[확인]`
- `_deploy/public/`은 `.gitignore`에 등재(`:26`)되어 **레포에도 없고 로컬에도 없다**.
- **이 머신에 동작하는 Python 인터프리터가 없다** (`python`/`python3`가 Microsoft Store 스텁만 존재, 실행 시 즉시 종료). `markdown` 패키지 설치 여부도 확인 불가.
- 따라서 **build.py를 재실행해 배포본과 대조(diff)하는 검증을 수행할 수 없었다.**
- 본 리포트에서 *배포 결과물*에 관한 `[확인]`은 **전부 라이브 curl 응답**을 근거로 한다. *build.py 동작*에 관한 서술은 **소스 정독 + 라이브 출력과의 대조**로 교차검증했다(예: featured 미삽입은 코드에서 발견 → 라이브에서 `class="featured"` 0건으로 확증).
- **권고**: 빌드 환경(Python 버전·`markdown` 버전)을 `requirements.txt`로 고정하고, CI에서 빌드→검증 게이트→배포가 한 번에 돌게 할 것. 지금은 **누가 언제 어느 코드로 빌드했는지 아무도 재현할 수 없다.**

---

# SECTION 5. 정상 확인된 항목 (합격)

허위 결함 보고를 막기 위해, **검증했고 문제 없었던** 항목을 명시한다.

- **히어로 이미지 12/12 정상.** img_map 키 ↔ slug 완전 일치, data URI 12개 전부 고유. 폴백 미발동. (의뢰서 3번 가설은 **반증됨** — §1.5)
- **alt 텍스트 12/12 존재, 품질 우수.** 화면 내용을 구체적으로 서술. 접근성 관점에서 모범적.
- **인라인 SVG 다이어그램 정상 렌더.** `role="img"` + `aria-labelledby` + `<title>` + `<desc>` 완비. (§1.3 B안 적용 시에도 **보존할 것**)
- **h1 유일성**: 13개 페이지 전부 `<h1>` 정확히 1개. 헤딩 계층(h1→h2→h3) 역전 없음.
- **`lang="ko"`** 13개 페이지 전부 정상.
- **`<meta name="viewport">`** 전부 정상.
- **title/description** 13개 전부 존재, 중복 없음. title 길이 87~131자(태그 포함 측정) — 한글 기준 적정.
- **HTML 구조 무결성**: doctype/html/head/body 각 1개. (build.py의 홈 조립이 위태로워 보이나 `_preview/*.html`이 fragment라 결과적으로 정상 — **실측으로 확인함**)
- **`/contact/` → 문의 URL 치환 정상** (build.py L104). 라이브에 `/contact/` 잔존 0건.
- **외부 링크 3종 전부 200**: `www.malgnsoft.com`, `www.wecandeo.com`, `www.malgnsoft.com/cloud/inquiry.jsp`. `target="_blank"`에 `rel="noopener"` 정상 부여.
- **FAB 접근성 우수**: `aria-haspopup`, `aria-expanded` 토글, `aria-label` 상태 반영, `role="menuitem"`, **Escape 키 닫기**, `:focus-visible` 아웃라인 3px. 잘 만들어졌다. (문제는 **홈에 없다는 것**뿐 — M-3)
- **`prefers-reduced-motion` 대응** 있음. **다크모드**(`prefers-color-scheme` + `data-theme`) 지원.
- **zstd 압축** 정상 적용.
- **홈 반응형 그리드** 3열→2열(900px)→1열(560px) 정상 정의.

---

# SECTION 6. 미검증 항목 (한계 명시)

curl·정적 분석으로는 닿지 못한 영역. **"문제 없음"이 아니라 "확인하지 못함"이다.**

| 항목 | 사유 |
|---|---|
| **실기기·실브라우저 렌더링** | 헤드리스 브라우저 미가용. Chrome/Safari/Firefox/Edge 실제 렌더, iOS Safari의 `position:sticky`·`backdrop-filter` 동작, 안드로이드 크롬 미검증 |
| **깨진 이미지의 실제 시각적 붕괴 정도** | width/height 있는 9건은 공간을 점유한 채 깨진 아이콘, 없는 3건은 레이아웃 붕괴로 **추정**되나 육안 미확인 |
| **Core Web Vitals 실측** | LCP/CLS/INP 수치 미측정. Lighthouse 미실행. (data URI 502KB 기반 LCP 악화는 `[추론]`) |
| **JS 런타임 에러** | IntersectionObserver·FAB 토글의 실제 콘솔 에러 유무 미확인. 특히 홈에 SCRIPT를 추가할 경우의 null 참조는 `[추론]` |
| **스크린리더 실사용** | NVDA/VoiceOver 실검증 미실시. 마크업 기준 정적 판단만 수행 |
| **키보드 탭 순서** | 실제 포커스 이동 순서·포커스 트랩 미검증 (FAB 메뉴 열림 시 포커스 관리는 코드상 부재로 보임 `[추론]`) |
| **`markdown` 라이브러리 렌더 정확성** | Python 미가용으로 재빌드 불가 → 라이브 HTML 관찰로 갈음 |
| **폼 검증·권한·빈 상태** | 해당 UI 없음(정적 블로그). 문의는 외부 사이트로 이관 |

---

# SECTION 7. 조치 우선순위

## P0 — 지금 즉시 (공개 상태 방치 불가)
1. **`<meta name="robots" content="noindex,nofollow">` 삽입** 또는 배포 내림. 미완성물이 색인되는 것을 먼저 막는다. (C-2)
2. **플레이스홀더 실토 문구·내부 경로 제거** — figcaption 7건, HTML 주석 6건. (C-4)

## P1 — 발행 전 필수 (하나라도 남으면 발행 불가)
3. **이미지 12종 실물 제작 → `/assets/img/` 절대경로 통일 → build.py 복사 단계 + 자산 검증 게이트** (C-1, §1.3 A안 + §1.4)
4. **카테고리 인덱스 6종 생성** → 내비 404 60건 + 브레드크럼 404 12건 해소 (C-3)
5. **홈 내비 5개 `href="#"` → `/{cat}/`, 필터 칩 `<span>` → `<a>`** (M-1, M-2)
6. **`blog.malgnsoft.com` DNS 충돌 해소** → 커스텀 도메인 연결 → canonical 정합 (C-2)
   - **레거시 JSP 서버가 그 이름으로 서비스 중임을 인프라 담당과 반드시 사전 조율할 것**
7. **미래 날짜 정리** — 드래프트 제외 또는 날짜 정정 (M-11)

## P2 — 발행과 동시에
8. JSON-LD(BlogPosting + FAQPage) 출력 + FAQ 36문답 가시 렌더 (M-5)
9. og:image·og:url·twitter:card (M-6)
10. sitemap.xml + robots.txt 생성 (M-7) — **단 C-2 해결 이후 제출**
11. 커스텀 404 페이지 (M-9)
12. 미작성 글 상호링크 7건 처리 (M-8)
13. 홈 FAB 주입 + featured 블록 삽입 (M-3, M-4)
14. 모바일 햄버거 메뉴 + 접이식 목차 (M-10)

## P3 — 후속
15. `--faint` 명도 대비 상향 (m-1)
16. data URI → 실제 파일 전환 (m-5) — **P1-3과 함께 하면 한 번에 끝난다**
17. width/height·lazy·favicon·캐시 헤더 (m-2, m-3, m-6)
18. build.py 견고성 10건 + 빌드 재현성 확보 (m-7, m-8)

---

## 총평

디자인·카피·alt 텍스트·FAB 접근성·SVG 다이어그램은 **수준이 높다.** 문제는 전부 **"만들어졌다고 보고됐지만 실제로는 없는 것"** 에서 나왔다.

- 이미지는 **참조만 있고 실물이 없다** — 원고가 스스로 placeholder라고 자백하고 있었는데 그대로 배포됐다.
- 카테고리 페이지는 **링크만 있고 페이지가 없다.**
- featured 블록은 **코드만 있고 출력에 없다** — 게다가 빌드 로그가 "featured 있음"이라고 **거짓 보고**했다.
- FAQ 36문답은 **원고에만 있고 웹에 없다.**
- canonical은 **선언만 있고 목적지가 404**다.

공통 구조는 하나다. **claimed ≠ verified.** build.py에는 자기가 만든 결과물을 검증하는 단계가 **단 하나도 없다.** 이미지가 없어도, 링크가 죽어도, featured가 빠져도 빌드는 `exit 0`으로 웃으며 끝난다.

수정안마다 **빌드 게이트**를 붙여둔 이유가 이것이다. 개별 결함을 다 고쳐도 게이트가 없으면 **다음 아티클에서 똑같이 재발한다.** 자산 검증·내부 링크 검증·금칙어 검증 3종 게이트를 build.py에 심는 것이, 이 리포트의 어떤 개별 수정보다 중요하다.
