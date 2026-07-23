<%@ page contentType="application/json; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  POST /api/update?pw=...  — 관리자 대시보드(/gamma/)의 "프로그램 갱신" 버튼이 호출한다.
  /home/blog 에서 GitHub의 최신본을 서버로 당겨오고, git 출력을 그대로 JSON으로 돌려준다.

  연산은 `git fetch origin <branch>` → `git reset --hard origin/<branch>` 두 단계다.
  (pull=merge 가 아니다. 이 저장소의 배포 브랜치는 GitHub Actions가 매번 통째로 갈아끼우므로,
   서버는 로컬을 원격에 맞춰 강제로 리셋하는 것이 맞다. pull 로 하면 merge 커밋이 생겨
   원격과 분기되고, 원격이 force-push 로 되감겼을 때 충돌한다.)

  응답: { ok:bool, exit:int, ms:long, output:"git이 출력한 내용" }
        인증 실패 401 {"error":"unauthorized"} / 사용 중 409 {"error":"busy"} / 꺼짐 403

  ── 이 엔드포인트는 웹 요청으로 서버에서 프로세스를 실행한다. 안전장치를 코드에 박아 둔다: ──
    · 비밀번호(stats와 동일) 없이는 아무것도 못 한다.
    · POST 전용 — 링크 프리뷰·크롤러의 GET으로 실행되지 않는다.
    · 명령은 셸을 거치지 않고 인자 배열로만 실행한다 → 셸/커맨드 인젝션 원천 차단.
      사용자 입력을 명령에 섞지 않는다(고정 명령: git fetch / git reset --hard).
    · 타임아웃(기본 60초) — 네트워크가 멈춰도 스레드를 영원히 붙잡지 않는다.
    · 동시 실행 1건으로 제한 — 버튼 연타로 git이 겹쳐 돌지 않는다.
    · updateEnabled=false 면 통째로 꺼진다(운영 중 잠글 수 있게).
--%>
<%!
  // 한 번에 하나만. 버튼 연타/중복 요청 방지.
  static final java.util.concurrent.atomic.AtomicBoolean RUNNING =
      new java.util.concurrent.atomic.AtomicBoolean(false);

  static String initParam(javax.servlet.ServletContext ctx, String name, String dflt) {
    String v = ctx.getInitParameter(name);
    return (v == null || v.trim().length() == 0) ? dflt : v.trim();
  }

  // git 명령 하나를 셸 없이 실행하고, 표준출력+표준에러를 합쳐 돌려준다.
  // 반환 [0]=exitCode(문자열, 타임아웃이면 "timeout"), [1]=출력, [2]=소요ms
  static String[] run(java.io.File dir, long timeoutMs, String... cmd) throws Exception {
    // 익명 스레드가 캡처할 값은 final 로 고정한다(소스 레벨 6/7 호환).
    final long limit = timeoutMs;
    ProcessBuilder pb = new ProcessBuilder(cmd);
    pb.directory(dir);
    pb.redirectErrorStream(true);          // stderr 를 stdout 에 합쳐 한 스트림으로 읽는다
    // 시스템 서비스로 뜬 Resin은 PATH가 빈약할 수 있다. git이 쓰는 최소 PATH를 보강한다.
    java.util.Map<String, String> env = pb.environment();
    String path = env.get("PATH");
    env.put("PATH", (path == null ? "" : path + java.io.File.pathSeparator) + "/usr/bin:/usr/local/bin:/bin");
    env.put("GIT_TERMINAL_PROMPT", "0");   // 자격증명 프롬프트로 멈추지 않게(공개 저장소라 불필요)

    long t0 = System.currentTimeMillis();
    final Process proc = pb.start();

    // 타임아웃 감시: 시간이 지나면 프로세스를 죽인다(데몬 스레드).
    // destroy 후에도 손자 프로세스(git-remote-https 등)가 파이프를 물고 있으면
    // readLine 이 EOF 를 못 받을 수 있어, 3초 뒤 한 번 더 강제 종료를 시도한다.
    final boolean[] killed = { false };
    Thread watch = new Thread() {
      public void run() {
        try {
          Thread.sleep(limit);
          killed[0] = true;
          proc.destroy();
          Thread.sleep(3000);
          try { proc.getClass().getMethod("destroyForcibly").invoke(proc); }  // Java 8+면 확실히 죽인다
          catch (Throwable ignore) { proc.destroy(); }                        // 6/7이면 한 번 더
        } catch (InterruptedException ignore) { }
      }
    };
    watch.setDaemon(true);
    watch.start();

    StringBuilder out = new StringBuilder();
    java.io.BufferedReader r = new java.io.BufferedReader(
        new java.io.InputStreamReader(proc.getInputStream(), "UTF-8"));
    try {
      String line;
      while ((line = r.readLine()) != null) {
        if (out.length() < 64 * 1024) out.append(line).append('\n');  // 폭주 방지 상한
      }
    } finally { try { r.close(); } catch (Exception ignore) { } }

    int code = proc.waitFor();
    watch.interrupt();
    long ms = System.currentTimeMillis() - t0;
    String exit = killed[0] ? "timeout" : String.valueOf(code);
    return new String[] { exit, out.toString(), String.valueOf(ms) };
  }
