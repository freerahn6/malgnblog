<%@ page contentType="application/json; charset=UTF-8" session="false" trimDirectiveWhitespaces="true" buffer="64kb" %>
<%@ include file="/WEB-INF/jsp/stats-store.jspf" %>
<%--
  GET /api/posts?pw=...  — 새 관리자 콘솔(/gamma2/)이 읽는 글 메타 매니페스트.

  빌드 때 build.py 가 /WEB-INF/posts.json 을 생성해 웹앱 안에 넣는다(발행글 + 비게시글 메타).
  WEB-INF 아래라 브라우저가 직접 URL로 못 읽는다 → 여기서 비밀번호를 확인한 뒤에만 스트리밍한다.
  이 규칙이 draft(비게시) 글의 제목·존재를 미인증 노출로부터 막는 유일한 관문이다.

  응답:
    200 { "generated":..., "count":N, "posts":[ {path,title,category,author,date,updated,funnel,slug,draft}, ... ] }
    401 { "error":"unauthorized" }             — 비밀번호 불일치
    200 { "count":0, "posts":[] }              — 매니페스트가 아직 없을 때(빈 목록으로 안전 처리)

  adminPw()·pwEquals() 는 stats-store.jspf(공용)에 있다. stats.jsp 와 같은 include·같은 인증.
  path 는 /api/stats 의 posts[].path 와 같은 형식("/{cat}/{slug}/")이라 클라이언트가 path로 조인한다.
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

  java.io.InputStream in = ctx.getResourceAsStream("/WEB-INF/posts.json");
  if (in == null) {
    // 매니페스트가 아직 배포되지 않았어도 콘솔이 깨지지 않도록 빈 목록을 200으로 준다.
    out.print("{\"count\":0,\"posts\":[]}");
    return;
  }

  java.io.Reader r = null;
  try {
    r = new java.io.InputStreamReader(in, "UTF-8");
    char[] buf = new char[8192];
    int n;
    while ((n = r.read(buf)) != -1) {
      out.write(buf, 0, n);
    }
  } catch (Exception e) {
    ctx.log("[malgnblog] posts.json 읽기 실패: " + e);
    // 버퍼(64kb)를 아직 안 넘겼으면 지우고 503으로 대체한다.
    try { out.clearBuffer(); } catch (Exception ignore) { }
    response.setStatus(503);
    out.print("{\"error\":\"unavailable\"}");
  } finally {
    if (r != null) try { r.close(); } catch (Exception ignore) { }
    else try { in.close(); } catch (Exception ignore) { }
  }
%>
