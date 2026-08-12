# TOAST UI Editor (벤더링)

관리자 콘솔 `/gamma2` 의 본문 위지윅 에디터. **CDN을 쓸 수 없는 자체서버 환경**이라
dist 를 저장소에 넣고 정적 파일로 서빙한다(`build.py` 가 `/gamma2/vendor/toastui/` 로 복사).

| 파일 | 원본 | 비고 |
|---|---|---|
| `toastui-editor.min.js` | `@toast-ui/editor@3.2.2` → `dist/toastui-editor.js` | esbuild 0.23 `--minify` |
| `toastui-editor.min.css` | 같은 패키지 `dist/toastui-editor.css` | 〃 |
| `toastui-editor-ko-kr.min.js` | 같은 패키지 `dist/i18n/ko-kr.js` | 한국어 UI |

- 라이선스: **MIT** (NHN Cloud FE Development Lab). 배너 주석을 파일 첫 줄에 보존했다.
- 갱신 방법: `npm pack @toast-ui/editor@3` → `dist/` 를 위 표대로 minify 해 덮어쓴다.
- **에디터를 업그레이드할 때는 표·인라인 SVG 가 든 기존 글을 반드시 한 편 열어 확인할 것.**
  이 블로그 본문은 마크다운에 원시 HTML 이 섞여 있어(`build.py` 의 `md_in_html`),
  위지윅 모드가 그 블록을 재작성하면 글이 깨진다. 콘솔이 그런 글을 마크다운 탭으로
  강제하는 이유다(`admin-console/시안-p2-관리자콘솔.html` 의 `hasRawHtml()`).