%>
<%
  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Robots-Tag", "noindex, nofollow");
  javax.servlet.ServletContext ctx = application;
  out.clearBuffer();

  // 실행으로 오해될 여지가 큰 기능이므로, 켜져 있을 때만 동작한다.
  if (!"true".equals(initParam(ctx, "updateEnabled", "true"))) {
    response.setStatus(403);
    out.print("{\"error\":\"disabled\"}");
    return;
  }

  // GET 등으로는 절대 실행하지 않는다.
  if (!"POST".equals(request.getMethod())) {
    response.setStatus(405);
    out.print("{\"error\":\"method_not_allowed\"}");
    return;
  }

  if (!pwEquals(request.getParameter("pw"), adminPw(ctx))) {
    response.setStatus(401);
    out.print("{\"error\":\"unauthorized\"}");
    return;
  }

  // 이미 돌고 있으면 겹쳐 실행하지 않는다.
  if (!RUNNING.compareAndSet(false, true)) {
    response.setStatus(409);
    out.print("{\"error\":\"busy\"}");
    return;
  }

  try {
    String gitDir = initParam(ctx, "gitDir", "/home/blog");
    String gitBin = initParam(ctx, "gitBin", "git");
    String branch = initParam(ctx, "gitBranch", "deploy");
    long timeoutMs = 1000L * Long.parseLong(initParam(ctx, "gitTimeoutSec", "60"));

    java.io.File dir = new java.io.File(gitDir);
    if (!new java.io.File(dir, ".git").exists()) {
      response.setStatus(500);
      out.print("{\"ok\":false,\"error\":\"not_a_git_repo\",\"output\":"
          + "\"" + jsonEscape(gitDir + " 에 .git 이 없습니다. gitDir 설정을 확인하세요.") + "\"}");
      return;
    }

    // 1) 원격을 받아온다.
    String[] f = run(dir, timeoutMs, gitBin, "fetch", "origin", branch);
    StringBuilder log = new StringBuilder();
    log.append("$ git fetch origin ").append(branch).append('\n').append(f[1]);

    boolean ok = "0".equals(f[0]);
    String exit = f[0];
    long ms = Long.parseLong(f[2]);

    // 2) fetch 가 성공했을 때만 로컬을 원격에 맞춘다.
    if (ok) {
      String[] rs = run(dir, timeoutMs, gitBin, "reset", "--hard", "origin/" + branch);
      log.append("\n$ git reset --hard origin/").append(branch).append('\n').append(rs[1]);
      ok = "0".equals(rs[0]);
      exit = rs[0];
      ms += Long.parseLong(rs[2]);
    }

    ctx.log("[malgnblog] update: exit=" + exit + " ms=" + ms);

    StringBuilder b = new StringBuilder(1024);
    b.append("{\"ok\":").append(ok)
     .append(",\"exit\":\"").append(jsonEscape(exit)).append("\"")
     .append(",\"ms\":").append(ms)
     .append(",\"output\":\"").append(jsonEscape(log.toString())).append("\"}");
    out.print(b.toString());

  } catch (Exception e) {
    response.setStatus(500);
    out.print("{\"ok\":false,\"error\":\"exec_failed\",\"output\":\""
        + jsonEscape(String.valueOf(e)) + "\"}");
  } finally {
    RUNNING.set(false);
  }
%>
