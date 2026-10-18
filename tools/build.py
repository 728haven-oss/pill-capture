#!/usr/bin/env python3
"""src/app.html → docs/ (PWA + Capacitor webDir)
   - index.html : 완전한 HTML 문서로 감싸고 manifest/아이콘/서비스워커 등록
   - manifest.webmanifest, sw.js, icons/
"""
import pathlib, shutil, subprocess, sys, json, hashlib, os

ROOT = pathlib.Path(__file__).resolve().parent.parent
SRC = ROOT / 'src/app.html'
DOCS = ROOT / 'docs'
NAME = '알약캡쳐'
THEME = '#0E8A74'

subprocess.run([sys.executable, str(ROOT / 'tools/make_icons.py')], check=True)
DOCS.mkdir(exist_ok=True)
(DOCS / 'icons').mkdir(exist_ok=True)
for n in (180, 192, 512):
    shutil.copy(ROOT / f'assets/icons/icon-{n}.png', DOCS / f'icons/icon-{n}.png')

body = SRC.read_text(encoding='utf-8')
# RevenueCat 공개 API 키 주입 (GitHub Secrets → 환경변수). 없으면 플레이스홀더 유지(구독 비활성)
body = body.replace('__RC_ANDROID_KEY__', os.environ.get('RC_ANDROID_KEY', '__RC_ANDROID_KEY__')).replace('__RC_IOS_KEY__', os.environ.get('RC_IOS_KEY', '__RC_IOS_KEY__'))
# ── 결제 on/off (config/billing.json) ─────────────────────────────
#  enabled:false → 완전 무료 배포: 모든 기능 무제한, 요금제 표시·페이월·RevenueCat 초기화 비활성
#  결제 재개: bash tools/enable_billing.sh  (전체 결제 구현 원본: 브랜치 billing-v1)
_bc = ROOT / 'config/billing.json'
BILLING = json.loads(_bc.read_text(encoding='utf-8')).get('enabled', True) if _bc.exists() else True
for a, b in [
    ("const FREE_PER_DAY = 5;", "const FREE_PER_DAY = 5;\nconst BILLING = %s; // config/billing.json" % ('true' if BILLING else 'false')),
    ("function canAnalyze(kind){ // kind: 'photo' | 'live' | 'video'\n", "function canAnalyze(kind){ // kind: 'photo' | 'live' | 'video'\n  if(!BILLING) return true;\n"),
    ("  if(!Pro.native){ $('plan').hidden = true; return; }", "  if(!BILLING || !Pro.native){ $('plan').hidden = true; return; }"),
    ("  renderPlan();\n  if(!Pro.native) return;", "  renderPlan();\n  if(!BILLING || !Pro.native) return;"),
]:
    assert body.count(a) == 1, 'billing patch target not found: ' + a[:40]
    body = body.replace(a, b)
print('billing', 'ON' if BILLING else 'OFF (free build)')
# ── 로그인 + 가입 후 무료체험 (config/auth.json, src/auth.js) ─────
#  enabled:false 면 아무 것도 주입하지 않음 → 기존 동작 그대로
_ac = ROOT / 'config/auth.json'
AUTH = json.loads(_ac.read_text(encoding='utf-8')) if _ac.exists() else {'enabled': False}
AUTH.pop('_comment', None)
AUTH_JS = ''
if AUTH.get('enabled'):
    AUTH['supabaseUrl'] = os.environ.get('SUPABASE_URL', AUTH.get('supabaseUrl', ''))
    AUTH['supabaseAnonKey'] = os.environ.get('SUPABASE_ANON_KEY', AUTH.get('supabaseAnonKey', ''))
    AUTH_JS = ('<script>window.__PC_AUTH=' + json.dumps(AUTH, ensure_ascii=False) + ';</script>\n<script>'
               + (ROOT / 'src/auth.js').read_text(encoding='utf-8') + '</script>')
    print('auth ON (trial %s days, providers %s)' % (AUTH.get('trialDays'), [k for k, v in (AUTH.get('providers') or {}).items() if v]))
else:
    print('auth OFF')
body = body + '\n' + AUTH_JS if AUTH_JS else body
# ── 학습형 알약 검출기 (src/ml: tf.min.js, pillnet.js, pillnet.json, pillnet.bin) → docs/ml/
#  있으면 <script> 로 주입하고 앱이 시작 시 모델을 읽는다. 없으면 규칙 기반만 동작
ML_DIR = ROOT / 'src/ml'
ML_TAGS = ''
if (ML_DIR / 'pillnet.bin').exists():
    (DOCS / 'ml').mkdir(exist_ok=True)
    for f in ('tf.min.js', 'pillnet.js', 'pillnet.json', 'pillnet.bin'):
        shutil.copy(ML_DIR / f, DOCS / 'ml' / f)
    mlver = hashlib.sha1((ML_DIR / 'pillnet.bin').read_bytes()).hexdigest()[:8]
    ML_TAGS = f'<script src="ml/tf.min.js"></script>\n<script src="ml/pillnet.js"></script>\n<script>window.__PC_ML={{json:"ml/pillnet.json?v={mlver}",bin:"ml/pillnet.bin?v={mlver}"}};</script>'
    print('ml detector ON', mlver)
    # YOLO 상자 검출기(src/ml/yolo: model.json + group*.bin + meta.json) 가 있으면 우선 사용
    YD = ML_DIR / 'yolo'; YOLO_FILES = []
    if (YD / 'model.json').exists() and (ML_DIR / 'pillyolo.js').exists():
        (DOCS / 'ml' / 'yolo').mkdir(exist_ok=True)
        yver = hashlib.sha1(b''.join(sorted(f.read_bytes() for f in YD.glob('*.bin')))).hexdigest()[:8]
        for f in sorted(YD.iterdir()):
            if f.is_file(): shutil.copy(f, DOCS / 'ml' / 'yolo' / f.name); YOLO_FILES.append('./ml/yolo/' + f.name)
        shutil.copy(ML_DIR / 'pillyolo.js', DOCS / 'ml' / 'pillyolo.js'); YOLO_FILES.append('./ml/pillyolo.js')
        meta = json.loads((YD / 'meta.json').read_text()) if (YD / 'meta.json').exists() else {}
        ML_TAGS += f'\n<script src="ml/pillyolo.js"></script>\n<script>window.__PC_ML.yolo="ml/yolo/model.json?v={yver}";window.__PC_ML.yoloConf={meta.get("conf", 0.35)};</script>'
        print('yolo detector ON', yver, meta)
