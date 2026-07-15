# -*- coding: utf-8 -*-
import re, os, json, markdown, html as H
BASE=os.path.dirname(os.path.abspath(__file__)); ART=BASE+"/articles"; PREV=BASE+"/_preview"; OUT=BASE+"/_deploy/public"; _D=BASE+"/_deploy"
SITE="https://blog.malgnsoft.com"
TRACK='<script>(function(){var p=location.pathname;if(p.indexOf("/admin")===0)return;try{fetch("/api/track?p="+encodeURIComponent(p),{method:"POST",keepalive:true})}catch(e){}})();</script>'

art_html=open(f"{PREV}/article.html",encoding='utf-8').read()
idx_html=open(f"{PREV}/index.html",encoding='utf-8').read()
ACSS=re.search(r'<style>(.*?)</style>',art_html,re.S).group(1)
HCSS=re.search(r'<style>(.*?)</style>',idx_html,re.S).group(1)
LOGO=re.search(r'src="(data:image/png;base64,[^"]+)"\s*alt="맑은소프트"',art_html).group(1)
MSYM=re.search(r'<button class="fab"[^>]*><img src="(data:image/png;base64,[^"]+)"',art_html).group(1)
FAB=re.search(r'<div class="fab-wrap">.*?</button>\s*</div>',art_html,re.S).group(0)
FAB=FAB.replace('/cloud/inquiry.jsp"','/cloud/inquiry.jsp#stickyMenu"')
INQ="https://www.malgnsoft.com/cloud/inquiry.jsp#stickyMenu"
SCRIPT=re.findall(r'<script>.*?</script>',art_html,re.S)[-1]
COVERS=re.findall(r'class="cover-img"[^>]*src="(data:image/jpeg;base64,[^"]+)"',idx_html)
IMG=json.load(open(_D+'/img_map.json',encoding='utf-8'))
NAMECARDS=json.load(open(_D+'/namecards.json',encoding='utf-8'))
FIGMAP=json.load(open(_D+'/figmap.json',encoding='utf-8'))
BANL=open(_D+'/wecandeo_datauri.txt',encoding='utf-8').read().strip()
BANR=open(_D+'/malgnsoft_datauri.txt',encoding='utf-8').read().strip()
BAN_LEFT=f'<a class="side-banner" href="https://www.wecandeo.com" target="_blank" rel="noopener"><img src="{BANL}" alt="위캔디오 - 동영상 클라우드 플랫폼"></a>'
BAN_RIGHT=f'<aside class="rail"><a href="https://www.malgnsoft.com" target="_blank" rel="noopener"><img src="{BANR}" alt="맑은소프트"></a></aside>'
EXTRA_CSS=('.wrap{max-width:1320px}'
 '.article-shell{grid-template-columns:176px minmax(0,1fr) 176px;gap:44px}'
 '.doc{min-width:0;overflow:hidden}'
 '.doc figure img,.doc article img{max-width:100%!important;height:auto;display:block;border:1px solid var(--border);border-radius:12px}'
 '.doc figure{max-width:100%}'
 '.rail-left{position:sticky;top:88px;align-self:start}'
 '.rail-left .side-banner{display:block;width:160px;margin:0 auto;border-radius:12px;overflow:hidden;line-height:0;box-shadow:var(--shadow);transition:transform .18s}'
 '.rail-left .side-banner:hover{transform:translateY(-3px)}'
 '.rail-left .side-banner img{width:100%;height:auto;display:block}'
 'aside.rail{position:sticky;top:88px;align-self:start;max-height:calc(100vh - 104px);overflow-y:auto;overflow-x:hidden;scrollbar-width:thin}'
 'aside.rail a{display:block;width:160px;margin:0 auto;border-radius:12px;overflow:hidden;line-height:0;box-shadow:var(--shadow);transition:transform .18s}'
 'aside.rail a:hover,aside.toc .side-banner:hover{transform:translateY(-3px)}'
 'aside.rail img{width:100%;height:auto;display:block}'
 '.byline .brole{color:var(--accent);font-weight:600;margin-left:6px;font-size:13px}'
 '.namecard{margin:72px 0 48px;display:flex;justify-content:center}'
 '.nc-img{width:100%;max-width:580px;height:auto;border-radius:14px;display:block;box-shadow:var(--shadow)}'
 '.recentlist{margin:28px 0 8px}'
 '.recentlist h2{font-size:18px;font-weight:800;letter-spacing:-0.02em;margin:0 0 8px;padding-bottom:11px;border-bottom:2px solid var(--border-strong)}'
 '.recentlist ul{list-style:none;margin:0;padding:0}'
 '.recentlist li{border-bottom:1px solid var(--border)}'
 '.recentlist a{display:flex;align-items:center;gap:13px;padding:13px 4px;color:var(--text);text-decoration:none}'
 '.recentlist a:hover .rl-title{color:var(--accent)}'
 '.recentlist .rl-cat{flex:none;font-size:11px;font-weight:700;color:var(--accent);background:var(--accent-soft);padding:4px 10px;border-radius:999px;min-width:82px;text-align:center}'
 '.recentlist .rl-title{flex:1;min-width:0;font-size:15px;font-weight:600;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}'
 '.recentlist .rl-date{flex:none;font-size:12.5px;color:var(--faint);font-variant-numeric:tabular-nums}'
 '@media (max-width:560px){.recentlist .rl-cat{display:none}.recentlist .rl-title{white-space:normal}}'
 '@media (max-width:1000px){.article-shell{grid-template-columns:1fr}aside.rail,.rail-left{display:none}}')

