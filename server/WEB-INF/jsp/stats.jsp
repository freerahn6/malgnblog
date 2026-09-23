<%@ page contentType="application/json; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  GET /api/stats?pw=...        — 관리자 대시보드(/gamma/)가 읽는 집계 JSON
  GET /api/stats?pw=...&reset=1 — 집계 초기화

  응답 형태는 기존 Netlify 함수와 동일하다(대시보드 코드를 고치지 않기 위해).
    { today, total, days:[{date,count}], posts:[{path,count}], date }

  글감 보드(/new)용 분기 — 아래 declarations 블록 참조
    GET  /api/stats?topics=1&pw=...          목록(삭제분 제외)
    POST /api/stats?topics=del    + pw&id    삭제 기록 추가(멱등)
    POST /api/stats?topics=undel  + pw&id    삭제 기록 제거(복구, 멱등)

  adminPw()·pwEquals()는 stats-store.jspf(공용)에 있다.
--%>
<%!
  /* ──────────────────────────────────────────────────────────────────────
     글감 보드(/new) — 카탈로그 서빙 + 삭제 기록

     왜 여기에 얹나: 실서버 Apache 는 /api/ 를 통째로 프록시하지 않고
     track/stats/update 만 개별 ProxyPass 라 새 엔드포인트는 404 가 난다.
     이미 살아 있는 /api/stats 에 쿼리로 분기한다(?posts=1 과 같은 수법).

     왜 선언을 이 파일 안에 두나: 공용 stats-store.jspf 에 넣으면 track.jsp·
     write.jsp 의 컴파일 단위까지 바뀐다(write.jsp 에는 이미 audit() 이 있어
     이름 충돌 위험도 있다). 여기 두면 다른 JSP 는 손대지 않은 채로 남는다.

     저장 위치: <statsDir>/topics-deleted.json — 웹루트 밖이라 update.jsp 의
     `git reset --hard` 가 건드리지 않는다. 이게 "영구 저장"의 실제 근거다.

     JSON 은 손으로 다룬다(외부 라이브러리 없음). 다만 '파싱'은 아래 4개
     함수로 한정했고, 같은 알고리즘을 파이썬으로 이식해 json 표준 구현과
     차분 대조했다(로컬에 JDK 가 없어 JSP 실행 검증이 불가능하므로).
     ────────────────────────────────────────────────────────────────────── */
  static final int    TOPICS_MAX_CHARS   = 1024 * 1024;   // 파일 읽기 상한(폭주 방어)
  static final int    TOPICS_MAX_DELETED = 5000;          // 삭제 기록 개수 상한
  static final int    TOPICS_MAX_ID      = 64;            // id 길이 상한
  static final String TOPICS_LOCK_ATTR   = "malgnblog.topicsLock";

  /** 삭제 기록 파일 잠금. 정적 include 라 클래스가 따로 생기므로 static 잠금은
   *  공유되지 않는다 → 애플리케이션 스코프에 잠금 객체를 하나 두고 그걸 쓴다.
   *  (ctx 자체를 잠그면 store() 를 부르는 조회수 수집 경로까지 막힌다) */
  static Object topicsLock(javax.servlet.ServletContext ctx) {
    synchronized (ctx) {
      Object o = ctx.getAttribute(TOPICS_LOCK_ATTR);
      if (o == null) {
        // 잠금 전용 객체. 컨테이너가 속성을 직렬화하더라도 안전하도록 Serializable 한 것을 쓴다.
        o = new java.util.ArrayList<String>(0);
        ctx.setAttribute(TOPICS_LOCK_ATTR, o);
      }
      return o;
    }
  }

  // ── 아주 작은 JSON 스캐너 (4개 함수로 끝낸다) ────────────────────────────
  /** 공백·개행을 건너뛴 위치. */
  static int jsWs(String s, int i) {
    while (i < s.length()) {
      char c = s.charAt(i);
      if (c == ' ' || c == '\t' || c == '\n' || c == '\r') i++;
      else break;
    }
    return i;
  }

  /** i 는 여는 따옴표. 닫는 따옴표 '다음' 위치를 준다(형식이 깨졌으면 -1).
   *  out 이 null 이 아니면 이스케이프를 푼 값을 담는다. */
  static int jsString(String s, int i, StringBuilder out) {
    if (i < 0 || i >= s.length() || s.charAt(i) != '"') return -1;
    i++;
    while (i < s.length()) {
      char c = s.charAt(i++);
      if (c == '"') return i;
      if (c != '\\') { if (out != null) out.append(c); continue; }
      if (i >= s.length()) return -1;
      char e = s.charAt(i++);
      if (e == 'u') {
        if (i + 4 > s.length()) return -1;
        if (out != null) {
          try { out.append((char) Integer.parseInt(s.substring(i, i + 4), 16)); }
          catch (Exception ig) { return -1; }
        }
        i += 4;
        continue;
      }
      if (out == null) continue;
      switch (e) {
        case 'n': out.append('\n'); break;
        case 'r': out.append('\r'); break;
        case 't': out.append('\t'); break;
        case 'b': out.append('\b'); break;
        case 'f': out.append('\f'); break;
        default:  out.append(e);
      }
    }
    return -1;
  }

  /** 값 하나(문자열·오브젝트·배열·숫자·리터럴)를 건너뛴 위치. 깨졌으면 -1.
   *  괄호 종류까지 검사하지는 않는다 — 입력은 build.py 가 만든 JSON 이다. */
  static int jsValue(String s, int i) {
    i = jsWs(s, i);
    if (i >= s.length()) return -1;
    char c = s.charAt(i);
    if (c == '"') return jsString(s, i, null);
    if (c == '{' || c == '[') {
      int depth = 0;
      while (i < s.length()) {
        char d = s.charAt(i);
        if (d == '"') { i = jsString(s, i, null); if (i < 0) return -1; continue; }
        if (d == '{' || d == '[') depth++;
        else if (d == '}' || d == ']') { depth--; if (depth == 0) return i + 1; }
        i++;
      }
      return -1;
    }
    int j = i;
    while (j < s.length()) {
      char d = s.charAt(j);
      if (d == ',' || d == '}' || d == ']' || d == ' ' || d == '\t' || d == '\n' || d == '\r') break;
      j++;
    }
    return (j == i) ? -1 : j;
  }

  /** 오브젝트에서 문자열 필드 하나를 꺼낸다(중첩 값은 건너뛴다). 없으면 null. */
  static String jsField(String obj, String name) {
    if (obj == null) return null;
    int i = jsWs(obj, 0);
    if (i >= obj.length() || obj.charAt(i) != '{') return null;
    i++;
    while (true) {
      i = jsWs(obj, i);
      if (i >= obj.length()) return null;
      char c = obj.charAt(i);
      if (c == '}') return null;
      if (c == ',') { i++; continue; }
      StringBuilder key = new StringBuilder();
      i = jsString(obj, i, key);
      if (i < 0) return null;
      i = jsWs(obj, i);
      if (i >= obj.length() || obj.charAt(i) != ':') return null;
      i = jsWs(obj, i + 1);
      if (name.equals(key.toString())) {
        if (i < obj.length() && obj.charAt(i) == '"') {
          StringBuilder val = new StringBuilder();
          return (jsString(obj, i, val) < 0) ? null : val.toString();
        }
        return null;                       // 문자열이 아닌 값은 이 화면에서 쓰지 않는다
      }
      i = jsValue(obj, i);
      if (i < 0) return null;
    }
  }

  /** 루트 오브젝트의 name 배열을 '원소 원문 조각' 목록으로 자른다.
   *  원소를 다시 조립하지 않고 원문 그대로 되돌려 주므로 값이 변형될 여지가 없다. */
  static java.util.List<String> jsArray(String json, String name) {
    java.util.List<String> out = new java.util.ArrayList<String>();
    if (json == null) return out;
    int i = jsWs(json, 0);
    if (i >= json.length() || json.charAt(i) != '{') return out;
    i++;
    while (true) {
      i = jsWs(json, i);
      if (i >= json.length()) return out;
      char c = json.charAt(i);
      if (c == '}') return out;
      if (c == ',') { i++; continue; }
      StringBuilder key = new StringBuilder();
      i = jsString(json, i, key);
      if (i < 0) return out;
      i = jsWs(json, i);
      if (i >= json.length() || json.charAt(i) != ':') return out;
      i = jsWs(json, i + 1);
      if (!name.equals(key.toString())) {
        i = jsValue(json, i);
        if (i < 0) return out;
        continue;
      }
      if (i >= json.length() || json.charAt(i) != '[') return out;
      i++;
      while (true) {
        i = jsWs(json, i);
        if (i >= json.length()) return out;
        char d = json.charAt(i);
        if (d == ']') return out;
        if (d == ',') { i++; continue; }
        int e = jsValue(json, i);
        if (e < 0) return out;
        out.add(json.substring(i, e));
        i = e;
      }
    }
  }

  // ── 파일 입출력 ────────────────────────────────────────────────────────
  /** 웹루트의 WEB-INF/topics.json(빌드가 배치). 없으면 null. */
  static String topicsCatalog(javax.servlet.ServletContext ctx) {
    java.io.InputStream in = ctx.getResourceAsStream("/WEB-INF/topics.json");
    if (in == null) return null;
    java.io.Reader rd = null;
    try {
      rd = new java.io.InputStreamReader(in, "UTF-8");
      StringBuilder sb = new StringBuilder(16384);
      char[] cb = new char[8192];
      int n;
      while ((n = rd.read(cb)) != -1) {
        sb.append(cb, 0, n);
        if (sb.length() > TOPICS_MAX_CHARS) break;
      }
      return sb.toString();
    } catch (Exception e) {
      ctx.log("[malgnblog] topics.json 읽기 실패: " + e);
      return null;
    } finally {
      if (rd != null) { try { rd.close(); } catch (Exception ig) { } }
      else { try { in.close(); } catch (Exception ig) { } }
    }
  }

  static java.io.File topicsDeletedFile(javax.servlet.ServletContext ctx) {
    return new java.io.File(dataDir(ctx), "topics-deleted.json");
  }

  /** 삭제된 id 목록. 파일이 없거나 깨졌으면 빈 목록(삭제 기록이 안 읽히면 '전부 보임'이 안전). */
  static java.util.List<String> topicsDeleted(javax.servlet.ServletContext ctx) {
    java.util.List<String> ids = new java.util.ArrayList<String>();
    java.io.File f = topicsDeletedFile(ctx);
    if (!f.isFile()) return ids;
    java.io.Reader r = null;
    try {
      r = new java.io.InputStreamReader(new java.io.FileInputStream(f), "UTF-8");
      StringBuilder sb = new StringBuilder(4096);
      char[] cb = new char[4096];
      int n;
      while ((n = r.read(cb)) != -1) {
        sb.append(cb, 0, n);
        if (sb.length() > TOPICS_MAX_CHARS) break;
      }
      java.util.List<String> raw = jsArray(sb.toString(), "deleted");
      for (int i = 0; i < raw.size(); i++) {
        StringBuilder v = new StringBuilder();
        if (jsString(raw.get(i), 0, v) < 0) continue;
        String id = v.toString();
        if (id.length() > 0 && !ids.contains(id)) ids.add(id);
      }
    } catch (Exception e) {
      ctx.log("[malgnblog] topics-deleted.json 읽기 실패: " + e);
    } finally {
      if (r != null) try { r.close(); } catch (Exception ig) { }
    }
    return ids;
  }

  /** 삭제 기록을 통째로 다시 쓴다(임시파일 → 원자적 교체, stats.tsv 와 같은 방식). */
  static boolean topicsSaveDeleted(javax.servlet.ServletContext ctx, java.util.List<String> ids) {
    java.io.File dst = topicsDeletedFile(ctx);
    java.io.File tmp = null;
    java.io.Writer w = null;
    try {
      java.text.SimpleDateFormat f = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
      f.setTimeZone(java.util.TimeZone.getTimeZone("Asia/Seoul"));   // 전 프로젝트 서울 기준
      StringBuilder b = new StringBuilder(ids.size() * 24 + 128);
      b.append("{\"updated\":\"").append(f.format(new java.util.Date()))
       .append(" KST\",\"count\":").append(ids.size()).append(",\"deleted\":[");
      for (int i = 0; i < ids.size(); i++) {
        if (i > 0) b.append(',');
        b.append('"').append(jsonEscape(ids.get(i))).append('"');
      }
      b.append("]}");

      // 고정 이름을 쓰면 재배포 순간(구/신 웹앱 공존) 같은 tmp 에 동시 write 가 날 수 있다
      tmp = java.io.File.createTempFile("topics", ".tmp", dst.getParentFile());
      w = new java.io.OutputStreamWriter(new java.io.FileOutputStream(tmp), "UTF-8");
      w.write(b.toString());
      w.close(); w = null;

      try {
        java.nio.file.Files.move(tmp.toPath(), dst.toPath(),
            java.nio.file.StandardCopyOption.REPLACE_EXISTING);
        tmp = null;
        return true;
      } catch (Throwable t) {
        if (tmp.renameTo(dst)) { tmp = null; return true; }
        ctx.log("[malgnblog] 삭제 기록 교체 실패(기존 파일 유지): " + t);
        return false;
      }
    } catch (Exception e) {
      ctx.log("[malgnblog] 삭제 기록 쓰기 실패: " + e);
      return false;
    } finally {
      if (w != null) try { w.close(); } catch (Exception ig) { }
      if (tmp != null) tmp.delete();
    }
  }

  /** 감사 로그 1줄. write.jsp 의 audit() 과 같은 파일에 쓰되 이름은 달리한다
   *  (같은 클래스에 두 개가 생기는 일을 원천 차단). 실패해도 요청은 계속된다. */
  static void topicsAudit(javax.servlet.ServletContext ctx, String line) {
    java.io.Writer w = null;
    try {
      java.text.SimpleDateFormat f = new java.text.SimpleDateFormat("yyyy-MM-dd HH:mm:ss");
      f.setTimeZone(java.util.TimeZone.getTimeZone("Asia/Seoul"));
      w = new java.io.OutputStreamWriter(
            new java.io.FileOutputStream(new java.io.File(dataDir(ctx), "admin.log"), true), "UTF-8");
      w.write(f.format(new java.util.Date()) + "\t" + line + "\n");
    } catch (Exception e) {
      ctx.log("[malgnblog] admin.log 기록 실패: " + e);
    } finally {
      if (w != null) try { w.close(); } catch (Exception ig) { }
    }
  }

  /** id 는 길이·제어문자만 본다(한글 id 도 허용 — 카탈로그를 쓰는 쪽을 묶지 않으려고). */
  static boolean topicsValidId(String id) {
    if (id == null || id.length() == 0 || id.length() > TOPICS_MAX_ID) return false;
    for (int i = 0; i < id.length(); i++) if (id.charAt(i) < 0x20) return false;
    return true;
  }
