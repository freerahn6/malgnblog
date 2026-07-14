# -*- coding: utf-8 -*-
import re, os, json, markdown, html as H
BASE=os.path.dirname(os.path.abspath(__file__)); ART=BASE+"/articles"; PREV=BASE+"/_preview"; OUT=BASE+"/_deploy/public"; _D=BASE+"/_deploy"
SITE="https://blog.malgnsoft.com"

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
BANL=open(_D+'/wecandeo_datauri.txt',encoding='utf-8').read().strip()
BANR=open(_D+'/malgnsoft_datauri.txt',encoding='utf-8').read().strip()
BAN_LEFT=f'<a class="side-banner" href="https://www.wecandeo.com" target="_blank" rel="noopener"><img src="{BANL}" alt="위캔디오 - 동영상 클라우드 플랫폼"></a>'
BAN_RIGHT=f'<aside class="rail"><a href="https://www.malgnsoft.com" target="_blank" rel="noopener"><img src="{BANR}" alt="맑은소프트"></a></aside>'
EXTRA_CSS=('.wrap{max-width:1320px}'
 '.article-shell{grid-template-columns:176px minmax(0,1fr) 176px;gap:44px}'
 '.rail-left{position:sticky;top:88px;align-self:start}'
 '.rail-left .side-banner{display:block;width:160px;margin:0 auto;border-radius:12px;overflow:hidden;line-height:0;box-shadow:var(--shadow);transition:transform .18s}'
 '.rail-left .side-banner:hover{transform:translateY(-3px)}'
 '.rail-left .side-banner img{width:100%;height:auto;display:block}'
 'aside.rail{position:sticky;top:88px;align-self:start;max-height:calc(100vh - 104px);overflow-y:auto;overflow-x:hidden;scrollbar-width:thin}'
 'aside.rail a{display:block;width:160px;margin:0 auto;border-radius:12px;overflow:hidden;line-height:0;box-shadow:var(--shadow);transition:transform .18s}'
 'aside.rail a:hover,aside.toc .side-banner:hover{transform:translateY(-3px)}'
 'aside.rail img{width:100%;height:auto;display:block}'
 '.byline .brole{color:var(--accent);font-weight:600;margin-left:6px;font-size:13px}'
 '.namecard{margin:50px 0 8px;display:flex;justify-content:center}'
 '.nc-badge{position:relative;width:100%;max-width:450px;background:var(--surface);border:1px solid var(--border);border-radius:20px;overflow:hidden;box-shadow:var(--shadow)}'
 '.nc-badge::before{content:"";position:absolute;top:-45px;right:-45px;width:140px;height:140px;border-radius:50%;background:linear-gradient(135deg,var(--accent),#1ec8c8);opacity:.16}'
 '.nc-badge::after{content:"";position:absolute;bottom:-28px;left:-28px;width:88px;height:88px;border-radius:26px;background:#1ec8c8;opacity:.12;transform:rotate(18deg)}'
 '.nc-hdr{position:relative;display:flex;justify-content:flex-end;padding:15px 22px 0}'
 '.nc-logo{font-weight:800;font-size:13px;letter-spacing:.16em;color:var(--accent)}'
 '.nc-row{position:relative;display:flex;align-items:center;gap:18px;padding:12px 24px 8px}'
 '.nc-photo{width:76px;height:76px;border-radius:20px;background:var(--accent-soft);display:flex;align-items:center;justify-content:center;font-size:42px;line-height:1;flex:none;border:2px solid var(--surface);box-shadow:0 4px 14px rgba(20,30,50,.12)}'
 '.nc-txt{min-width:0}'
 '.nc-nm{font-size:24px;font-weight:800;color:var(--text);letter-spacing:-0.02em;line-height:1.05;display:flex;align-items:baseline;gap:8px;flex-wrap:wrap}'
 '.nc-nm .nc-en{font-size:12px;font-weight:600;color:var(--faint);letter-spacing:.04em}'
 '.nc-rl{margin-top:6px;font-size:14px;font-weight:700;color:var(--accent);display:flex;align-items:baseline;gap:7px}'
 '.nc-rl .nc-en2{font-size:10.5px;font-weight:600;color:var(--faint);letter-spacing:.08em}'
 '.nc-tm{margin-top:7px;font-size:12.5px;color:var(--muted)}'
 '.nc-ft{position:relative;display:flex;justify-content:space-between;align-items:center;padding:11px 24px;margin-top:10px;border-top:1px solid var(--border);font-size:10.5px;font-weight:700;letter-spacing:.05em;color:var(--faint);text-transform:uppercase;background:color-mix(in srgb,var(--accent-soft) 45%,transparent)}'
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

def md2html(body):
    h=markdown.markdown(body,extensions=['fenced_code','sane_lists','attr_list','md_in_html'])
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
</main>{banr}</div>
<footer class="site"><div class="wrap"><span class="plate"><img src="{logo}" alt="맑은소프트"></span><span>맑은소프트 블로그 · (주)맑은소프트</span><span style="margin-left:auto">© 맑은소프트</span></div></footer>
{fab}
{script}
</body></html>'''

for a in arts:
    body_html,toc=md2html(a['body'])
    body_html=body_html.replace('href="/contact/"',f'href="{INQ}" target="_blank" rel="noopener"')
    _ti=[]
    for k,(sid,txt) in enumerate(toc):
        cls=' class="on"' if k==0 else ''
        _ti.append(f'<li><a href="#{sid}"{cls}>{H.escape(txt)}</a></li>')
    toc_html=''.join(_ti)
    hero=IMG.get(a['slug'],COVERS[1])
    aname,arole,aroleEn,aen,aemoji=author_of(a)
    namecard=(f'<div class="namecard"><div class="nc-badge">'
        f'<div class="nc-hdr"><span class="nc-logo">MALGNSOFT</span></div>'
        f'<div class="nc-row"><div class="nc-photo">{aemoji}</div>'
        f'<div class="nc-txt"><div class="nc-nm">{H.escape(aname)}<span class="nc-en">{aen}</span></div>'
        f'<div class="nc-rl">{arole}<span class="nc-en2">{aroleEn}</span></div>'
        f'<div class="nc-tm">맑은소프트 블로그 전담팀</div></div></div>'
        f'<div class="nc-ft"><span>이 글을 쓴 사람</span><span>malgnsoft.com</span></div></div></div>')
    _url=f"{SITE}/{a['category']}/{a['slug']}/"
    page=PAGE.format(title=H.escape(a['title']),desc=H.escape(a.get('description','')),cat=a['category'],slug=a['slug'],
        catlabel=CATL.get(a['category'],a['category']),css=ACSS,logo=LOGO,toc=toc_html,date=a.get('date',''),
        rt=read_min(a['body']),hero=hero,body=body_html,fab=FAB,script=SCRIPT,extra=EXTRA_CSS,banl=BAN_LEFT,banr=BAN_RIGHT,
        aname=H.escape(aname),arole=arole,ainit=aemoji,namecard=namecard,jsonld=jsonld(a,_url))
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
feat=bysl['lms-selection-guide-for-corporate-training']
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
 '<meta name="viewport" content="width=device-width,initial-scale=1">'
 '<meta name="description" content="교육을 운영하는 사람을 위한 LMS 실전 지식. 기업교육·HRD 담당자를 위한 이러닝·자격검정·에듀테크 인사이트.">'
 '<meta property="og:type" content="website"><meta property="og:title" content="맑은소프트 블로그"><meta property="og:url" content="'+SITE+'/"><meta property="og:image" content="https://www.malgnsoft.com/img/og_logo.gif">'
 '<link rel="canonical" href="https://blog.malgnsoft.com/">'+HOME_LD)
home=head+featured_html+'\n\n  <div class="grid">\n'+cards+'\n  </div>\n'+tail
home=home.replace('</style>',HOME_EXTRA+'</style></head><body>',1)
home=home_prefix+home+'</body></html>'
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
    cpage=cprefix+cpage+'</body></html>'
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
_ai_bots=['GPTBot','OAI-SearchBot','ChatGPT-User','PerplexityBot','ClaudeBot','Claude-Web','Google-Extended','CCBot','Bingbot','Applebot-Extended']
_robots="User-agent: *\nAllow: /\n\n"+"".join(f"User-agent: {b}\nAllow: /\n\n" for b in _ai_bots)+f"Sitemap: {SITE}/sitemap.xml\n"
open(f"{OUT}/robots.txt",'w',encoding='utf-8').write(_robots)
print("sitemap.xml:",len(entries),"urls | robots.txt")

print("TOTAL articles:",len(arts))
EOF=1