CATL={'lms':'LMS·이러닝','hrd':'기업교육·HRD','certification':'자격검정','video':'동영상·콘텐츠','edutech':'에듀테크·AI','news':'맑은소프트 소식'}
AUTHORS={'안기범':('팀장','TEAM LEAD','AN GI-BEOM','👨‍💼'),'강이슬':('과장','MANAGER','KANG I-SEUL','👩‍💼'),'이채영':('대리','ASSISTANT MANAGER','LEE CHAE-YEONG','👩‍💻'),'한다현':('대리','ASSISTANT MANAGER','HAN DA-HYEON','👩‍🏫')}
def author_of(a):
    n=a.get('author','교육운영 노트'); r,re_,en,em=AUTHORS.get(n,('','','','✍️')); return n,r,re_,en,em
COVER={'lms-selection-guide-for-corporate-training':0,'what-is-lms':1,'refund-training-lms-operation-guide':2,
 'legal-mandatory-training-online':3,'self-hosted-vs-cloud-lms':4,'certification-system-build-guide':5,
 'what-is-microlearning':6,'why-own-video-platform':7,'lms-case-studies-3':8,'online-exam-anti-cheating-setup':9,
 'lms-vs-lxp':6,'certificate-auto-issue':2}

def parse(fp):
    raw=open(fp,encoding='utf-8').read()
    m=re.match(r'^---\s*\n(.*?)\n---\s*\n(.*)$',raw,re.S)
    fm,body=m.group(1),m.group(2)
    d={}
    for line in fm.split('\n'):
        mm=re.match(r'^([a-zA-Z_]+):\s*(.*)$',line)
        if mm and mm.group(1) in ('title','description','category','slug','funnel','date','author'):
            v=mm.group(2).strip().strip('"').strip("'")
            d[mm.group(1)]=v
    # faq 블록 파싱 (q/a 쌍)
    faq=[]
    fmatch=re.search(r'(?ms)^faq:\s*\n(.*?)(?=^[a-zA-Z_]+:|\Z)', fm)
    if fmatch:
        for qm in re.finditer(r'-\s*q:\s*(.+?)\n\s*a:\s*(.+?)(?=\n\s*-\s*q:|\Z)', fmatch.group(1), re.S):
            q=qm.group(1).strip().strip('"').strip("'")
            ans=re.sub(r'\s+',' ',qm.group(2).strip().strip('"').strip("'"))
            faq.append((q,ans))
    d['faq']=faq
    # strip a leading H1 if any, and trailing FAQ header duplication left as-is
    body=re.sub(r'^\s*#\s+.*\n','',body,count=1)
    d['body']=body.strip()
    return d

arts=[]
for fn in os.listdir(ART):
    if fn.endswith('.md'):
        d=parse(f"{ART}/{fn}"); d['file']=fn; arts.append(d)
# order by date
arts.sort(key=lambda a:a.get('date',''))
bysl={a['slug']:a for a in arts}

def _collapse_blanks(m): return re.sub(r'\n[ \t]*\n+','\n',m.group(0))
def prep_html_blocks(body):
    # SVG/figure/table 등 원시 HTML 블록 안의 빈 줄 제거 → 마크다운이 블록을 쪼개 escape하는 것 방지
    for tag in ('figure','svg','table'):
        body=re.sub(rf'<{tag}\b.*?</{tag}>', _collapse_blanks, body, flags=re.S)
    return body
def md2html(body):
    h=markdown.markdown(prep_html_blocks(body),extensions=['fenced_code','sane_lists','attr_list','md_in_html'])
    # add ids to h2 + collect toc
    toc=[]; i=[0]
    def repl(m):
        i[0]+=1; sid=f"s-{i[0]}"; txt=re.sub(r'<[^>]+>','',m.group(1)).strip()
        toc.append((sid,txt)); return f'<h2 id="{sid}">{m.group(1)}</h2>'
    h=re.sub(r'<h2>(.*?)</h2>',repl,h,flags=re.S)
    return h,toc

def read_min(body):
    t=len(re.sub(r'\s','',re.sub(r'<[^>]+>','',body)))
    return max(3,round(t/500))

