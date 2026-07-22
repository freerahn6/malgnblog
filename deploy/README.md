# 자동 배포 — 운영자용

`main`에 push하면 사이트가 자동으로 갱신됩니다. **서버는 담당자가 최초 1회 설정한 뒤 손대지 않습니다.**

```
git push main
     │
     ▼
GitHub Actions ─ 빌드(build.py) → 건전성 검사 → deploy 브랜치에 커밋(public_html/ 아래)
                                                        │
웹서버 cron (2분마다) ─ git fetch + reset ──────────────┘
                      → /home/blog/public_html 갱신
```

**서버 환경** — Rocky Linux 9.5 / Apache 2.4.62 / Resin 4.0.67
**레이아웃** — git 루트 `/home/blog` · 웹루트 `/home/blog/public_html` · 데이터 `/home/blog/data`

- **서버에 자격증명이 없습니다.** 공개 저장소를 읽기만 하므로 토큰·키가 필요 없습니다.
- **서버에 빌드 환경이 없습니다.** GitHub이 빌드까지 끝냅니다. 서버는 `git`만 씁니다.
- **deploy 브랜치의 트리 모양 = 서버의 `/home/blog`.** 그래서 서버는 `git reset` 한 번으로 웹루트가 갱신됩니다(rsync 불필요).
- **Apache가 문서를 직접 서빙하고, Resin은 `/api/*` 조회수 수집만 맡습니다.**

## 평소 사용법

```bash
git add articles/새-글.md
git commit -m "새 글 발행"
git push
```

끝입니다. **최대 2~3분** 뒤 사이트에 반영됩니다(GitHub 빌드 ~1분 + 서버 폴링 최대 2분).
진행 상황은 레포 **Actions** 탭에서 볼 수 있습니다.

문서(`*.md`)나 `deploy/`만 고친 커밋은 빌드하지 않습니다. `articles/` 안의 글은 물론 배포 대상입니다.

## 최초 1회 준비

### 1. 레포를 공개로 전환

서버가 자격증명 없이 받아가려면 공개 저장소여야 합니다.

**웹에서**: 레포 → Settings → 맨 아래 **Danger Zone** → *Change repository visibility* → **Make public**

**CLI로**:
```bash
gh repo edit freerahn6/malgnblog --visibility public --accept-visibility-change-consequences
```

> 전환 전 확인 완료: 커밋된 자격증명·키는 없습니다.
> 공개되는 것은 원고(md)·빌드 스크립트·기획 문서이며, 완성된 사이트는 어차피 공개될 내용입니다.

### 2. 첫 빌드 실행

레포 → **Actions → 배포 브랜치 갱신 → Run workflow**

`deploy` 브랜치가 생성되고 정적 HTML이 올라갑니다. 서버 설치는 이게 끝난 뒤에 해야 합니다.

### 3. 서버 담당자에게 전달

[서버담당자-설치가이드.md](서버담당자-설치가이드.md) · [apache-blog.conf](apache-blog.conf) ·
[resin-blog.xml](resin-blog.xml) 세 개를 전달하세요.
보안 관점 요약(인바운드 80/443뿐·자격증명 없음·실행되는 코드는 조회수 JSP 2개뿐)이 문서 앞머리에 정리되어 있습니다.

### 4. DNS

`blog.malgnsoft.com`을 자체서버 A레코드로 변경합니다(현재 Netlify CNAME).

## 문제가 생기면

**Actions 탭에 빨간 X** — 빌드 또는 검증 실패입니다. 이 경우 `deploy` 브랜치가 갱신되지 않으므로
**서버의 현재 사이트는 그대로 유지됩니다.** 깨진 사이트가 나가는 일은 없습니다.

**Actions는 초록불인데 사이트가 그대로** — 서버 cron 문제입니다. 담당자에게 설치가이드 4장(동작 확인)을 요청하세요.

**롤백** — `deploy` 브랜치는 커밋 이력이 쌓입니다. 이전 커밋으로 되돌리면 서버가 2분 안에 따라옵니다.
```bash
git fetch origin deploy
git push origin +<되돌릴커밋>:deploy
```

## 대안 워크플로

[bundle.yml](../.github/workflows/bundle.yml)은 **수동 실행 전용**으로 남겨뒀습니다.
서버 자동 갱신이 막히거나 담당자에게 직접 파일을 전달해야 할 때, Actions 탭에서 수동 실행하면
검증까지 마친 정적 파일 묶음(zip)을 내려받을 수 있습니다.

## 조회수 집계 (Resin JSP로 이관 완료)

Netlify Functions + Blobs에 있던 기능을 Resin JSP로 다시 구현했습니다. 소스는 `server/WEB-INF/`,
빌드 때 웹루트의 `public_html/WEB-INF/` 로 함께 배포됩니다.

| | |
|---|---|
| 수집 | `POST /api/track?p=/경로/` — 모든 페이지 하단 스크립트가 호출 |
| 조회 | `GET /api/stats?pw=...` — 관리자 대시보드가 읽는 JSON (응답 형태는 Netlify 때와 동일) |
| 대시보드 | `/gamma/` — `build.py` 의 `ADMIN_PATH` 로 바꾼다. robots.txt에는 적지 않는다(경로 광고가 되므로) |
| 저장 | `/home/blog/data/stats.tsv` — 텍스트 파일. DB 없음 |
| 비밀번호 | 기본 `gamma`. 서버의 `/home/blog/data/admin.pw` 파일이 있으면 그 값이 우선(배포 없이 변경) |

집계 파일은 웹루트 **밖**에 있어 배포(`git reset`)로 지워지지 않고 외부에서 읽히지도 않습니다.
초기화가 필요하면 `GET /api/stats?pw=...&reset=1`.

**알아둘 한계**

- **누적 조회수는 0부터 다시 시작합니다.** Netlify Blobs에 쌓였던 데이터는 이관하지 않습니다.
- **집계 1건마다 파일을 통째로 다시 씁니다.** 한 건도 잃지 않는 대신 track 요청이 직렬화됩니다.
  현재 트래픽에선 문제없지만, 크롤러 버스트가 잦아지면 주기적 flush로 바꿔야 합니다.
- **경로는 ASCII 슬러그만 집계됩니다.** 한글 슬러그를 쓰기 시작하면 그 글의 조회수가 빠집니다
  (거부 시 Resin 로그에 남습니다). 슬러그 규칙을 바꾸려면 `track.jsp` 의 `validPath` 도 함께 고쳐야 합니다.
- **첫 설치에서 가장 깨지기 쉬운 지점**은 `WEB-INF` 아래 JSP를 `<jsp-file>` 로 매핑한 부분입니다.
  스펙상 정상이지만 Resin 4.0.67 실측이 안 됐습니다. 설치가이드 4장의 `curl -X POST .../api/track` 이
  204가 아니라 **404**를 내면 이 문제이며, JSP를 `/api/` 아래로 옮기는 폴백이 필요합니다.
