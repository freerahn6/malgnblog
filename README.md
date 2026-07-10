# 맑은소프트 블로그 (교육운영 노트)

맑은소프트의 구글 SEO 비즈니스 블로그 프로젝트. 기업교육·HRD 담당자를 타깃으로, LMS·이러닝·자격검정·에듀테크 실무 지식을 다룬다.

## 구성
```
_preview/            블로그 디자인 시안 (정적 HTML)
  index.html         블로그 홈 (매거진 카드 그리드)
  article.html       글 상세 뷰 (목차 사이드바 + 플로팅 메뉴)
  what-is-lms.html   초기 아티클 렌더 시안
articles/            SEO 아티클 원고 (마크다운 + front matter)
00_전략기획서.md ~ 05_검수리포트.md   기획·전략·검수 산출물
_brief.md / _facts.md / _taxonomy.md / _writing-guide.md   공용 기준 문서
```

## 확정 방향
- 주소: `blog.malgnsoft.com` (도메인 추후 연결)
- 스택: 정적 SSG(Astro 권고), 내부링크·이미지 상대경로 / canonical·JSON-LD 절대경로
- 콘텐츠 배합: 정보(TOFU) 50 / 실무(MOFU) 35 / 제품·홍보(BOFU) 15
- 편집 원칙: 운영자 렌즈 + 교육 게이트 (상세 `_writing-guide.md`)

## 현재 상태
디자인 시안(홈·상세) 확정 단계, 콘텐츠 파일럿 6편 작성 완료, 3개월 캘린더 24편 중 나머지 집필 예정.
