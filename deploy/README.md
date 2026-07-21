# 자동 배포 — 운영자용

`main`에 push하면 사이트가 자동으로 갱신됩니다. **서버는 담당자가 최초 1회 설정한 뒤 손대지 않습니다.**

```
git push main
     │
     ▼
GitHub Actions ─ 빌드(build.py) → 건전성 검사 → deploy 브랜치에 정적 HTML 커밋
                                                        │
웹서버 cron (2분마다) ─ git fetch ──────────────────────┘
                      → 웹루트 반영
```

- **서버에 자격증명이 없습니다.** 공개 저장소를 읽기만 하므로 토큰·키가 필요 없습니다.
- **서버에 빌드 환경이 없습니다.** GitHub이 빌드까지 끝냅니다. 서버는 `git`과 `rsync`만 씁니다.
- **인바운드 포트를 열지 않습니다.** 서버 → github.com 아웃바운드만 씁니다.

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

[서버담당자-설치가이드.md](서버담당자-설치가이드.md)와 [nginx-blog.conf](nginx-blog.conf)를 전달하세요.
보안 관점 요약(인바운드 없음·자격증명 없음·실행되는 것은 git/rsync뿐)이 문서 앞머리에 정리되어 있습니다.

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

## 알려진 미해결 항목

**조회수 집계와 `/admin` 통계는 동작하지 않습니다.** Netlify Functions + Blobs에 종속된 기능이라
자체서버에는 대체 구현이 없습니다. nginx에서 `/api/track`을 204로 받아 404 로그만 막아둔 상태이며,
**수집은 되지 않고 `/admin` 대시보드도 비어 보입니다.** 통계가 필요하면 별도 결정이 필요합니다.