%>
<%
  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Robots-Tag", "noindex, nofollow");

  javax.servlet.ServletContext ctx = application;
  out.clearBuffer();               // 태그 사이 개행이 JSON 앞에 붙지 않게

  // POST 본문(글감 삭제·복구)의 한글 id 가 깨지지 않게. 첫 getParameter 보다 먼저 불러야 한다.
  // GET(대시보드) 동작에는 영향이 없다 — 쿼리스트링 디코딩은 컨테이너 설정이 맡는다.
  try { request.setCharacterEncoding("UTF-8"); } catch (Exception ignore) { }

  if (!pwEquals(request.getParameter("pw"), adminPw(ctx))) {
    response.setStatus(401);
    out.print("{\"error\":\"unauthorized\"}");
    return;
  }

  // ?posts=1 → 글 메타 매니페스트(WEB-INF/posts.json)를 그대로 돌려준다.
  //   서버의 Apache가 /api/ 를 통째로 프록시하지 않고 track/stats/update 만 개별 프록시하는
  //   환경이라, 새 /api/posts 경로는 Apache 404가 난다. 이미 프록시되는 이 /api/stats 에
  //   얹어 새 관리자 콘솔(/gamma2)이 매니페스트를 받도록 한다(같은 인증). posts.jsp 는
  //   Apache가 blanket /api/ 로 갱신되면 쓸 수 있게 남겨둔다.
  //   전체를 읽어 한 번에 출력한다(기본 버퍼 초과·중간 실패에도 안전).
  if (request.getParameter("posts") != null) {
    java.io.InputStream in = ctx.getResourceAsStream("/WEB-INF/posts.json");
    if (in == null) { out.print("{\"count\":0,\"posts\":[]}"); return; }
    java.io.Reader rd = null;
    try {
      rd = new java.io.InputStreamReader(in, "UTF-8");
      StringBuilder sb = new StringBuilder(16384);
      char[] cb = new char[8192];
      int cn;
      while ((cn = rd.read(cb)) != -1) sb.append(cb, 0, cn);
      out.print(sb.toString());
    } catch (Exception ex) {
      ctx.log("[malgnblog] posts.json 읽기 실패: " + ex);
      response.setStatus(503);
      out.print("{\"error\":\"unavailable\"}");
    } finally {
      if (rd != null) { try { rd.close(); } catch (Exception ig) {} }
      else { try { in.close(); } catch (Exception ig) {} }
    }
    return;
  }

  // ── 글감 보드(/new) ────────────────────────────────────────────────────
  //   ?topics=1      목록   (GET)
  //   ?topics=del    삭제   (POST, 본문 id=…)   — 비번도 본문으로 받는다(액세스로그 평문 방지)
  //   ?topics=undel  복구   (POST, 본문 id=…)
  String topicsOp = request.getParameter("topics");
  if (topicsOp != null) {

    if ("del".equals(topicsOp) || "undel".equals(topicsOp)) {
      // 크롤러·링크프리뷰의 GET 으로 글감이 사라지면 안 된다.
      if (!"POST".equals(request.getMethod())) {
        response.setStatus(405);
        response.setHeader("Allow", "POST");
        out.print("{\"error\":\"method_not_allowed\"}");
        return;
      }
      String id = request.getParameter("id");
      if (id != null) id = id.trim();
      if (!topicsValidId(id)) {
        response.setStatus(400);
        out.print("{\"error\":\"bad_request\",\"detail\":\"id 가 비었거나 너무 깁니다\"}");
        return;
      }
      boolean del = "del".equals(topicsOp);
      int  rc      = 200;
      boolean changed = false;
      int  size    = 0;
      // 파일 하나를 통째로 다시 쓰므로 읽기부터 쓰기까지를 한 번에 잠근다.
      // (연타로 여러 건을 지워도 마지막 한 건만 남는 일이 없어야 한다)
      synchronized (topicsLock(ctx)) {
        java.util.List<String> ids = topicsDeleted(ctx);
        if (del) {
          if (ids.contains(id)) changed = false;                 // 같은 id 두 번 → 멱등
          else if (ids.size() >= TOPICS_MAX_DELETED) rc = 400;
          else { ids.add(id); changed = true; }
        } else {
          while (ids.remove(id)) changed = true;                 // 없으면 그냥 no-op → 멱등
        }
        if (rc == 200 && changed && !topicsSaveDeleted(ctx, ids)) rc = 500;
        size = ids.size();
      }
      if (rc == 400) {
        response.setStatus(400);
        out.print("{\"error\":\"too_many\",\"detail\":\"삭제 기록이 상한에 닿았습니다\"}");
        return;
      }
      if (rc == 500) {
        response.setStatus(500);
        out.print("{\"error\":\"save_failed\",\"detail\":\"삭제 기록을 저장하지 못했습니다\"}");
        return;
      }
      topicsAudit(ctx, (del ? "topic-del" : "topic-undel") + "\t" + id
                       + "\t" + (changed ? "changed" : "nochange") + "\tn=" + size);
      out.print("{\"ok\":true,\"id\":\"" + jsonEscape(id) + "\",\"deleted\":" + del
                + ",\"changed\":" + changed + ",\"count\":" + size + "}");
      return;
    }

    // 목록. 카탈로그 원소를 '원문 조각' 그대로 재사용하므로 값이 변형되지 않는다.
    String cat = topicsCatalog(ctx);
    java.util.List<String> gone = topicsDeleted(ctx);
    java.util.List<String> elems = jsArray(cat, "topics");
    StringBuilder alive = new StringBuilder(8192);
    StringBuilder trash = new StringBuilder(2048);
    int nAlive = 0, nTrash = 0;
    java.util.List<String> seen = new java.util.ArrayList<String>();
    for (int i = 0; i < elems.size(); i++) {
      String el = elems.get(i);
      String id = jsField(el, "id");
      if (id == null) id = "";
      if (id.length() > 0) seen.add(id);
      if (id.length() > 0 && gone.contains(id)) {
        if (nTrash++ > 0) trash.append(',');
        trash.append(el);
      } else {
        if (nAlive++ > 0) alive.append(',');
        alive.append(el);
      }
    }
    // 카탈로그에서 아예 사라진 id 의 삭제 기록. 화면에서 되살릴 길이 없어지므로 따로 알린다.
    StringBuilder orphan = new StringBuilder(256);
    int nOrphan = 0;
    for (int i = 0; i < gone.size(); i++) {
      if (seen.contains(gone.get(i))) continue;
      if (nOrphan++ > 0) orphan.append(',');
      orphan.append('"').append(jsonEscape(gone.get(i))).append('"');
    }

    StringBuilder b = new StringBuilder(alive.length() + trash.length() + 512);
    b.append("{\"ok\":true,\"catalog\":").append(cat == null ? "false" : "true")
     .append(",\"generated\":\"").append(jsonEscape(cat == null ? "" : jsField(cat, "generated")))
     .append("\",\"count\":").append(nAlive)
     .append(",\"trashCount\":").append(nTrash)
     .append(",\"topics\":[").append(alive)
     .append("],\"trash\":[").append(trash)
     .append("],\"orphan\":[").append(orphan)
     .append("],\"date\":\"").append(todayKST()).append("\"}");
    out.print(b.toString());
    return;
  }

  java.util.Map<String, Long> m = store(ctx);
  String kst = todayKST();

  if ("1".equals(request.getParameter("reset"))) {
    synchronized (m) { m.clear(); save(ctx, m); }
    out.print("{\"reset\":true}");
    return;
  }

  java.util.List<String[]> days  = new java.util.ArrayList<String[]>();
  java.util.List<String[]> posts = new java.util.ArrayList<String[]>();
  synchronized (m) {
    for (java.util.Map.Entry<String, Long> e : m.entrySet()) {
      String k = e.getKey();
      String v = String.valueOf(e.getValue());
      if (k.startsWith("T:"))      days.add(new String[]{ k.substring(2), v });
      else if (k.startsWith("P:")) posts.add(new String[]{ k.substring(2), v });
    }
  }

  java.util.Collections.sort(days, new java.util.Comparator<String[]>() {
    public int compare(String[] a, String[] b) { return a[0].compareTo(b[0]); }   // 날짜 오름차순
  });
  java.util.Collections.sort(posts, new java.util.Comparator<String[]>() {
    public int compare(String[] a, String[] b) {                                  // 조회수 내림차순
      return Long.valueOf(b[1]).compareTo(Long.valueOf(a[1]));
    }
  });

  long total = 0L;
  for (String[] p : posts) total += Long.parseLong(p[1]);
  String today = "0";
  for (String[] d : days) if (d[0].equals(kst)) today = d[1];

  StringBuilder b = new StringBuilder(1024);
  b.append("{\"today\":").append(today).append(",\"total\":").append(total).append(",\"days\":[");
  for (int i = 0; i < days.size(); i++) {
    if (i > 0) b.append(',');
    b.append("{\"date\":\"").append(jsonEscape(days.get(i)[0])).append("\",\"count\":").append(days.get(i)[1]).append('}');
  }
  b.append("],\"posts\":[");
  for (int i = 0; i < posts.size(); i++) {
    if (i > 0) b.append(',');
    b.append("{\"path\":\"").append(jsonEscape(posts.get(i)[0])).append("\",\"count\":").append(posts.get(i)[1]).append('}');
  }
  b.append("],\"date\":\"").append(kst).append("\"}");
  out.print(b.toString());
%>
