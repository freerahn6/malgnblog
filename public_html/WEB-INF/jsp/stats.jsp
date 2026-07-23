<%@ page contentType="application/json; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  GET /api/stats?pw=...        — 관리자 대시보드(/gamma/)가 읽는 집계 JSON
  GET /api/stats?pw=...&reset=1 — 집계 초기화

  응답 형태는 기존 Netlify 함수와 동일하다(대시보드 코드를 고치지 않기 위해).
    { today, total, days:[{date,count}], posts:[{path,count}], date }

  adminPw()·pwEquals()는 stats-store.jspf(공용)에 있다.
--%>
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
