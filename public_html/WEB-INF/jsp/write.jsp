<%@ page contentType="application/json; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" buffer="256kb" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  글 쓰기 API — 관리자 콘솔(/gamma2)의 [새 글]·[수정] 저장이 호출한다.

  POST /api/posts/write                     (Apache가 blanket /api/ 로 갱신된 뒤 쓸 수 있는 정식 경로)
  POST /api/stats?write=1                   (현재 실서버 경로 — stats.jsp 가 여기로 forward 한다)

  ─ 왜 GitHub 에 커밋하나
  서버 워킹트리에 직접 쓰면 다음 [프로그램 갱신] 때 update.jsp 의
  `git reset --hard origin/deploy` 로 지워진다. 원고의 진실은 원격 저장소의 main 이고,
  거기에 커밋해야 Actions 가 다시 빌드해 deploy 브랜치로 내려온다. 그래서 이 JSP 는
  "로컬에 쓰기"가 아니라 "GitHub Contents API 로 원격 커밋"을 대행한다.

  ─ 파라미터 (전부 POST 본문. 쿼리스트링에 넣지 말 것)
    pw       관리자 비밀번호            (필수)
    action   get | save                 (필수)
    file     원고 파일명 "slug.md"      (필수, ^[a-z0-9][a-z0-9-]*\.md$)
    content  저장할 마크다운 원문 전체  (action=save 필수)
    sha      직전에 받은 blob sha       (action=save 에서 '수정'일 때 필수 / '신규'면 생략)
    message  커밋 메시지                (선택)

  비밀번호를 POST 본문으로만 받는 이유: 쓰기 권한이 붙은 요청의 비번이
  Apache/Resin 액세스로그에 평문으로 남지 않게 하기 위해서다(기획서 F4).

  ─ 응답
    200 {"ok":true,"file":..,"sha":..,"content":".."}          action=get
    200 {"ok":true,"sha":newSha,"commit":"https://..."}        action=save
    400 {"error":"bad_request","detail":".."}
    401 {"error":"unauthorized"}
    403 {"error":"write_disabled"}      writeEnabled=false
    404 {"error":"not_found"}           원고 없음(get)
    409 {"error":"sha_conflict"}        그사이 원격이 바뀜 / 신규인데 이미 있음
    502 {"error":"github_unavailable","detail":".."}
    503 {"error":"no_token"}            서버에 github.token 이 없음

  ─ frontmatter 조립은 서버가 하지 않는다
  콘솔이 원문(raw)을 받아 편집한 뒤 '완성된 마크다운 전문'을 content 로 보낸다.
  서버는 그대로 커밋만 한다. YAML 재직렬화를 JSP 안에서 하면 build.py 의 파싱 규약과
  두 곳에서 어긋날 수 있고(특히 faq·tags 같은 build.py 가 안 읽는 필드), 여기는
  로컬 검증이 안 되는 코드다. 조립은 콘솔 한 곳에만 둔다.
