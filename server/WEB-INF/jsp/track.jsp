<%@ page contentType="text/plain; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  POST /api/track?p=/lms/some-slug/   — 조회수 +1, 본문 없이 204.
  모든 페이지 하단 스크립트가 호출한다. 실패해도 페이지 동작에는 영향이 없다.
--%>
<%!
  static final int MAX_KEYS = 5000;   // 잘못된 경로가 쏟아져도 파일이 무한히 커지지 않게

  static void bump(java.util.Map<String, Long> m, String key) {
    Long cur = m.get(key);
    m.put(key, Long.valueOf((cur == null ? 0L : cur.longValue()) + 1L));
  }

  // 사이트가 실제로 만드는 경로 모양만 통과시킨다. 여기서 걸러야 집계가 쓰레기로 안 찬다.
  static boolean validPath(String p) {
    if (p == null || p.length() == 0 || p.length() > 200) return false;
    if (p.charAt(0) != '/') return false;
    for (int i = 0; i < p.length(); i++) {
      char c = p.charAt(i);
      boolean ok = (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z') || (c >= '0' && c <= '9')
                || c == '/' || c == '-' || c == '_' || c == '.';
      if (!ok) return false;
    }
    return p.indexOf("..") < 0;
  }
%>
<%
  // 204에는 본문이 없어야 한다. 태그 사이 개행이 버퍼에 남으므로 먼저 비운다.
  // (여기서 비워두면 아래에 실수로 출력이 끼어들어도 커밋 전이라 안전하다)
  out.clearBuffer();
  response.setHeader("Cache-Control", "no-store");
  response.setStatus(204);

  javax.servlet.ServletContext ctx = application;

  // 크롤러·링크 프리뷰 봇이 GET으로 긁어 카운트를 부풀리는 것을 막는다.
  // 페이지 스크립트는 항상 POST로 호출한다.
  if (!"POST".equals(request.getMethod())) return;

  String p = request.getParameter("p");
  if (p == null) p = "/";

  if (!validPath(p)) {
    // 슬러그는 전부 ASCII라는 전제다. 한글 슬러그가 생기면 여기서 조용히 버려지므로 로그를 남긴다.
    ctx.log("[malgnblog] track: 집계 제외 경로 " + p.length() + "자");
    return;
  }
  // /admin은 관리자 본인 조회라 집계하지 않는다(Netlify 구현과 동일)
  if (p.startsWith("/admin")) return;

  java.util.Map<String, Long> m = store(ctx);
  synchronized (m) {
    String dayKey = "T:" + todayKST();
    String pageKey = "P:" + p;
    // 상한은 페이지 키에만 건다. 일자 키(연 365개)까지 막으면 일별 통계가 조용히 얼어붙는다.
    boolean pageAllowed = m.containsKey(pageKey) || m.size() < MAX_KEYS;
    bump(m, dayKey);
    if (pageAllowed) bump(m, pageKey);
    save(ctx, m);
  }
%>