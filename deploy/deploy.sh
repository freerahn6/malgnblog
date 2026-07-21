#!/usr/bin/env bash
# malgnblog 배포 스크립트
#   origin/<branch> 최신 반영 → build.py 빌드 → 건전성 검사 → 원자적 교체
#
# 수동 실행:  sudo -u blog /srv/malgnblog/deploy/deploy.sh
# 강제 재빌드: FORCE=1 sudo -u blog /srv/malgnblog/deploy/deploy.sh
set -euo pipefail

ROOT="${BLOG_ROOT:-/srv/malgnblog}"
REPO="$ROOT/repo"
VENV="$ROOT/venv"
RELEASES="$ROOT/releases"
CURRENT="$ROOT/current"
BRANCH="${DEPLOY_BRANCH:-main}"
KEEP="${KEEP_RELEASES:-5}"
MIN_PAGES="${MIN_PAGES:-20}"   # 이보다 적게 생성되면 빌드 실패로 간주

log() { printf '[%s] %s\n' "$(date '+%F %T')" "$*"; }
fail() { log "❌ $*"; exit 1; }

mkdir -p "$RELEASES"

# 동시 실행 방지 — 웹훅이 연달아 와도 한 번만 돈다
exec 9>"$ROOT/.deploy.lock"
if ! flock -n 9; then
  log "다른 배포가 진행 중 — 이번 요청은 건너뜁니다"
  exit 0
fi

cd "$REPO"

git fetch --prune origin "$BRANCH"
NEW=$(git rev-parse "origin/$BRANCH")
CUR=$(git rev-parse HEAD)

if [ "$NEW" = "$CUR" ] && [ -e "$CURRENT" ] && [ "${FORCE:-0}" != "1" ]; then
  log "변경 없음 (${CUR:0:7}) — 건너뜁니다"
  exit 0
fi

log "배포 시작: ${CUR:0:7} → ${NEW:0:7}"
git reset --hard "origin/$BRANCH"

# 의존성 — requirements.txt가 바뀌었을 때만 실질적으로 동작(이미 충족되면 즉시 통과)
"$VENV/bin/pip" install -q -r requirements.txt

# build.py는 기존 산출물을 지우지 않고 덮어쓰기만 한다.
# 비우지 않으면 삭제·이름변경된 글의 옛 페이지가 계속 살아남는다.
rm -rf "$REPO/_deploy/public"

log "빌드 중..."
"$VENV/bin/python" build.py

# ---- 건전성 검사: 조용히 실패한 빌드를 서비스에 올리지 않는다 ----
OUT="$REPO/_deploy/public"
[ -s "$OUT/index.html" ] || fail "index.html이 없거나 비어 있음 — 기존 배포를 유지합니다"
PAGES=$(find "$OUT" -name index.html | wc -l)
[ "$PAGES" -ge "$MIN_PAGES" ] || fail "생성 페이지 $PAGES 개(최소 $MIN_PAGES) — 기존 배포를 유지합니다"
[ -s "$OUT/sitemap.xml" ] || fail "sitemap.xml 누락 — 기존 배포를 유지합니다"

# ---- 원자적 교체 ----
REL="$RELEASES/$(date +%Y%m%d-%H%M%S)-${NEW:0:7}"
mkdir -p "$REL"
cp -a "$OUT/." "$REL/"

ln -sfn "$REL" "$CURRENT.tmp"
mv -Tf "$CURRENT.tmp" "$CURRENT"      # rename(2) — 교체 순간 끊김 없음
log "✅ 교체 완료: $REL (페이지 $PAGES 개)"

# ---- 오래된 릴리스 정리(롤백용으로 $KEEP개 보관) ----
ls -1dt "$RELEASES"/*/ 2>/dev/null | tail -n +$((KEEP + 1)) | xargs -r rm -rf

log "배포 종료"