PUBLISHER={"@type":"Organization","name":"맑은소프트","url":"https://www.malgnsoft.com","logo":{"@type":"ImageObject","url":"https://www.malgnsoft.com/img/logo.png"},"sameAs":["https://www.malgnsoft.com","https://blog.naver.com/malgnlms"]}
def jsonld(a,url):
    blocks=[{"@context":"https://schema.org","@type":"Article","headline":a['title'],"description":a.get('description',''),
      "datePublished":a.get('date',''),"dateModified":a.get('date',''),"inLanguage":"ko-KR",
      "author":{"@type":"Person","name":a.get('author','교육운영 노트')},"publisher":PUBLISHER,
      "image":"https://www.malgnsoft.com/img/og_logo.gif","mainEntityOfPage":{"@type":"WebPage","@id":url}},
     {"@context":"https://schema.org","@type":"BreadcrumbList","itemListElement":[
      {"@type":"ListItem","position":1,"name":"홈","item":SITE+"/"},
      {"@type":"ListItem","position":2,"name":CATL[a['category']],"item":f"{SITE}/{a['category']}/"},
      {"@type":"ListItem","position":3,"name":a['title'],"item":url}]}]
    if a.get('faq'):
        blocks.append({"@context":"https://schema.org","@type":"FAQPage","mainEntity":[
          {"@type":"Question","name":q,"acceptedAnswer":{"@type":"Answer","text":ans}} for q,ans in a['faq']]})
    return ''.join(f'<script type="application/ld+json">{json.dumps(b,ensure_ascii=False)}</script>' for b in blocks)

PAGE='''<!doctype html><html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title} — 맑은소프트 블로그</title><meta name="description" content="{desc}">
<link rel="canonical" href="https://blog.malgnsoft.com/{cat}/{slug}/">
<link rel="alternate" type="application/rss+xml" title="맑은소프트 블로그 RSS" href="https://blog.malgnsoft.com/rss.xml">
<meta property="og:type" content="article"><meta property="og:title" content="{title}"><meta property="og:description" content="{desc}"><meta property="og:url" content="https://blog.malgnsoft.com/{cat}/{slug}/"><meta property="og:site_name" content="맑은소프트 블로그"><meta property="og:image" content="https://www.malgnsoft.com/img/og_logo.gif"><meta property="article:published_time" content="{date}"><meta name="twitter:card" content="summary_large_image">
{jsonld}
<style>{css}{extra}</style></head><body>
<div class="progress" id="progress"></div>
<header class="site"><div class="wrap">
<a class="brand" href="/"><span class="plate"><img src="{logo}" alt="맑은소프트"></span></a>
<nav class="main"><a href="/">전체</a><a href="/lms/">LMS·이러닝</a><a href="/hrd/">기업교육·HRD</a><a href="/certification/">자격검정</a><a href="/video/">동영상·콘텐츠</a><a href="/edutech/">에듀테크</a></nav>
<a href="https://www.malgnsoft.com/cloud/inquiry.jsp#stickyMenu" target="_blank" rel="noopener" class="cta-btn">도입 문의</a>
</div></header>
<div class="wrap article-shell">
<aside class="rail-left">{banl}</aside>
<main class="doc">
<nav class="breadcrumb"><a href="/">홈</a><span class="sep">›</span><a href="/{cat}/">{catlabel}</a><span class="sep">›</span><span>{title}</span></nav>
<span class="cat-chip">{catlabel}</span>
<h1 class="title">{title}</h1>
<p class="dek">{desc}</p>
<div class="byline"><span class="avatar">{ainit}</span><span class="who">{aname}<span class="brole">{arole}</span></span><span class="m"><span class="dot"></span><span class="num">{date}</span><span class="dot"></span><span>읽는 시간 {rt}분</span></span></div>
<div class="hero-img"><img src="{hero}" alt="{title}"></div>
<article>{body}</article>
{namecard}
{recentlist}
</main>{banr}</div>
<footer class="site"><div class="wrap"><span class="plate"><img src="{logo}" alt="맑은소프트"></span><span>맑은소프트 블로그 · (주)맑은소프트</span><span style="margin-left:auto">© 맑은소프트</span></div></footer>
{fab}
{script}
{track}
</body></html>'''

