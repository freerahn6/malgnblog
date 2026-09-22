# -*- coding: utf-8 -*-
"""
고용노동통계(laborstat.moel.go.kr) OLAP 통계표 직접다운로드 스크립트.
로그인 불필요. KOSIS statHtml 계열의 directDown 경로(makeLarge -> downLarge)를 그대로 호출한다.

사용:  python fetch-laborstat.py DT_118N_ENTN041 118_162_001
출력:  ./<tblId>.csv  (원본 EUC-KR 그대로 저장)  +  <tblId>.utf8.csv (UTF-8-SIG 변환본)

재개: 대상 CSV가 이미 있고 0바이트가 아니면 건너뛴다(덮어쓰기 안 함).
"""
import sys, os, re, json, time, random
import urllib.request, urllib.parse, http.cookiejar

BASE = "https://laborstat.moel.go.kr"
OUT  = os.path.dirname(os.path.abspath(__file__))

cj = http.cookiejar.CookieJar()
op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))

def post(path, pairs, tries=4):
    body = urllib.parse.urlencode(pairs, doseq=True).encode()
    for i in range(tries):
        try:
            req = urllib.request.Request(BASE + path, data=body,
                  headers={'Content-Type': 'application/x-www-form-urlencoded',
                           'Referer': BASE + '/'})
            r = op.open(req, timeout=300)
            return r, r.read()
        except urllib.error.HTTPError as e:
            if e.code in (429, 500, 502, 503, 504) and i < tries - 1:
                time.sleep((2 ** i) + random.random()); continue
            raise
        except Exception:
            if i < tries - 1:
                time.sleep((2 ** i) + random.random()); continue
            raise

def fetch(tbl_id, list_id, prd_se='Y', filetype='csv'):
    dst = os.path.join(OUT, tbl_id + '.csv')
    if os.path.exists(dst) and os.path.getsize(dst) > 0:
        print('[skip] already downloaded:', dst); return dst

    # 1) 다운로드 팝업 HTML -> 폼 파라미터(DIM_CO, prdDeCnt, dbUser) 획득
    _, h = post('/directDownDiv.do',
                [('orgId', '118'), ('tblId', tbl_id), ('vwCd', 'MT_LTITLE'), ('listId', list_id)])
    html = h.decode('utf-8', 'replace')
    def val(name, default=''):
        m = re.search(r'name="%s"[^>]*value="([^"]*)"' % name, html) or \
            re.search(r'value="([^"]*)"[^>]*name="%s"' % name, html)
        return m.group(1) if m else default
    dim_co    = val('DIM_CO', '9130')
    prd_cnt   = val('prdDeCnt', '21')
    db_user   = val('dbUser', 'NSI_IN_118.')

    # 2) 제공 시점 목록
    _, p = post('/directDownPrdDe.do',
                [('orgId', '118'), ('tblId', tbl_id), ('prdSe', prd_se),
                 ('pub', ''), ('dbUser', db_user), ('st', '')])
    prds = sorted(set(re.findall(r'name="PRD_DE"[^>]*value="(\d{4})"', p.decode('utf-8', 'replace'))
                      or re.findall(r'value="(\d{4})"', p.decode('utf-8', 'replace'))))
    if not prds:
        raise SystemExit('시점 목록을 찾지 못함: ' + tbl_id)
    print('[%s] 시점 %d개: %s ~ %s' % (tbl_id, len(prds), prds[0], prds[-1]))

    pairs = [('orgId', '118'), ('tblId', tbl_id), ('prdDe', ','.join(prds) + ','),
             ('prdNm', ''), ('prdDeCnt', prd_cnt), ('DIM_CO', dim_co),
             ('mode', 'directMake'), ('VWCD', 'MT_LTITLE'), ('direct', 'direct'),
             ('dbUser', db_user), ('pub', ''), ('st', ''),
             ('downLargeFileType', filetype), ('downLargeExprType', '1'),
             ('downLargeSort', 'asc'), ('prdSe', prd_se)] + [('PRD_DE', x) for x in prds]

    # 3) 서버측 파일 생성 -> 4) 내려받기
    _, b = post('/makeLarge.do', pairs)
    f = json.loads(b.decode('utf-8'))['file']
    time.sleep(1.0)
    _, data = post('/downLarge.do?file=' + urllib.parse.quote(f), pairs)
    with open(dst, 'wb') as fp:
        fp.write(data)
    txt = data.decode('euc-kr', 'replace')
    with open(os.path.join(OUT, tbl_id + '.utf8.csv'), 'w', encoding='utf-8-sig', newline='') as fp:
        fp.write(txt)
    print('[ok] %s  %d bytes  %d rows' % (dst, len(data), txt.count('\n')))
    return dst

if __name__ == '__main__':
    targets = [('DT_118N_ENTN041', '118_162_001'),   # 노동비용 2019~   (10인이상 회사법인, 10차 산업분류)
               ('DT_118N_ENTN031', '118_179'),       # 노동비용 2008~2018 (10인이상 회사법인, 9차 산업분류)
               ('DT_ENTN021',      '118_471'),       # 노동비용 2004~2007
               ('DT_ENTN011',      '118_472'),       # 노동비용 1998~2003
               ('DT_ENTN001',      '118_473')]       # 노동비용 1994~1997
    if len(sys.argv) >= 3:
        targets = [(sys.argv[1], sys.argv[2])]
    for t, l in targets:
        try:
            fetch(t, l)
        except Exception as e:
            print('[fail]', t, repr(e))
        time.sleep(2)
