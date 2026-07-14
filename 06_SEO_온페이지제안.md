# 맑은소프트 블로그 — SEO 온페이지·기술·AI검색(AIO/GEO) 실행 제안

> 대상: `https://blog.malgnsoft.com` (Netlify 정적, 글 12편, 카테고리 6개)
> 전제: canonical·meta·OG/Twitter·JSON-LD(Article·FAQPage·Breadcrumb)·sitemap·robots·모바일반응형·내부링크·롱폼/표/SVG는 **이미 done**. 이 문서는 **"그 위에 무엇을 더 할까"** 만 다룬다.
> 근거: 2026년 최신 웹 리서치(문서 하단 출처). 추측·일반론 배제, 실행 가능한 항목만.

---

## 0. 한눈에 보는 우선순위 맵

| 순위 | 항목 | 핵심 문제 | 난이도 | 기대효과 |
|---|---|---|---|---|
| **P0-1** | 이미지 base64 인라인 → 실제 파일 호스팅 | OG공유·이미지검색 불가 + LCP/속도 악화 | 중 | 소셜공유 썸네일 복구, 이미지검색 유입, LCP 개선 |
| **P0-2** | 구글 서치콘솔 + GA4 셋업 | 측정 기반 자체가 없음 = 개선 판정 불가 | 하 | 색인·쿼리·CTR·CWV 실측, 이후 모든 판단의 근거 |
| **P0-3** | AI검색 인용용 "답변 우선(answer-first)" 블록 | AI Overviews·ChatGPT·Perplexity 인용 구조 미비 | 중 | AI 답변 인용 노출(제로클릭 시대 브랜드 노출) |
| **P0-4** | Author/Organization 엔티티 스키마 강화(sameAs) | E-E-A-T의 'Experience/author' 신호 약함 | 하 | AI Overview 인용·지식패널·저자 권위 |
| **P0-5** | AI 크롤러 명시 허용(robots.txt) + Core Web Vitals 기본기 | AI봇 접근·INP/LCP 미검증 | 하 | AI 학습·인용 크롤 보장, 페이지경험 신호 |
| P1-1 | 정의·요약·Q&A·비교표 "발췌 최적화" 콘텐츠 리라이트 | 롱폼은 있으나 AI/피처드스니펫 추출 구조 아님 | 중 | 피처드 스니펫 + AI 인용 동시 |
| P1-2 | 내부링크 앵커 다양화 + Pillar 권위 집중 | 앵커·상향링크 정밀도 | 하 | 클러스터 권위 전달, 헤드키워드 상승 |
| P1-3 | 콘텐츠 freshness(갱신일자·주기적 리프레시) 체계 | 12편 정적, 갱신 신호 없음 | 하 | Perplexity/AI 최신성 가점, HCU 지속발행 신호 |
| P1-4 | 제3자 인용·언급 확보(G2류·보도·위키데이터) | 오프사이트 권위/멘션 부족 | 중 | AI 인용확률·백링크·엔티티 신뢰 |
| P2-1 | llms.txt 배치 | AI 라우팅 파일(현재 효과 제한적) | 하 | 저비용 선제 대응 |
| P2-2 | 이미지 AVIF/WebP + fetchpriority/lazy 정밀화 | 이미지 성능 상세 최적화 | 중 | LCP 추가 개선 |
| P2-3 | HowTo/Video/ItemList 등 스키마 확장 | 구조화데이터 커버리지 | 중 | 리치결과·AI 이해도 |

---

## P0 — 즉시 (측정 기반 + 최대 임팩트)

### P0-1. 이미지 base64 인라인 → 실제 파일로 호스팅

**무엇을**
- 본문·OG의 모든 이미지를 base64 data-URI에서 **실제 `.webp/.avif` 파일**(`/images/…`)로 분리해 Netlify에 정적 호스팅.
- 각 글에 **전용 OG 이미지 1장**(1200×630, 절대 URL)을 실제 파일로 지정. SVG 도표도 검색·공유 대상이 되도록 `<img src>` 파일 또는 인라인 SVG + 별도 래스터 OG 병행.
- `width`/`height` 명시, alt·캡션 유지(이미 규칙 있음), 본문 상단 대표 이미지에 `fetchpriority="high"`, 접힘 아래 이미지에 `loading="lazy"`.

