# 자체 웹서버 자동배포 설치 가이드

GitHub `main`에 push → 웹훅 수신 → `git pull` → `build.py` → 무중단 교체.

```
GitHub push ──웹훅──▶ nginx /gh-webhook ──▶ webhook.py (127.0.0.1:8099)
                                                │ 서명 검증 후
                                                ▼
                                            deploy.sh
                            fetch → 빌드 → 검사 → current 심볼릭 링크 교체
```

전제: Linux + nginx, root(sudo) 권한, 도메인 `blog.malgnsoft.com`이 이 서버를 가리킴.

---

## 1. 사용자·디렉터리

```bash
sudo useradd -r -m -d /srv/malgnblog -s /bin/bash blog
sudo mkdir -p /srv/malgnblog/{releases,deploy}
sudo chown -R blog:blog /srv/malgnblog
```

## 2. 레포 클론 + 가상환경

```bash
sudo -u blog -H bash <<'EOF'
cd /srv/malgnblog
git clone https://github.com/freerahn6/malgnblog.git repo
python3 -m venv venv
./venv/bin/pip install -q -r repo/requirements.txt
EOF
```

> **비공개 레포라면** HTTPS 대신 배포키(읽기 전용)를 씁니다.
> `sudo -u blog ssh-keygen -t ed25519 -f /srv/malgnblog/.ssh/id_ed25519 -N ''` 로 키를 만들고
> 공개키를 GitHub 레포 → Settings → Deploy keys에 등록한 뒤
> `git clone git@github.com:freerahn6/malgnblog.git repo` 로 클론하세요.

## 3. 배포 스크립트 배치

```bash
sudo cp /srv/malgnblog/repo/deploy/{deploy.sh,webhook.py} /srv/malgnblog/deploy/
sudo chown blog:blog /srv/malgnblog/deploy/*
sudo chmod +x /srv/malgnblog/deploy/deploy.sh
```

> 레포 안의 것을 직접 쓰지 않고 복사해 두는 이유: 배포 중 `git reset --hard`가
> 실행 중인 스크립트 자신을 갈아엎는 상황을 피하기 위해서입니다.
> **스크립트를 수정했을 때는 이 복사를 다시 해야 반영됩니다.**

## 4. 첫 빌드 (수동 확인)

```bash
sudo -u blog FORCE=1 /srv/malgnblog/deploy/deploy.sh
ls -l /srv/malgnblog/current      # releases/... 를 가리키면 성공
```

## 5. 시크릿 + 서비스 등록

```bash
# 시크릿 생성 — 이 값을 GitHub 웹훅에도 그대로 넣습니다
SECRET=$(openssl rand -hex 32); echo "$SECRET"

sudo tee /etc/malgnblog.env >/dev/null <<EOF
GH_WEBHOOK_SECRET=$SECRET
DEPLOY_BRANCH=main
DEPLOY_SCRIPT=/srv/malgnblog/deploy/deploy.sh
WEBHOOK_LISTEN=127.0.0.1
WEBHOOK_PORT=8099
EOF
sudo chmod 600 /etc/malgnblog.env

sudo cp /srv/malgnblog/repo/deploy/malgnblog-webhook.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now malgnblog-webhook
sudo systemctl status malgnblog-webhook
```

## 6. nginx

```bash
sudo cp /srv/malgnblog/repo/deploy/nginx-blog.conf /etc/nginx/sites-available/blog.malgnsoft.com
sudo ln -s /etc/nginx/sites-available/blog.malgnsoft.com /etc/nginx/sites-enabled/
sudo nginx -t && sudo systemctl reload nginx
```

SSL이 아직 없다면 먼저 80 포트만 열어 두고:

```bash
sudo certbot --nginx -d blog.malgnsoft.com
```

## 7. GitHub 웹훅 등록

레포 → **Settings → Webhooks → Add webhook**

| 항목 | 값 |
|---|---|
| Payload URL | `https://blog.malgnsoft.com/gh-webhook` |
| Content type | `application/json` |
| Secret | 5단계에서 만든 `$SECRET` |
| Events | **Just the push event** |

저장하면 GitHub가 곧바로 `ping`을 보냅니다. **Recent Deliveries**에서 `200 pong`이면 연결 성공.

---

## 운영

```bash
# 배포 로그
sudo journalctl -u malgnblog-webhook -f

# 수동 배포 / 강제 재빌드
sudo -u blog /srv/malgnblog/deploy/deploy.sh
sudo -u blog FORCE=1 /srv/malgnblog/deploy/deploy.sh

# 롤백 — 직전 릴리스로 되돌리기
ls -1dt /srv/malgnblog/releases/*/          # 최근 5개 보관
sudo -u blog ln -sfn /srv/malgnblog/releases/<원하는릴리스> /srv/malgnblog/current.tmp
sudo -u blog mv -Tf /srv/malgnblog/current.tmp /srv/malgnblog/current
```

### 안전장치
- **서명 검증** — `X-Hub-Signature-256` HMAC이 맞지 않으면 401. 시크릿을 모르면 배포를 트리거할 수 없습니다.
- **브랜치 필터** — `main` 외 브랜치 push는 무시합니다.
- **중복 실행 차단** — 연속 push가 와도 `flock`으로 한 번만 실행됩니다.
- **건전성 검사** — 빌드 결과가 index.html 없음 / 페이지 20개 미만 / sitemap 누락이면 **교체하지 않고 기존 배포를 유지**합니다. 깨진 빌드가 서비스에 올라가지 않습니다.
- **원자적 교체** — `mv -Tf`(rename)로 심볼릭 링크를 바꾸므로 교체 중 반쪽짜리 사이트가 보이는 순간이 없습니다.
- **롤백 보관** — 최근 5개 릴리스를 남깁니다.

### 알려진 미해결 항목
- **조회수 집계 / `/admin` 통계**: Netlify Functions + Blobs에 종속된 기능이라 자체서버에는 대체 구현이 없습니다.
  nginx 설정에서 `/api/track`을 204로 받아 오류만 막아둔 상태이며, **수집은 되지 않습니다.**
  `/admin` 대시보드도 데이터가 비어 보입니다. 통계가 필요하면 별도 결정이 필요합니다.
