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
  // 첫 getParameter() 가 본문 파싱을 확정시키므로 인코딩은 그 전에 잡아야 한다.
  // (아래 ?write= 분기가 write.jsp 로 forward 하는데, 거기서 setCharacterEncoding 을
  //  해봐야 이미 늦다 — 한글 원고가 깨진 채로 커밋된다)
  try { request.setCharacterEncoding("UTF-8"); } catch (Exception ignore) { }

  response.setHeader("Cache-Control", "no-store");
  response.setHeader("X-Robots-Tag", "noindex, nofollow");

  javax.servlet.ServletContext ctx = application;
  out.clearBuffer();               // 태그 사이 개행이 JSON 앞에 붙지 않게

  // ?write=1 → 글 쓰기 API(write.jsp)로 넘긴다.
  //   posts=1 과 같은 이유의 우회다 — 서버 Apache 가 /api/ 를 통째로 프록시하지 않고
  //   track/stats/update 만 개별 프록시해서, 새 /api/posts/write 경로는 Apache 404 가 난다.
  //   이미 프록시되는 이 경로에 얹는다. 인증·POST 검사는 write.jsp 가 직접 하므로
  //   여기서는 아무것도 검사하지 않고 그대로 넘긴다(비번은 POST 본문에 있다).
  //   Apache 가 blanket /api/ 로 갱신되면 /api/posts/write 정식 경로를 쓰면 된다.
  if (request.getParameter("write") != null) {
    request.getRequestDispatcher("/WEB-INF/jsp/write.jsp").forward(request, response);
    return;
  }

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