**왜(근거)**
- base64 인라인은 **OG/트위터 카드가 외부 절대 URL 이미지를 요구**하므로 SNS·메신저 공유 시 썸네일이 뜨지 않고, **구글 이미지검색에 색인될 독립 URL이 없다**. 인라인 데이터는 HTML을 부풀려 **LCP를 지연**시킨다(캐시 불가, 최초 렌더에 전부 파싱).
- 2026 이미지 SEO 정설: WebP/AVIF는 JPEG 대비 **25~50% 용량 절감**, LCP 이미지엔 **fetchpriority="high" + lazy 금지**, 그 외엔 lazy, 모든 이미지에 width/height로 **CLS 제거**. (SitePoint, corewebvitals.io, crawlvision)
- INP·LCP·CLS는 2026에도 **실측 필드데이터 기반 랭킹 신호**. (crawlvision, mewastudio)

**기대효과**: 소셜 공유 썸네일 복구 → 공유 CTR↑, 구글 이미지검색 신규 유입 채널, LCP/CLS 개선으로 페이지경험 신호 회복.
**난이도**: 중 (빌드 시 이미지 추출·변환 파이프라인 1회 구성, 이후 자동).

---

### P0-2. 구글 서치콘솔(GSC) + GA4 셋업 — 측정 기반부터

**무엇을 (절차)**
1. **GSC 등록**: search.google.com/search-console → 속성 추가 → **도메인 속성**(DNS TXT, blog 서브도메인 포함 권장) 또는 URL 접두어(`https://blog.malgnsoft.com`). Netlify DNS에 TXT 레코드 추가로 소유 확인.
2. **sitemap 제출**: GSC > Sitemaps에 `sitemap.xml` 제출. (robots.txt에도 `Sitemap:` 절대경로 명시 재확인)
3. **색인 확인**: URL 검사 도구로 12편 + 6허브 색인 상태 점검, 미색인 URL "색인 요청".
4. **GA4 설치**: gtag 스니펫 삽입. 이벤트로 **CTA 클릭(문의/데모), 스크롤 깊이, 아웃바운드, 파일 다운로드**를 전환 이벤트 등록.
5. **GSC↔GA4 연동** + Bing Webmaster Tools도 등록(ChatGPT/Copilot이 Bing 색인 참조).
6. 모니터링 루프: 쿼리·CTR·평균순위·CWV(페이지경험 리포트)·색인 커버리지 주간 확인.

**왜(근거)**
- 현재 **자체 측정 자산이 없어 개선을 판정할 수 없다.** 그로스 원칙(가설→실험→측정→반복)상 측정 인프라가 P0. AI 답변 인용은 클릭이 안 남으므로 **GSC 노출수/브랜드 검색 증가**로 간접 측정해야 한다.
- ChatGPT Search·Copilot은 **Bing 색인**을 크게 참조 → Bing 등록이 AI 노출의 저비용 지렛대.

**기대효과**: 이후 모든 항목의 성패를 데이터로 판정. 표본·기간(2~4주, 충분 이벤트) 확보 후에만 콘텐츠 승격/폐기 판단.
**난이도**: 하 (반나절).

> 판정 주의: 신규 도입 직후 노벨티/색인 지연이 있으므로, **최소 2~4주·색인 안정화 후** 쿼리·CTR을 읽고, 진단지표(CWV·CTR)와 성과지표(순위·전환)를 분리해 본다.

---

### P0-3. AI검색 인용용 "답변 우선(answer-first)" 구조 도입

**무엇을**
- 각 글 **도입부에 40~60단어 직답 요약 블록**("한 줄 정의 + 핵심 결론")을 배치. 예: "LMS란 …를 뜻한다. 기업교육 담당자는 자체개발보다 클라우드 임대가 …한 경우 유리하다."
- **H2/H3를 질문형**으로("LMS 구축 비용은 얼마인가?"), 각 섹션 **첫 2문장에 직답 → 이후 부연** 구조로 리라이트(주변 문맥 없이도 추출 가능하게).
- 글 말미 **"핵심 요약 3줄"** + 기존 FAQPage 스키마의 Q&A를 **본문 가시 텍스트로도** 노출(스키마만이 아니라 본문에도).
- **명시적 수치·출처·고유명사**를 문장에 심는다(예: "고용보험 환급률 최대 100%", "동시접속 N명" 등 검증 가능한 사실).

