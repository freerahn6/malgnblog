# 클러스터 ↔ URL slug ↔ front matter 통합 택소노미 (감마 확정)

> 마케팅(01)의 피라 A~F와 기획(03)의 URL slug를 감마가 1:1로 확정. 모든 팀은 front matter `category`에 아래 **slug**를, `cluster`에 피라 코드를 사용한다.

| 피라 | 마케팅 명칭(01) | URL slug(03) | front matter category | 배합 성격 |
|---|---|---|---|---|
| A | LMS·이러닝 구축/운영 | `lms` | lms | 정보·실무 |
| B | 기업교육·HRD(법정·환급·직무) | `hrd` | hrd | 실무 중심 |
| C | 자격검정·인증 | `certification` | certification | 실무·신뢰 |
| D | 동영상·콘텐츠 플랫폼(위캔디오·임대) | `video` | video | 정보·실무 |
| E | 에듀테크·교육 AI(운영자 렌즈) | `edutech` | edutech | 정보(TOFU) |
| F | 맑은소프트 소식·신뢰(E-E-A-T) | `news` | news | 홍보(BOFU) |

- URL 패턴: `/{category}/{slug}/` (트레일링 슬래시 유지). slug는 영문 소문자+하이픈, 발행 후 불변.
- 2단계 주제(구축가이드/환급과정 등)는 URL이 아니라 `tags` + `cluster` 논리로만 표현.
- 확정 스택: 정적 SSG(Astro). 내부링크·이미지=상대경로, canonical/og/JSON-LD=절대경로(`SITE_URL` 주입).
