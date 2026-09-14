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
const FILES = ['./', './index.html', './manifest.webmanifest', './icons/icon-192.png', './icons/icon-512.png'];
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
# 스토어 등록용 이미지도 Pages로 공개 (콘솔 업로드용)
SS = ROOT / 'store/screenshots'
if SS.exists():
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