**왜(근거)**
- 2026 GEO 정설: LLM은 **"질문을 문맥 없이 해소하는 40~60단어 추출 블록"**을 선호. answer-first 산문 + 질문형 헤딩 + JSON-LD + 검증 출처가 인용 확률을 높인다. **통계·출처 추가는 AI 가시성을 각 30~40% 개선.** (Frase, Shadow, Pixelmojo)
- 구글 AI Overviews는 **기존 검색 상위 + 구조화데이터 + 직답 콘텐츠**에서 주로 발췌. 한국은 구글 AI 모드가 한국어 정식 출시되어 **"클릭이 아니라 인용"**으로 목표가 이동. (allmyuniverse, next-t)

**기대효과**: 피처드 스니펫 + AI Overviews/ChatGPT/Perplexity 인용 → 제로클릭 환경에서도 브랜드 노출.
**난이도**: 중 (12편 순차 리라이트, 템플릿화하면 반복 저비용).

---

### P0-4. Author/Organization 엔티티 스키마 강화 (sameAs)

**무엇을**
- **Organization 스키마**(사이트 전역): `name`, `url`, `logo`, `sameAs`[홈페이지·회사 링크드인·유튜브·네이버블로그·보도자료], 신뢰자산을 `award`(국무총리표창 등), `hasCredential`(메인비즈·가족친화·CSAP 등)로 명시.
- **Article에 author = Person/Organization 연결**: 저자 Person 엔티티(`name`, `url`=저자페이지, `jobTitle`, `worksFor`=맑은소프트, `knowsAbout`=[LMS, HRD, 이러닝], `sameAs`). 익명 대신 **실명 또는 "맑은소프트 에디터"+회사 엔티티** 부여.
- 저자 **바이오 박스**(본문 하단, 2~3문장 + 전문영역)를 스키마와 **동일 문구**로. 가능하면 **Wikidata 항목 생성** 후 sameAs에 연결.

**왜(근거)**
- 2026 E-E-A-T의 기계적 핵심 = **Person/Organization 엔티티 + sameAs 체인**. sameAs가 풍부·검증가능할수록 **AI Overview 인용·지식패널·저자 권위 가중치**가 올라간다. **Wikidata 한 줄이 소셜 5개보다 강함.** (leadgen-economy, stackmatix, growthvibe)
- 2026 랭킹에서 **Experience(1인칭 경험·사례)**가 가장 강하게 검증되는 신호 — 맑은소프트의 40+ 도입사례·표창은 최상급 E-E-A-T 자산인데 **엔티티로 구조화**해야 기계가 읽는다. (analytify, semihuman)

**기대효과**: AI 인용·지식패널 정확도, 저자귀속 콘텐츠 랭킹 가중.
**난이도**: 하 (스키마 추가 + 바이오 박스 템플릿).

---

### P0-5. AI 크롤러 허용 명시 + Core Web Vitals 기본 점검

**무엇을**
- robots.txt에 **AI 크롤러 명시 허용**: `GPTBot`, `OAI-SearchBot`, `PerplexityBot`, `ClaudeBot`, `Google-Extended`, `Applebot-Extended`, `Bingbot`. (인용을 원하므로 차단하지 않는다.)
- GSC 페이지경험/PageSpeed Insights로 **LCP<2.5s, INP<200ms, CLS<0.1** 실측. 정적사이트라 유리하나 base64 이미지(P0-1)와 JS 인터랙션(INP) 점검.
- 렌더 블로킹 CSS/JS 최소화, 폰트 `font-display:swap`, 웹폰트 서브셋(한글 서브셋으로 용량↓).

**왜(근거)**
- AI 인용을 받으려면 해당 봇의 **크롤 접근이 열려 있어야** 한다(로그상 llms.txt는 거의 안 읽지만 robots 접근제어는 유효). (dataimpulse, digitalapplied)
- INP는 2024.3부터 공식 CWV, **모든 상호작용 응답성**을 측정(200ms 목표). LCP는 fetchpriority·lazy 규칙으로 관리. (crawlvision, sitepoint)

**기대효과**: AI 학습·인용 크롤 보장, 페이지경험 신호 안정.
**난이도**: 하.

---

## P1 — 다음 (콘텐츠·구조 심화)

### P1-1. 발췌 최적화 콘텐츠 리라이트(정의·요약·Q&A·비교표)
- **무엇을**: 각 글에 ① 상단 **정의 박스**(용어 1문장 정의) ② **비교표**(자체개발vs임대, LMS별 기능 등 — 이미 표 문화 있음, AI가 파싱하기 좋은 `<table>` 유지·헤더 명확화) ③ **"주요 통계/사실" 리스트**(수치+근거) ④ 본문 노출 FAQ.
- **왜**: 표·리스트·정의는 피처드 스니펫과 AI 발췌의 최적 포맷. Perplexity는 **최근 12개월 내 발행** 콘텐츠를 선호 → 발행일·갱신일 명시. (Frase, ailabsaudit)
- **기대효과**: 스니펫+AI 인용 동시. **난이도**: 중.