else:
    print('ml detector OFF')
ver = hashlib.sha1(body.encode()).hexdigest()[:8]
html = f'''<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="{THEME}">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="{NAME}">
<link rel="manifest" href="manifest.webmanifest">
<link rel="apple-touch-icon" href="icons/icon-180.png">
<link rel="icon" type="image/png" sizes="192x192" href="icons/icon-192.png">
<style>body{{padding-top:env(safe-area-inset-top)}} .dock{{padding-bottom:calc(14px + env(safe-area-inset-bottom))!important}}</style>
</head>
<body>
{ML_TAGS}
{body}
<script>
if ('serviceWorker' in navigator && location.protocol === 'https:') {{
  navigator.serviceWorker.register('sw.js?v={ver}').catch(function(){{}});
}}
</script>
</body>
</html>
'''
(DOCS / 'index.html').write_text(html, encoding='utf-8')

manifest = {
    'name': NAME, 'short_name': NAME, 'lang': 'ko',
    'description': '알약 사진 한 장으로 종류별 개수 확인',
    'start_url': './index.html', 'scope': './', 'display': 'standalone',
    'background_color': '#F3F6F4', 'theme_color': THEME,
    'icons': [
        {'src': 'icons/icon-192.png', 'sizes': '192x192', 'type': 'image/png', 'purpose': 'any'},
        {'src': 'icons/icon-512.png', 'sizes': '512x512', 'type': 'image/png', 'purpose': 'any maskable'},
    ],
}
(DOCS / 'manifest.webmanifest').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')

sw = f'''const C = 'pillcapture-{ver}';
const FILES = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png'{', "./ml/tf.min.js", "./ml/pillnet.js", "./ml/pillnet.json", "./ml/pillnet.bin"' if ML_TAGS else ''}{''.join(', "%s"' % f for f in (YOLO_FILES if ML_TAGS else []))}];
self.addEventListener('install', e => {{ e.waitUntil(caches.open(C).then(c => c.addAll(FILES)).then(() => self.skipWaiting())); }});
self.addEventListener('activate', e => {{ e.waitUntil(caches.keys().then(ks => Promise.all(ks.filter(k => k !== C).map(k => caches.delete(k)))).then(() => self.clients.claim())); }});
self.addEventListener('fetch', e => {{
  if (e.request.method !== 'GET' || !e.request.url.startsWith(self.location.origin)) return;
  e.respondWith(fetch(e.request).then(r => {{ const cp = r.clone(); caches.open(C).then(c => c.put(e.request, cp)); return r; }}).catch(() => caches.match(e.request)));
}});
'''
(DOCS / 'sw.js').write_text(sw, encoding='utf-8')
(DOCS / '.nojekyll').write_text('')
shutil.copy(ROOT / 'store/privacy.html', DOCS / 'privacy.html')
shutil.copy(ROOT / 'store/terms.html', DOCS / 'terms.html')
# 스토어 등록용 이미지도 Pages로 공개 (콘솔 업로드용) — Pages 워크플로에서만 (앱 번들에 6MB 스크린샷이 섞이지 않도록)
SS = ROOT / 'store/screenshots'
if SS.exists() and os.environ.get('GITHUB_WORKFLOW', '').startswith('PWA'):
    (DOCS / 'store').mkdir(exist_ok=True)
    for f in SS.glob('*.png'): shutil.copy(f, DOCS / 'store' / f.name)
    for n in (512, 1024): shutil.copy(ROOT / f'assets/icons/icon-{n}.png', DOCS / 'store' / f'icon-{n}.png')
# store/pages_assets.txt 에 적힌 URL(릴리스 AAB 등)을 docs/store/ 로 내려받아 Pages에 함께 공개 (콘솔 업로드용, 실패해도 무시)
#  (Pages 워크플로에서만 — 앱 빌드(docs=webDir)에 섞이지 않도록)
PA = ROOT / 'store/pages_assets.txt'
if PA.exists() and os.environ.get('GITHUB_WORKFLOW', '').startswith('PWA'):
    import urllib.request
    (DOCS / 'store').mkdir(exist_ok=True)
    for line in PA.read_text(encoding='utf-8').splitlines():
        url = line.strip()
        if not url or url.startswith('#'): continue
        try:
            urllib.request.urlretrieve(url, DOCS / 'store' / url.rsplit('/', 1)[-1])
            print('fetched', url)
        except Exception as e:
            print('skip', url, e)
print('build OK →', DOCS, 'version', ver)