--%>
<%!
  // ── GitHub Contents API 설정 (web.xml context-param) ──────────────────────
  static String cfg(javax.servlet.ServletContext ctx, String k, String dflt) {
    String v = ctx.getInitParameter(k);
    return (v == null || v.trim().length() == 0) ? dflt : v.trim();
  }

  /** 토큰은 웹루트 밖 파일에서만 읽는다. git reset 영향 밖이고 브라우저로 절대 안 나간다. */
  static String githubToken(javax.servlet.ServletContext ctx) {
    String p = cfg(ctx, "githubTokenFile", "");
    java.io.File f = (p.length() > 0) ? new java.io.File(p)
                                      : new java.io.File(dataDir(ctx), "github.token");
    if (!f.isFile()) return null;
    java.io.BufferedReader r = null;
    try {
      r = new java.io.BufferedReader(new java.io.InputStreamReader(
            new java.io.FileInputStream(f), "UTF-8"));
      String line = r.readLine();
      if (line != null && line.trim().length() > 0) return line.trim();
    } catch (Exception ignore) {
    } finally { if (r != null) try { r.close(); } catch (Exception ignore) { } }
    return null;
  }

  // ── Base64 (Java 6/7 호환 — java.util.Base64 를 쓰지 않는다) ───────────────
  static final char[] B64 = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/".toCharArray();

  static String b64encode(byte[] in) {
    StringBuilder b = new StringBuilder((in.length + 2) / 3 * 4);
    for (int i = 0; i < in.length; i += 3) {
      int b0 = in[i] & 0xff;
      int b1 = (i + 1 < in.length) ? (in[i + 1] & 0xff) : -1;
      int b2 = (i + 2 < in.length) ? (in[i + 2] & 0xff) : -1;
      b.append(B64[b0 >>> 2]);
      b.append(B64[((b0 & 0x03) << 4) | (b1 < 0 ? 0 : (b1 >>> 4))]);
      b.append(b1 < 0 ? '=' : B64[((b1 & 0x0f) << 2) | (b2 < 0 ? 0 : (b2 >>> 6))]);
      b.append(b2 < 0 ? '=' : B64[b2 & 0x3f]);
    }
    return b.toString();
  }

  static byte[] b64decode(String s) {
    int[] rev = new int[128];
    for (int i = 0; i < 128; i++) rev[i] = -1;
    for (int i = 0; i < B64.length; i++) rev[B64[i]] = i;
    java.io.ByteArrayOutputStream o = new java.io.ByteArrayOutputStream(s.length() * 3 / 4 + 3);
    int buf = 0, bits = 0;
    for (int i = 0; i < s.length(); i++) {
      char c = s.charAt(i);
      if (c == '=' ) break;
      if (c > 127 || rev[c] < 0) continue;            // 개행 등은 건너뛴다
      buf = (buf << 6) | rev[c];
      bits += 6;
      if (bits >= 8) { bits -= 8; o.write((buf >>> bits) & 0xff); }
    }
    return o.toByteArray();
  }

  // ── 아주 작은 JSON 리더 (응답에서 문자열 필드 하나만 꺼낸다) ────────────────
  /** from 이후에서 "key":"..." 를 찾아 이스케이프를 푼 값을 준다. 없으면 null. */
  static String jsonStr(String json, String key, int from) {
    String needle = "\"" + key + "\"";
    int i = json.indexOf(needle, from);
    if (i < 0) return null;
    i += needle.length();
    while (i < json.length() && (json.charAt(i) == ' ' || json.charAt(i) == ':')) i++;
    if (i >= json.length() || json.charAt(i) != '"') return null;   // 문자열이 아닌 필드
    i++;
    StringBuilder b = new StringBuilder();
    while (i < json.length()) {
      char c = json.charAt(i++);
      if (c == '"') break;
      if (c != '\\') { b.append(c); continue; }
      if (i >= json.length()) break;
      char e = json.charAt(i++);
      switch (e) {
        case 'n': b.append('\n'); break;
        case 'r': b.append('\r'); break;
        case 't': b.append('\t'); break;
        case 'b': b.append('\b'); break;
        case 'f': b.append('\f'); break;
        case 'u':
          if (i + 4 <= json.length()) {
            try { b.append((char) Integer.parseInt(json.substring(i, i + 4), 16)); } catch (Exception ig) { }
            i += 4;
          }
          break;
        default: b.append(e);
      }
    }
    return b.toString();
  }

  /** GitHub API 한 번 호출. 결과를 [상태코드, 본문] 으로 돌려준다. */
  static Object[] api(javax.servlet.ServletContext ctx, String method, String url,
                      String token, String body, int timeoutMs) throws java.io.IOException {
    java.net.HttpURLConnection c =
        (java.net.HttpURLConnection) new java.net.URL(url).openConnection();
    try {
      c.setRequestMethod(method);
      c.setConnectTimeout(timeoutMs);
      c.setReadTimeout(timeoutMs);
      c.setInstanceFollowRedirects(false);
      c.setRequestProperty("Authorization", "token " + token);
      c.setRequestProperty("Accept", "application/vnd.github+json");
      c.setRequestProperty("X-GitHub-Api-Version", "2022-11-28");
      c.setRequestProperty("User-Agent", "malgnblog-admin");   // 없으면 GitHub 이 403
      if (body != null) {
        byte[] payload = body.getBytes("UTF-8");
        c.setDoOutput(true);
        c.setFixedLengthStreamingMode(payload.length);
        c.setRequestProperty("Content-Type", "application/json; charset=utf-8");
        java.io.OutputStream os = c.getOutputStream();
        try { os.write(payload); os.flush(); } finally { try { os.close(); } catch (Exception ig) { } }
      }
      int code = c.getResponseCode();
      java.io.InputStream in = (code >= 400) ? c.getErrorStream() : c.getInputStream();
      StringBuilder sb = new StringBuilder(4096);
      if (in != null) {
        java.io.Reader r = new java.io.InputStreamReader(in, "UTF-8");
        try {
          char[] cb = new char[4096];
          int n;
          while ((n = r.read(cb)) != -1) sb.append(cb, 0, n);
        } finally { try { r.close(); } catch (Exception ig) { } }
      }
      return new Object[]{ Integer.valueOf(code), sb.toString() };
    } finally {
      try { c.disconnect(); } catch (Exception ig) { }
    }
  }

  /** 감사 로그 1줄. 실패해도 요청은 계속된다(로그 때문에 저장을 막지 않는다). */
  static void audit(javax.servlet.ServletContext ctx, String line) {
    java.io.Writer w = null;
    try {
      java.text.SimpleDateFormat f = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
      f.setTimeZone(java.util.TimeZone.getTimeZone("Asia/Seoul"));
      w = new java.io.OutputStreamWriter(
            new java.io.FileOutputStream(new java.io.File(dataDir(ctx), "admin.log"), true), "UTF-8");
      w.write(f.format(new java.util.Date()) + "\t" + line + "\n");
    } catch (Exception e) {
      ctx.log("[malgnblog] admin.log 기록 실패: " + e);
    } finally { if (w != null) try { w.close(); } catch (Exception ig) { } }
  }
