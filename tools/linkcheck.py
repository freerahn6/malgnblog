# -*- coding: utf-8 -*-
"""본문 내부링크가 실제 생성된 페이지를 가리키는지 검사한다.

빌드 산출물(_deploy/public)에 실제로 만들어진 index.html을 진실로 삼는다.
front matter를 파싱해 URL을 추측하면 오탐이 난다(실측으로 확인된 사항).

사용: python build.py && python tools/linkcheck.py
      깨진 링크가 있으면 종료코드 1 → CI에서 배포를 막을 수 있다.

배경: 미발행 slug로 링크가 걸린 채 발행된 사례가 6건 있었다(2026-07-23 정리).
      "나중에 쓸 글"을 미리 링크해 두면 그대로 죽은 링크가 된다.
"""
import io, glob, os, re, sys

BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(BASE, '_deploy', 'public')
ART = os.path.join(BASE, 'articles')

# 빌드가 만들지 않지만 유효한 경로: /contact/는 빌드 시 외부 문의 URL로 치환된다(build.py)
EXTRA_VALID = {'/', '/contact/'}


def built_urls():
    urls = set(EXTRA_VALID)
    for p in glob.glob(os.path.join(OUT, '**', 'index.html'), recursive=True):
        rel = os.path.relpath(p, OUT).replace(os.sep, '/')
        urls.add('/' + rel[:-len('index.html')])
    return urls


def main():
    if not os.path.isdir(OUT):
        print('[linkcheck] 빌드 산출물이 없습니다. 먼저 python build.py 를 실행하세요.')
        return 1

    valid = built_urls()
    bad = {}
    for f in sorted(glob.glob(os.path.join(ART, '*.md'))):
        s = io.open(f, encoding='utf-8').read()
        for link in sorted(set(re.findall(r'\]\((/[^)#]*)\)', s))):
            if link not in valid:
                bad.setdefault(link, []).append(os.path.basename(f)[:-3])

    print('[linkcheck] 생성된 URL %d개 / 검사한 글 %d편'
          % (len(valid), len(glob.glob(os.path.join(ART, '*.md')))))
    if not bad:
        print('[linkcheck] 깨진 내부링크 없음')
        return 0

    print('[linkcheck] 깨진 내부링크 %d종:' % len(bad))
    for link, files in sorted(bad.items()):
        print('  %-52s <- %s' % (link, ', '.join(files)))
    print('\n미발행 글을 가리키고 있습니다. 링크를 지우거나, 발행된 글로 바꾸세요.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