### P1-2. 내부링크 앵커 다양화 + Pillar 권위 집중
- **무엇을**: 이미 있는 토픽클러스터 링크의 **앵커 텍스트를 타깃키워드 변주**로 다양화(동일 앵커 반복 지양), Supporting→Pillar **상향 링크를 본문 상단**에 배치, 인접 피라 간 수평링크 추가. 각 글 **관련글 3~4개** 블록.
- **왜**: 백링크가 여전히 강한 신호이나 오프사이트는 시간이 걸림 → **온사이트 내부링크로 Pillar에 권위를 몰아** 헤드키워드(LMS·기업교육) 경쟁을 뚫는다(전략서 4장과 정합). (analytify)
- **난이도**: 하.

### P1-3. 콘텐츠 freshness 체계
- **무엇을**: 각 글에 **"최종 업데이트: YYYY-MM"** 가시 표기 + Article 스키마 `dateModified` 갱신. **분기별 리프레시 루틴**(수치·연도·사례 갱신, "2026" 유지). 캘린더대로 **주 2회 지속 발행**.
- **왜**: HCU는 **지속적 양질 발행 패턴을 사이트 단위로 평가**(저품질 누적 시 도메인 전체 타격). Perplexity·AI는 최신성에 가점. 네이버도 최신성·활동지표 민감. (orbit/HCU, semihuman, inblog)
- **난이도**: 하 (운영 루틴).

### P1-4. 제3자 인용·언급(오프사이트 엔티티 신뢰)
- **무엇을**: 보도자료·업계 매체 기고, LMS 비교/리뷰 디렉터리 등재, **위키데이터/나무위키 등 엔티티 소스** 정비, 파트너(EBS·강남인강 등) 페이지에서의 링크·언급 확보.
- **왜**: **4개+ 플랫폼에서 언급되면 ChatGPT 인용 확률 2.8배**, G2류 리뷰사이트가 AI 3사에서 가장 많이 인용됨. 백링크·엔티티 멘션은 랭킹·AI 인용 공통 신호. (Shadow, analytify)
- **난이도**: 중 (홍보팀 협업).

---

## P2 — 여력 시

- **P2-1 llms.txt**: 루트에 `/llms.txt`(사이트 개요 + 핵심 글 목록 링크). 현재 **주요 LLM은 거의 안 읽지만(파일의 97% 요청 0건)** 비용이 반나절이라 선제 배치 가치. 크롤 제어는 robots.txt로. (ppc.land, dataimpulse) — **난이도 하, 기대효과 낮음(선행투자)**.
- **P2-2 이미지 성능 정밀화**: AVIF 우선 + WebP 폴백(`<picture>`), 반응형 `srcset`, LCP만 preload. — 난이도 중.
- **P2-3 스키마 확장**: 실무 가이드에 **HowTo**, 도표 많은 글에 **ItemList**, 위캔디오 영상에 **VideoObject**, 사례글에 **Organization+Review/사례**. — 난이도 중.

---

## 그 외 발견한 개선점

1. **한국어 검색 이원화 대응**: 구글(백링크·E-E-A-T·구조화데이터)과 네이버(C-Rank 출처신뢰·D.I.A 문서품질·체류/공유)는 알고리즘이 다르다. 이 블로그는 **구글 최적화가 정답**이나, 기존 네이버블로그(50편)에서 **본문 요약+대표링크로 blog.malgnsoft.com 유입**을 흘려 초기 트래픽·체류를 보완할 수 있다. (inblog, next-t)
2. **제로클릭 대비 KPI 재정의**: AI 인용 시대엔 세션뿐 아니라 **GSC 노출수·브랜드검색량·직접유입**을 성장지표로 병행 추적(P0-2 GA4 이벤트와 결합).
3. **BOFU 브랜드 키워드 선점**: "맑은소프트 LMS/맑은이러닝/위캔디오"는 경쟁이 없어 100% 확보 가능 — 전용 페이지 + Organization 스키마로 **지식패널 유도**.
4. **표는 이미지가 아니라 HTML `<table>`**(브리프 규칙) 준수 재확인 — AI 파싱·발췌에 결정적. 기존 SVG 도표에는 반드시 텍스트 대체(캡션/근접 문단)를 둔다.

