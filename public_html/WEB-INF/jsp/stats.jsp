<%@ page contentType="application/json; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  GET /api/stats?pw=...        — 관리자 대시보드(/gamma/)가 읽는 집계 JSON
  GET /api/stats?pw=...&reset=1 — 집계 초기화

  응답 형태는 기존 Netlify 함수와 동일하다(대시보드 코드를 고치지 않기 위해).
    { today, total, days:[{date,count}], posts:[{path,count}], date }
--%>
<%!
  static String adminPw(javax.servlet.ServletContext ctx) {
    // 파일이 있으면 그쪽이 우선 — 비밀번호를 바꾸려고 배포할 필요가 없게
    java.io.File f = new java.io.File(dataDir(ctx), "admin.pw");
    if (f.isFile()) {
      java.io.BufferedReader r = null;
      try {
        r = new java.io.BufferedReader(new java.io.InputStreamReader(
              new java.io.FileInputStream(f), "UTF-8"));
        String line = r.readLine();
        if (line != null && line.trim().length() > 0) return line.trim();
      } catch (Exception ignore) {
      } finally { if (r != null) try { r.close(); } catch (Exception ignore) { } }
    }
    String p = ctx.getInitParameter("adminPassword");
    return (p == null || p.length() == 0) ? "gamma" : p;
  }

  // 타이밍 노출을 줄이려고 길이·내용을 한 번에 비교하지 않는다
  static boolean pwEquals(String a, String b) {
    if (a == null || b == null) return false;
    if (a.length() != b.length()) return false;
    int diff = 0;
    for (int i = 0; i < a.length(); i++) diff |= a.charAt(i) ^ b.charAt(i);
    return diff == 0;
  }
%>
<%
  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Robots-Tag", "noindex, nofollow");

  javax.servlet.ServletContext ctx = application;
  out.clearBuffer();               // 태그 사이 개행이 JSON 앞에 붙지 않게

  if (!pwEquals(request.getParameter("pw"), adminPw(ctx))) {
    response.setStatus(401);
    out.print("{\"error\":\"unauthorized\"}");
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