%>
<%
  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Robots-Tag", "noindex, nofollow");

  javax.servlet.ServletContext ctx = application;
  out.clearBuffer();

  // POST 전용. 크롤러·링크프리뷰의 GET 으로 커밋이 일어나면 안 된다.
  if (!"POST".equals(request.getMethod())) {
    response.setStatus(405);
    response.setHeader("Allow", "POST");
    out.print("{\"error\":\"method_not_allowed\"}");
    return;
  }
  request.setCharacterEncoding("UTF-8");

  if (!"true".equals(cfg(ctx, "writeEnabled", "true"))) {
    response.setStatus(403);
    out.print("{\"error\":\"write_disabled\"}");
    return;
  }
  if (!pwEquals(request.getParameter("pw"), adminPw(ctx))) {
    response.setStatus(401);
    out.print("{\"error\":\"unauthorized\"}");
    return;
  }

  String token = githubToken(ctx);
  if (token == null) {
    response.setStatus(503);
    out.print("{\"error\":\"no_token\",\"detail\":\"서버에 github.token 이 없습니다\"}");
    return;
  }

  String action = request.getParameter("action");
  String file   = request.getParameter("file");

  // 파일명은 articles/ 안의 단일 .md 로만 제한한다. 경로 구분자·상위 이동을 원천 차단.
  if (file == null || !file.matches("[a-z0-9][a-z0-9-]*\\.md")) {
    response.setStatus(400);
    out.print("{\"error\":\"bad_request\",\"detail\":\"file 형식이 올바르지 않습니다(slug.md)\"}");
    return;
  }

  String repo    = cfg(ctx, "githubRepo", "freerahn6/malgnblog");
  String branch  = cfg(ctx, "githubBranch", "main");
  String dir     = cfg(ctx, "githubArticleDir", "articles");
  int timeoutMs  = 10000;
  try { timeoutMs = Integer.parseInt(cfg(ctx, "githubTimeoutSec", "10")) * 1000; } catch (Exception ig) { }

  String base = "https://api.github.com/repos/" + repo + "/contents/" + dir + "/" + file;

  try {
    // ── action=get : 편집할 원문 + sha ────────────────────────────────────
    if ("get".equals(action)) {
      Object[] rs = api(ctx, "GET", base + "?ref=" + branch, token, null, timeoutMs);
      int code = ((Integer) rs[0]).intValue();
      String bodyTxt = (String) rs[1];
      if (code == 404) {
        response.setStatus(404);
        out.print("{\"error\":\"not_found\"}");
        return;
      }
      if (code != 200) {
        response.setStatus(502);
        out.print("{\"error\":\"github_unavailable\",\"detail\":\"" + jsonEscape("HTTP " + code) + "\"}");
        return;
      }
      String sha = jsonStr(bodyTxt, "sha", 0);
      String enc = jsonStr(bodyTxt, "content", 0);
      String raw = (enc == null) ? "" : new String(b64decode(enc), "UTF-8");
      out.print("{\"ok\":true,\"file\":\"" + jsonEscape(file) + "\",\"sha\":\"" + jsonEscape(sha)
                + "\",\"content\":\"" + jsonEscape(raw) + "\"}");
      return;
    }

    // ── action=save : 원격 main 에 1커밋 ──────────────────────────────────
    if ("save".equals(action)) {
      String content = request.getParameter("content");
      String sha     = request.getParameter("sha");
      String msg     = request.getParameter("message");
      if (content == null || content.trim().length() == 0) {
        response.setStatus(400);
        out.print("{\"error\":\"bad_request\",\"detail\":\"content 가 비었습니다\"}");
        return;
      }
      if (content.length() > 400000) {           // 원고 한 편이 이보다 클 이유가 없다
        response.setStatus(400);
        out.print("{\"error\":\"bad_request\",\"detail\":\"content 가 너무 큽니다\"}");
        return;
      }
      if (msg == null || msg.trim().length() == 0) msg = "콘솔 저장: " + file;

      StringBuilder req = new StringBuilder(content.length() * 2 + 512);
      req.append("{\"message\":\"").append(jsonEscape(msg))
         .append("\",\"branch\":\"").append(jsonEscape(branch))
         .append("\",\"content\":\"").append(b64encode(content.getBytes("UTF-8"))).append('"');
      // sha 가 있으면 '수정'(낙관적 잠금), 없으면 '신규 생성'.
      // 신규인데 파일이 이미 있으면 GitHub 이 422 를 준다 → 409 로 바꿔 콘솔이 안내한다.
      if (sha != null && sha.trim().length() > 0) {
        req.append(",\"sha\":\"").append(jsonEscape(sha.trim())).append('"');
      }
      req.append('}');

      Object[] rs = api(ctx, "PUT", base, token, req.toString(), timeoutMs);
      int code = ((Integer) rs[0]).intValue();
      String bodyTxt = (String) rs[1];

      if (code == 409 || code == 422) {
        audit(ctx, "save\t" + file + "\tCONFLICT " + code);
        response.setStatus(409);
        out.print("{\"error\":\"sha_conflict\",\"detail\":\""
                  + jsonEscape(sha == null || sha.length() == 0
                      ? "같은 슬러그의 원고가 이미 있습니다"
                      : "다른 곳에서 먼저 수정됐습니다") + "\"}");
        return;
      }
      if (code != 200 && code != 201) {
        String detail = jsonStr(bodyTxt, "message", 0);
        audit(ctx, "save\t" + file + "\tFAIL " + code + " " + (detail == null ? "" : detail));
        ctx.log("[malgnblog] GitHub 저장 실패 " + code + ": " + bodyTxt);
        response.setStatus(502);
        out.print("{\"error\":\"github_unavailable\",\"detail\":\""
                  + jsonEscape("HTTP " + code + (detail == null ? "" : " " + detail)) + "\"}");
        return;
      }

      // 응답: {"content":{...,"sha":".."},"commit":{"sha":..,"html_url":".."}}
      // 첫 "sha" 는 content.sha(= 다음 낙관적 잠금 기준), commit 쪽은 html_url 만 쓴다.
      String newSha = jsonStr(bodyTxt, "sha", 0);
      int ci = bodyTxt.indexOf("\"commit\"");
      String commitUrl = (ci < 0) ? null : jsonStr(bodyTxt, "html_url", ci);
      audit(ctx, "save\t" + file + "\tOK " + (sha == null || sha.length() == 0 ? "create" : "update")
                 + " " + (newSha == null ? "" : newSha));
      out.print("{\"ok\":true,\"sha\":\"" + jsonEscape(newSha) + "\",\"commit\":\""
                + jsonEscape(commitUrl == null ? "" : commitUrl) + "\"}");
      return;
    }

    response.setStatus(400);
    out.print("{\"error\":\"bad_request\",\"detail\":\"action 은 get 또는 save\"}");

  } catch (java.net.SocketTimeoutException e) {
    ctx.log("[malgnblog] GitHub 타임아웃: " + e);
    response.setStatus(502);
    out.print("{\"error\":\"github_unavailable\",\"detail\":\"응답 시간 초과\"}");
  } catch (Exception e) {
    ctx.log("[malgnblog] write.jsp 오류: " + e);
    response.setStatus(502);
    out.print("{\"error\":\"github_unavailable\",\"detail\":\"" + jsonEscape(String.valueOf(e)) + "\"}");
  }
%>