---

## 측정 KPI (이 제안의 성패 판정)

| 지표 | 도구 | 판정 시점 |
|---|---|---|
| 색인 URL 수 / 색인 오류 | GSC 커버리지 | 셋업 후 2주 |
| 노출수·평균순위·CTR(쿼리별) | GSC 실적 | 4주+ (표본 확보 후) |
| CWV: LCP/INP/CLS 통과율 | GSC 페이지경험/PSI | 이미지분리 후 2주 |
| 이미지검색·소셜공유 유입 | GA4 채널/소스 | 4~8주 |
| AI 인용 노출(간접) | 브랜드검색·직접유입·노출수 추이 | 4~8주(AI Overview 반영 지연) |
| 전환: CTA클릭→리드, 유입글별 리드 | GA4 이벤트 | 8주+ |

> 판정 원칙: **학습·색인 안정화 전 조기판단(peeking) 금지**. 진단지표(CTR·CWV)와 성과지표(순위·리드)를 분리해 읽고, 최소 4주·충분 표본 후 콘텐츠 승격/리프레시/폐기를 결정한다.

---

## 출처 (2026년 리서치)

- [Analytify — 13 Most Important Google Ranking Factors 2026](https://analytify.io/google-ranking-factors/)
- [Orbit — Google 2026 Helpful Content Update Guide](https://orbitinfotech.com/blog/google-2026-helpful-content-update/)
- [SemiHuman — Helpful Content Update & SEO 2026](https://www.semihuman.ai/blog/helpful-content-update-seo-2026)
- [Frase — GEO Playbook: Get Cited by AI Search](https://www.frase.io/blog/how-to-get-cited-by-ai-search-engines-the-complete-geo-playbook)
- [Shadow — Get cited by ChatGPT, Perplexity, Google AI Overviews](https://www.shadow.inc/resources/get-cited-by-ai-search)
- [Pixelmojo — GEO Playbook 2026](https://www.pixelmojo.io/blogs/geo-playbook-get-cited-chatgpt-perplexity-claude)
- [ailabsaudit — Get Cited by Perplexity 2026](https://ailabsaudit.com/blog/en/perplexity-guide-maximize-citations)
- [SitePoint — Image Optimization for Core Web Vitals 2026](https://www.sitepoint.com/image-optimization-for-core-web-vitals-in-2026-what-actually-moves-the-needle/)
- [Crawlvision — Core Web Vitals 2026 (LCP/INP/CLS)](https://crawlvision.com/blog/core-web-vitals-2026-seo-guide/)
- [corewebvitals.io — Optimize images for CWV](https://www.corewebvitals.io/pagespeed/optimize-images-for-core-web-vitals)
- [MewaStudio — SEO & Core Web Vitals 2026](https://www.mewastudio.com/en/blog/seo-core-web-vitals-2026)
- [leadgen-economy — E-E-A-T Author-Entity Verification & AI Overviews](https://www.leadgen-economy.com/blog/eeat-author-entity-verification-ai-overviews/)
- [Stackmatix — Organization Schema & Entity SEO 2026](https://www.stackmatix.com/blog/organization-schema-knowledge-graph)
- [growthvibe — Entity SEO: Schema & Knowledge Graphs](https://www.growthvibe.com/ai-seo/entity-seo/)
- [dataimpulse — Robots.txt & AI Crawlers 2026](https://dataimpulse.com/blog/robots-txt-ai-crawlers/)
- [digitalapplied — AI Crawler Access Control 2026](https://www.digitalapplied.com/blog/ai-crawler-access-control-2026-robots-llms-txt-decision-matrix)
- [ppc.land — llms.txt adoption 8.8x but 97% zero AI requests](https://ppc.land/llms-txt-adoption-rises-8-8x-but-97-of-files-get-zero-ai-requests/)
- [allmyuniverse — 구글 AI 모드 최적화 2026(한국)](https://allmyuniverse.com/google-ai-mode-optimization-seo-strategy-guide-2026/)
- [next-t — 콘텐츠 SEO: 검색의도·토픽클러스터·E-E-A-T 2026](https://www.next-t.co.kr/seo/content-seo/)
- [inblog — 한국 검색엔진 순위·점유율 2026](https://inblog.ai/ko/blog/korea-search-engine-rankings)