for a in arts:
    body_html,toc=md2html(a['body'])
    body_html=body_html.replace('href="/contact/"',f'href="{INQ}" target="_blank" rel="noopener"')
    if a['slug'] in FIGMAP:
        body_html=re.sub(r'(<img[^>]*\ssrc=")(?:\./images/[^"]+|/assets/img/[^"]+)("[^>]*>)',
                         lambda m:m.group(1)+FIGMAP[a['slug']]+m.group(2), body_html, count=1)
    _ti=[]
    for k,(sid,txt) in enumerate(toc):
        cls=' class="on"' if k==0 else ''
        _ti.append(f'<li><a href="#{sid}"{cls}>{H.escape(txt)}</a></li>')
    toc_html=''.join(_ti)
    hero=IMG.get(a['slug'],COVERS[1])
    aname,arole,aroleEn,aen,aemoji=author_of(a)
    _badge=NAMECARDS.get(aname)
    namecard=(f'<div class="namecard"><img class="nc-img" loading="lazy" src="{_badge}" alt="{H.escape(aname)} {arole} - 맑은소프트 블로그 전담팀"></div>') if _badge else ''
    _recent=[x for x in sorted(arts,key=lambda y:y.get('date',''),reverse=True) if x['slug']!=a['slug']][:10]
    _ritems=''.join(f'<li><a href="/{x["category"]}/{x["slug"]}/"><span class="rl-cat">{CATL[x["category"]]}</span><span class="rl-title">{H.escape(x["title"])}</span><span class="rl-date">{x.get("date","").replace("-",".")}</span></a></li>' for x in _recent)
    recentlist=f'<section class="recentlist"><h2>최신 글</h2><ul>{_ritems}</ul></section>'
    _url=f"{SITE}/{a['category']}/{a['slug']}/"
    page=PAGE.format(title=H.escape(a['title']),desc=H.escape(a.get('description','')),cat=a['category'],slug=a['slug'],
        catlabel=CATL.get(a['category'],a['category']),css=ACSS,logo=LOGO,toc=toc_html,date=a.get('date',''),
        rt=read_min(a['body']),hero=hero,body=body_html,fab=FAB,script=SCRIPT,extra=EXTRA_CSS,banl=BAN_LEFT,banr=BAN_RIGHT,
        aname=H.escape(aname),arole=arole,ainit=aemoji,namecard=namecard,recentlist=recentlist,jsonld=jsonld(a,_url),track=TRACK)
    d=f"{OUT}/{a['category']}/{a['slug']}"; os.makedirs(d,exist_ok=True)
    open(f"{d}/index.html",'w',encoding='utf-8').write(page)
    print("page:",a['category'],a['slug'],len(page)//1024,"KB toc",len(toc))

# ---- HOME ----
head=idx_html[:idx_html.find('<article class="featured">')]
tail=idx_html[idx_html.find('</main>'):]
# fix head: remove preview banner, home links
head=re.sub(r'<div class="banner">.*?</div>\s*','',head,count=1,flags=re.S)
head=head.replace('<a class="brand" href="#">','<a class="brand" href="/">',1)
head=head.replace('<a href="#" class="active">전체</a>','<a href="/" class="active">전체</a>',1)
head=head.replace('<a href="#" class="cta-btn">도입 문의</a>','<a href="https://www.malgnsoft.com/cloud/inquiry.jsp#stickyMenu" target="_blank" rel="noopener" class="cta-btn">도입 문의</a>',1)
head=head.replace('<title>교육운영 노트 by 맑은소프트 — 블로그 디자인 시안</title>','<title>맑은소프트 블로그 — 교육을 운영하는 사람을 위한 LMS 실전 지식</title>',1)
HOME_EXTRA=('.wrap{max-width:1320px}'
 '.filters{position:static}'
 '.filters .wrap{justify-content:center}'
 '.card,.featured{position:relative}'
 '.card h3 a.clink,.featured h2 a.clink{color:inherit;text-decoration:none}'
 '.card:hover h3 a.clink,.featured:hover h2 a.clink{color:var(--accent)}'
 'a.clink::after{content:"";position:absolute;inset:0;z-index:2}'
 '.home-shell{display:grid;grid-template-columns:176px minmax(0,1fr) 176px;gap:40px;align-items:start}'
 '.home-main{min-width:0}'
 '.home-shell .grid{grid-template-columns:repeat(3,1fr)}'
 '.rail-left,.home-shell .rail{position:sticky;top:88px;align-self:start;max-height:calc(100vh - 104px);overflow-y:auto;overflow-x:hidden;scrollbar-width:thin}'
 '.rail-left .side-banner,.home-shell .rail a{display:block;width:160px;margin:0 auto;border-radius:12px;overflow:hidden;line-height:0;box-shadow:var(--shadow);transition:transform .18s}'
 '.rail-left .side-banner:hover,.home-shell .rail a:hover{transform:translateY(-3px)}'
 '.rail-left .side-banner img,.home-shell .rail img{width:100%;height:auto;display:block}'
 '@media (max-width:1000px){.home-shell{grid-template-columns:1fr}.rail-left,.home-shell .rail{display:none}}'
 '@media (max-width:900px){.home-shell .grid{grid-template-columns:repeat(2,1fr)}}'
 '@media (max-width:560px){.home-shell .grid{grid-template-columns:1fr}}')
head=head.replace('<main class="wrap">','<div class="wrap home-shell"><aside class="rail-left">'+BAN_LEFT+'</aside><main class="home-main">',1)
tail=tail.replace('</main>','</main>'+BAN_RIGHT+'</div>',1)
def excerpt(s,n=88):
    s=s.strip(); return s if len(s)<=n else s[:n].rsplit(' ',1)[0]+'…'
feat=sorted(arts,key=lambda x:x.get('date',''),reverse=True)[0]  # 최신글 자동 헤드라인
def card_cover(a,extra=''):
    return (f'<div class="cover"><img class="cover-img" loading="lazy" '
            f'src="{IMG.get(a["slug"],COVERS[1])}" alt="{H.escape(a["title"])}"><span class="scrim"></span>'
            f'<span class="cat">{CATL[a["category"]]}</span>{extra}</div>')
_fn,_fr,_fre,_fen,_fem=author_of(feat)
featured_html=('<article class="featured">'+card_cover(feat,'<span class="ctitle">HEADLINE</span>')+
    f'<div class="body"><span class="flag">헤드라인</span><h2><a class="clink" href="/{feat["category"]}/{feat["slug"]}/">{H.escape(feat["title"])}</a></h2>'
    f'<p>{H.escape(excerpt(feat.get("description",""),120))}</p>'
    f'<div class="meta" style="padding-top:6px"><span class="avatar">{_fem}</span><span class="who">{H.escape(_fn)}</span>'
    f'<span class="dot"></span><span class="num">{feat.get("date","").replace("-",".")}</span></div></div></article>')
rest=[a for a in sorted(arts,key=lambda x:x.get('date',''),reverse=True) if a['slug']!=feat['slug']][:9]
cards=''
for a in rest:
    _an,_ar,_are,_aen,_aem=author_of(a)
    cards+=('<article class="card">'+card_cover(a)+
        f'<div class="body"><h3><a class="clink" href="/{a["category"]}/{a["slug"]}/">{H.escape(a["title"])}</a></h3><p class="excerpt">{H.escape(excerpt(a.get("description","")))}</p>'
        f'<div class="meta"><span class="avatar">{_aem}</span><span class="who">{H.escape(_an)}</span>'
        f'<span class="dot"></span><span class="num">{a.get("date","").replace("-",".")}</span></div></div></article>')
_org={"@context":"https://schema.org","@type":"Organization","name":"맑은소프트","alternateName":"MALGNSOFT INC.","url":"https://www.malgnsoft.com","logo":"https://www.malgnsoft.com/img/logo.png","sameAs":["https://www.malgnsoft.com","https://blog.naver.com/malgnlms"]}
_web={"@context":"https://schema.org","@type":"WebSite","name":"맑은소프트 블로그","url":SITE,"inLanguage":"ko-KR","publisher":{"@type":"Organization","name":"맑은소프트"}}
HOME_LD=''.join(f'<script type="application/ld+json">{json.dumps(x,ensure_ascii=False)}</script>' for x in (_org,_web))
home_prefix=('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
 '<meta name="naver-site-verification" content="78d05abce6d558d7e4414c1b56bee9ca2d6cfdda">'
 '<meta name="google-site-verification" content="ed6YuxeH6G565UsO9R5T7yNPnQizMdcpjZINHNM8FQM">'
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="description" content="교육을 운영하는 사람을 위한 LMS 실전 지식. 기업교육·HRD 담당자를 위한 이러닝·자격검정·에듀테크 인사이트.">'
 '<meta property="og:type" content="website"><meta property="og:title" content="맑은소프트 블로그"><meta property="og:url" content="'+SITE+'/"><meta property="og:image" content="https://www.malgnsoft.com/img/og_logo.gif">'
 '<link rel="canonical" href="https://blog.malgnsoft.com/">'
 '<link rel="alternate" type="application/rss+xml" title="맑은소프트 블로그 RSS" href="https://blog.malgnsoft.com/rss.xml">'+HOME_LD)
home=head+featured_html+'\n\n  <div class="grid">\n'+cards+'\n  </div>\n'+tail
home=home.replace('</style>',HOME_EXTRA+'</style></head><body>',1)
home=home_prefix+home+TRACK+'</body></html>'
os.makedirs(OUT,exist_ok=True)
open(f"{OUT}/index.html",'w',encoding='utf-8').write(home)
print("HOME:",len(home)//1024,"KB, cards:",len(arts)-1,"+featured")

# ---- 카테고리 허브 페이지 ----
CATDESC={'lms':'LMS·이러닝 구축과 운영에 관한 실전 가이드','hrd':'기업교육·HRD 담당자를 위한 실무 지식','certification':'자격검정 시스템 구축·운영 가이드','video':'동영상·콘텐츠 플랫폼 이야기','edutech':'에듀테크·교육 AI 트렌드와 운영자 대응','news':'맑은소프트 소식과 신뢰자산'}
made_cats=[]
for cat in CATL:
    cat_arts=[a for a in sorted(arts,key=lambda x:x.get('date',''),reverse=True) if a['category']==cat]
    if not cat_arts: continue
    made_cats.append(cat)
    ccards=''
    for a in cat_arts:
        _an,_ar,_are,_aen,_aem=author_of(a)
        ccards+=('<article class="card">'+card_cover(a)+
            f'<div class="body"><h3><a class="clink" href="/{a["category"]}/{a["slug"]}/">{H.escape(a["title"])}</a></h3><p class="excerpt">{H.escape(excerpt(a.get("description","")))}</p>'
            f'<div class="meta"><span class="avatar">{_aem}</span><span class="who">{H.escape(_an)}</span>'
            f'<span class="dot"></span><span class="num">{a.get("date","").replace("-",".")}</span></div></div></article>')
    chead=(head.replace('<h1>맑은소프트 블로그</h1>',f'<h1>{CATL[cat]}</h1>',1)
        .replace('<p>국내 1위 LMS 맑은소프트에서 전하는 소식과 인사이트</p>',f'<p>{CATDESC[cat]}</p>',1)
        .replace('<title>맑은소프트 블로그 — 교육을 운영하는 사람을 위한 LMS 실전 지식</title>',f'<title>{CATL[cat]} — 맑은소프트 블로그</title>',1))
    cpage=chead+'  <div class="grid">\n'+ccards+'\n  </div>\n'+tail
    cpage=cpage.replace('</style>',HOME_EXTRA+'</style></head><body>',1)
    cprefix=('<!doctype html><html lang="ko"><head><meta charset="utf-8">'
     '<meta name="viewport" content="width=device-width,initial-scale=1">'
     f'<meta name="description" content="{CATDESC[cat]}"><link rel="canonical" href="{SITE}/{cat}/">')
    cpage=cprefix+cpage+TRACK+'</body></html>'
    os.makedirs(f"{OUT}/{cat}",exist_ok=True)
    open(f"{OUT}/{cat}/index.html",'w',encoding='utf-8').write(cpage)
print("CATEGORY pages:",made_cats)

# ---- sitemap.xml + robots.txt ----
gmax=max((a.get('date','') for a in arts), default='2026-07-14')
entries=[(SITE+"/",gmax,"daily")]
entries+=[(f"{SITE}/{c}/",gmax,"weekly") for c in made_cats]
entries+=[(f"{SITE}/{a['category']}/{a['slug']}/",a.get('date',gmax),"monthly") for a in arts]
sm=['<?xml version="1.0" encoding="UTF-8"?>','<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">']
for loc,mod,freq in entries:
    sm.append(f'  <url><loc>{loc}</loc><lastmod>{mod}</lastmod><changefreq>{freq}</changefreq></url>')
sm.append('</urlset>')
open(f"{OUT}/sitemap.xml",'w',encoding='utf-8').write('\n'.join(sm)+'\n')
_ai_bots=['Yeti','Daum','GPTBot','OAI-SearchBot','ChatGPT-User','PerplexityBot','ClaudeBot','Claude-Web','Google-Extended','CCBot','Bingbot','Applebot-Extended']
_robots="User-agent: *\nAllow: /\nDisallow: /admin\n\n"+"".join(f"User-agent: {b}\nAllow: /\n\n" for b in _ai_bots)+f"Sitemap: {SITE}/sitemap.xml\n"
open(f"{OUT}/robots.txt",'w',encoding='utf-8').write(_robots)
print("sitemap.xml:",len(entries),"urls | robots.txt")

# ---- RSS 피드 (네이버 웹마스터도구·구독기용) ----
import datetime as _dt
_WD=['Mon','Tue','Wed','Thu','Fri','Sat','Sun']; _MO=['Jan','Feb','Mar','Apr','May','Jun','Jul','Aug','Sep','Oct','Nov','Dec']
def _rfc822(d):
    try:
        y,m,day=map(int,d.split('-')); dt=_dt.date(y,m,day)
        return f"{_WD[dt.weekday()]}, {day:02d} {_MO[m-1]} {y} 09:00:00 +0900"
    except Exception: return "Mon, 01 Jan 2026 09:00:00 +0900"
_rss_items=''
for a in sorted(arts,key=lambda x:x.get('date',''),reverse=True):
    _u=f"{SITE}/{a['category']}/{a['slug']}/"
    _rss_items+=(f'<item><title>{H.escape(a["title"])}</title><link>{_u}</link>'
        f'<description>{H.escape(a.get("description",""))}</description>'
        f'<author>{H.escape(a.get("author","맑은소프트"))}</author><category>{CATL[a["category"]]}</category>'
        f'<pubDate>{_rfc822(a.get("date",""))}</pubDate><guid isPermaLink="true">{_u}</guid></item>')
_rss=('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
    f'<title>맑은소프트 블로그</title><link>{SITE}/</link>'
    '<description>교육을 운영하는 사람을 위한 LMS 실전 지식 — 기업교육·HRD·이러닝·자격검정·에듀테크</description>'
    f'<language>ko-KR</language><lastBuildDate>{_rfc822(gmax)}</lastBuildDate>'
    f'<atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>'
    f'{_rss_items}</channel></rss>')
open(f"{OUT}/rss.xml",'w',encoding='utf-8').write(_rss)
print("rss.xml:",len(arts),"items")

# ---- /admin 통계 대시보드 (비번 gamma, 데이터는 /api/stats) ----
_tmap={"/":"블로그 홈"}
for c in made_cats: _tmap[f"/{c}/"]=CATL[c]+" (카테고리)"
for a in arts: _tmap[f"/{a['category']}/{a['slug']}/"]=a['title']
ADMIN=r"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1"><meta name="robots" content="noindex,nofollow">
<title>맑은소프트 블로그 · 통계 관리</title>
<style>
:root{--bg:#f4f6fa;--card:#fff;--text:#1a2233;--muted:#6b7688;--line:#e6e9f0;--accent:#2563eb;--accent-soft:#e7efff}
@media(prefers-color-scheme:dark){:root{--bg:#0e1420;--card:#161d2b;--text:#e7ecf3;--muted:#93a0b4;--line:#273043;--accent:#5b8cff;--accent-soft:#1a2540}}
:root[data-theme="dark"]{--bg:#0e1420;--card:#161d2b;--text:#e7ecf3;--muted:#93a0b4;--line:#273043;--accent:#5b8cff;--accent-soft:#1a2540}
:root[data-theme="light"]{--bg:#f4f6fa;--card:#fff;--text:#1a2233;--muted:#6b7688;--line:#e6e9f0;--accent:#2563eb;--accent-soft:#e7efff}
*{box-sizing:border-box}body{margin:0;font-family:system-ui,-apple-system,'Malgun Gothic',sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.wrap{max-width:960px;margin:0 auto;padding:24px 18px 60px}
#gate{min-height:100vh;display:flex;align-items:center;justify-content:center;padding:20px}
.gatecard{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:36px 32px;width:100%;max-width:360px;box-shadow:0 10px 40px rgba(20,30,50,.10);text-align:center}
.gatecard h1{font-size:19px;margin:0 0 4px}.gatecard p{color:var(--muted);font-size:13px;margin:0 0 22px}
.gatecard input{width:100%;padding:12px 14px;border:1px solid var(--line);border-radius:10px;font-size:15px;background:var(--bg);color:var(--text);text-align:center;letter-spacing:.1em}
.gatecard input:focus{outline:none;border-color:var(--accent)}
.gatecard button{width:100%;margin-top:12px;padding:12px;border:0;border-radius:10px;background:var(--accent);color:#fff;font-size:15px;font-weight:700;cursor:pointer}
.err{color:#e5484d;font-size:13px;margin-top:12px;min-height:18px}
#dash{display:none}.top{display:flex;align-items:center;gap:12px;margin-bottom:22px;flex-wrap:wrap}
.top h1{font-size:20px;margin:0;font-weight:800;letter-spacing:-.02em}.top .sp{flex:1}.top .meta{color:var(--muted);font-size:13px}
.btn{border:1px solid var(--line);background:var(--card);color:var(--muted);padding:7px 12px;border-radius:8px;font-size:13px;cursor:pointer}
.cards{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:26px}@media(max-width:560px){.cards{grid-template-columns:1fr}}
.stat{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px}
.stat .lbl{color:var(--muted);font-size:13px;font-weight:600}.stat .val{font-size:34px;font-weight:800;letter-spacing:-.02em;margin-top:6px;font-variant-numeric:tabular-nums}
.panel{background:var(--card);border:1px solid var(--line);border-radius:14px;padding:20px 22px;margin-bottom:22px}.panel h2{font-size:15px;margin:0 0 16px;font-weight:800}
table{width:100%;border-collapse:collapse}th,td{text-align:left;padding:11px 8px;border-bottom:1px solid var(--line);font-size:14px}
th{color:var(--muted);font-size:12px;font-weight:700}td.n{text-align:right;font-variant-numeric:tabular-nums;font-weight:700}td.rank{width:34px;color:var(--muted);font-weight:700}
.bar{height:6px;background:var(--accent-soft);border-radius:3px;margin-top:5px}.bar span{display:block;height:100%;background:var(--accent);border-radius:3px}
a{color:var(--accent);text-decoration:none}
</style></head><body>
<div id="gate"><form class="gatecard" id="gform">
<div style="font-size:30px;margin-bottom:8px">📊</div><h1>블로그 통계 관리</h1><p>접근하려면 비밀번호를 입력하세요</p>
<input id="pw" type="password" placeholder="비밀번호" autocomplete="current-password" autofocus>
<button type="submit">입장</button><div class="err" id="err"></div></form></div>
<div id="dash"><div class="wrap">
<div class="top"><h1>📊 블로그 통계</h1><span class="meta" id="asof"></span><span class="sp"></span>
<button class="btn" id="refresh">새로고침</button><button class="btn" id="logout">나가기</button></div>
<div class="cards">
<div class="stat"><div class="lbl">오늘 조회수</div><div class="val" id="c-today">-</div></div>
<div class="stat"><div class="lbl">누적 조회수</div><div class="val" id="c-total">-</div></div>
<div class="stat"><div class="lbl">게시물 수</div><div class="val" id="c-posts">-</div></div></div>
<div class="panel"><h2>일별 조회수 (최근 30일)</h2><div id="chart"></div></div>
<div class="panel"><h2>게시물 조회수 순위</h2><table><thead><tr><th></th><th>제목</th><th style="text-align:right">조회수</th></tr></thead><tbody id="rank"></tbody></table></div>
</div></div>
<script>
var TMAP=__TMAP__,NPOSTS=__NPOSTS__;
function $(id){return document.getElementById(id)}
function fmt(n){return (n||0).toLocaleString('ko-KR')}
function esc(s){return (s+'').replace(/[&<>]/g,function(c){return {'&':'&amp;','<':'&lt;','>':'&gt;'}[c]})}
function drawChart(days){
 days=days.slice(-30);
 if(!days.length){$('chart').innerHTML='<p style="color:var(--muted);font-size:13px">아직 데이터가 없습니다.</p>';return}
 var W=880,H=200,pad=28,ih=H-pad*2,iw=W-pad*2,base=pad+ih;
 var max=Math.max.apply(null,days.map(function(d){return d.count}));if(max<1)max=1;
 var n=days.length;
 var pts=days.map(function(d,i){var x=pad+(n<=1?iw/2:iw*i/(n-1));var y=pad+ih-(d.count/max)*ih;return [x,y,d]});
 var poly=pts.map(function(p){return p[0].toFixed(1)+','+p[1].toFixed(1)}).join(' ');
 var area='M '+pad+' '+base+' L '+pts.map(function(p){return p[0].toFixed(1)+' '+p[1].toFixed(1)}).join(' L ')+' L '+pts[n-1][0].toFixed(1)+' '+base+' Z';
 var dots=pts.map(function(p){return '<circle cx="'+p[0].toFixed(1)+'" cy="'+p[1].toFixed(1)+'" r="2.5" fill="var(--accent)"/>'}).join('');
 function lbl(p){return '<text x="'+p[0].toFixed(1)+'" y="'+(H-6)+'" font-size="10" fill="var(--muted)" text-anchor="middle">'+p[2].date.slice(5)+'</text>'}
 var labels=[lbl(pts[0])];if(n>2)labels.push(lbl(pts[Math.floor(n/2)]));if(n>1)labels.push(lbl(pts[n-1]));
 $('chart').innerHTML='<svg viewBox="0 0 '+W+' '+H+'" width="100%" style="max-width:100%;height:auto">'+
  '<path d="'+area+'" fill="var(--accent-soft)" opacity=".55"/>'+
  '<polyline points="'+poly+'" fill="none" stroke="var(--accent)" stroke-width="2"/>'+dots+labels.join('')+'</svg>';
}
function render(d){
 $('c-today').innerHTML=fmt(d.today);$('c-total').innerHTML=fmt(d.total);$('c-posts').innerHTML=fmt(NPOSTS);
 $('asof').textContent=(d.date||'')+' 기준 (KST)';drawChart(d.days||[]);
 var max=(d.posts[0]&&d.posts[0].count)||1;
 var rows=(d.posts||[]).slice(0,40).map(function(p,i){var t=TMAP[p.path]||p.path;var w=Math.round(p.count/max*100);
  return '<tr><td class="rank">'+(i+1)+'</td><td><a href="'+esc(p.path)+'" target="_blank">'+esc(t)+'</a><div class="bar"><span style="width:'+w+'%"></span></div></td><td class="n">'+fmt(p.count)+'</td></tr>'}).join('');
 $('rank').innerHTML=rows||'<tr><td colspan="3" style="color:var(--muted)">아직 조회 데이터가 없습니다.</td></tr>';
 $('gate').style.display='none';$('dash').style.display='block';
}
function load(pw){return fetch('/api/stats?pw='+encodeURIComponent(pw)).then(function(r){if(r.status!==200)throw new Error('bad');return r.json()}).then(function(d){sessionStorage.setItem('bpw',pw);render(d)})}
$('gform').addEventListener('submit',function(e){e.preventDefault();$('err').textContent='';load($('pw').value).catch(function(){$('err').textContent='비밀번호가 올바르지 않습니다.'})});
$('refresh').addEventListener('click',function(){var pw=sessionStorage.getItem('bpw');if(pw)load(pw)});
$('logout').addEventListener('click',function(){sessionStorage.removeItem('bpw');location.reload()});
(function(){var pw=sessionStorage.getItem('bpw');if(pw)load(pw).catch(function(){sessionStorage.removeItem('bpw')})})();
</script></body></html>"""
ADMIN=ADMIN.replace('__TMAP__',json.dumps(_tmap,ensure_ascii=False)).replace('__NPOSTS__',str(len(arts)))
os.makedirs(f"{OUT}/admin",exist_ok=True)
open(f"{OUT}/admin/index.html",'w',encoding='utf-8').write(ADMIN)
print("admin dashboard 생성")

print("TOTAL articles:",len(arts))
EOF=1
