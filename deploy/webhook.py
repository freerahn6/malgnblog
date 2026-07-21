#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""GitHub push 웹훅 수신기 — 표준 라이브러리만 사용.

nginx가 https://blog.malgnsoft.com/gh-webhook 을 이 프로세스(127.0.0.1:8099)로
넘겨주고, 서명이 검증된 대상 브랜치 push에 대해서만 deploy.sh를 실행한다.

설정은 환경변수로 주입한다(systemd EnvironmentFile 참고):
  GH_WEBHOOK_SECRET  필수. GitHub 웹훅에 등록한 것과 동일한 시크릿
  DEPLOY_BRANCH      기본 main
  DEPLOY_SCRIPT      기본 /srv/malgnblog/deploy/deploy.sh
  WEBHOOK_LISTEN     기본 127.0.0.1  (외부에 직접 노출하지 말 것 — nginx 뒤에 둔다)
  WEBHOOK_PORT       기본 8099
"""
import hmac
import json
import os
import subprocess
import sys
import threading
from hashlib import sha256
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

SECRET = os.environ.get("GH_WEBHOOK_SECRET", "").encode()
BRANCH = os.environ.get("DEPLOY_BRANCH", "main")
SCRIPT = os.environ.get("DEPLOY_SCRIPT", "/srv/malgnblog/deploy/deploy.sh")
LISTEN = os.environ.get("WEBHOOK_LISTEN", "127.0.0.1")
PORT = int(os.environ.get("WEBHOOK_PORT", "8099"))

MAX_BODY = 5 * 1024 * 1024  # GitHub push 페이로드 상한 여유분
_deploy_lock = threading.Lock()

# 로그에 한글을 쓴다. LANG이 없는 서버는 stdout 인코딩이 ASCII라 print가 예외를 던지고,
# 그 예외가 요청 핸들러를 죽여 응답 자체가 나가지 않는다. 출력단을 UTF-8로 고정한다.
for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass


def log(msg):
    """로그 실패가 요청 처리를 막아서는 안 된다."""
    try:
        print(msg, flush=True)  # systemd가 journald로 수집
    except Exception:
        pass


def run_deploy(reason):
    """deploy.sh를 백그라운드로 실행. 실제 동시성 차단은 deploy.sh의 flock이 담당."""
    if not _deploy_lock.acquire(blocking=False):
        log(f"배포가 이미 진행 중 — 요청 무시 ({reason})")
        return
    try:
        log(f"배포 실행: {reason}")
        r = subprocess.run(
            ["/usr/bin/env", "bash", SCRIPT],
            capture_output=True, text=True, timeout=900,
        )
        for line in (r.stdout or "").splitlines():
            log(f"  {line}")
        if r.returncode != 0:
            log(f"배포 실패 (exit {r.returncode})")
            for line in (r.stderr or "").splitlines():
                log(f"  ! {line}")
    except subprocess.TimeoutExpired:
        log("배포 시간 초과(15분) — 중단됨")
    except Exception as e:  # 수신기는 어떤 경우에도 죽지 않아야 한다
        log(f"배포 중 예외: {e!r}")
    finally:
        _deploy_lock.release()


class Handler(BaseHTTPRequestHandler):
    server_version = "malgnblog-webhook"

    def _reply(self, code, text):
        body = text.encode()
        self.send_response(code)
        self.send_header("Content-Type", "text/plain; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):  # 기본 stderr 접근로그 억제
        pass

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
        except ValueError:
            return self._reply(400, "bad length")
        if length <= 0 or length > MAX_BODY:
            return self._reply(400, "bad length")

        body = self.rfile.read(length)

        # ---- 서명 검증: 이게 유일한 인증 수단이다 ----
        sig = self.headers.get("X-Hub-Signature-256", "")
        if not SECRET:
            log("GH_WEBHOOK_SECRET 미설정 — 요청 거부")
            return self._reply(500, "server not configured")
        expected = "sha256=" + hmac.new(SECRET, body, sha256).hexdigest()
        if not hmac.compare_digest(sig, expected):
            log(f"서명 불일치 — 거부 (from {self.client_address[0]})")
            return self._reply(401, "bad signature")

        event = self.headers.get("X-GitHub-Event", "")
        if event == "ping":
            log("ping 수신 — 웹훅 연결 정상")
            return self._reply(200, "pong")
        if event != "push":
            return self._reply(204, "")

        try:
            payload = json.loads(body)
        except json.JSONDecodeError:
            return self._reply(400, "bad json")

        ref = payload.get("ref", "")
        if ref != f"refs/heads/{BRANCH}":
            log(f"대상 브랜치 아님({ref}) — 무시")
            return self._reply(204, "")

        after = (payload.get("after") or "")[:7]
        pusher = (payload.get("pusher") or {}).get("name", "?")

        # GitHub는 10초 안에 응답을 기대한다. 먼저 응답하고 배포는 뒤에서 돌린다.
        self._reply(202, "accepted")
        threading.Thread(
            target=run_deploy, args=(f"push {after} by {pusher}",), daemon=True
        ).start()

    def do_GET(self):
        # 헬스체크용 — 시크릿·상태를 노출하지 않는다
        self._reply(200, "ok")


def main():
    if not SECRET:
        print("GH_WEBHOOK_SECRET이 설정되지 않았습니다.", file=sys.stderr)
        sys.exit(1)
    srv = ThreadingHTTPServer((LISTEN, PORT), Handler)
    log(f"웹훅 수신 대기 {LISTEN}:{PORT} (브랜치 {BRANCH})")
    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        pass


if __name__ == "__main__":
    main()
