#!/usr/bin/env python3
"""알약캡쳐 앱 아이콘/스플래시 생성 → assets/icons/icon-{180,192,512,1024}.png, icon-foreground.png, splash-2732.png
   글자 없이 도형만 그리므로 폰트가 없는 CI 러너에서도 동일하게 나옵니다. pip install pillow 필요.
   원본 로고로 바꾸려면 assets/icons/*.png 를 같은 이름으로 교체하세요.
"""
import pathlib
from PIL import Image, ImageDraw

ROOT = pathlib.Path(__file__).resolve().parent.parent
OUT = ROOT / 'assets/icons'; OUT.mkdir(parents=True, exist_ok=True)
BG = (14, 138, 116)        # 앱 액센트 #0E8A74
BG2 = (10, 105, 89)
WHITE = (255, 255, 255)
ORANGE = (255, 122, 26)

def draw_icon(n, rounded=True, bg=BG):
    S = 4  # 슈퍼샘플링(부드러운 가장자리)
    N = n * S
    im = Image.new('RGBA', (N, N), (0, 0, 0, 0)); d = ImageDraw.Draw(im)
    if rounded: d.rounded_rectangle((0, 0, N - 1, N - 1), radius=int(N * 0.22), fill=bg + (255,))
    else: d.rectangle((0, 0, N - 1, N - 1), fill=bg + (255,))
    # 뷰파인더 모서리
    m, L, w = int(N * 0.16), int(N * 0.14), max(2, int(N * 0.035))
    for (x, y, dx, dy) in ((m, m, 1, 1), (N - m, m, -1, 1), (m, N - m, 1, -1), (N - m, N - m, -1, -1)):
        d.line((x, y, x + dx * L, y), fill=WHITE + (230,), width=w)
        d.line((x, y, x, y + dy * L), fill=WHITE + (230,), width=w)
    # 기울어진 캡슐: 절반 흰색 / 절반 주황
    cw, ch = int(N * 0.56), int(N * 0.26); cx, cy = N // 2, N // 2
    box = (cx - cw // 2, cy - ch // 2, cx + cw // 2, cy + ch // 2)
    mask = Image.new('L', (N, N), 0); ImageDraw.Draw(mask).rounded_rectangle(box, radius=ch // 2, fill=255)
    body = Image.new('RGBA', (N, N), (0, 0, 0, 0)); bd = ImageDraw.Draw(body)
    bd.rectangle((box[0], box[1], cx, box[3]), fill=WHITE + (255,))
    bd.rectangle((cx, box[1], box[2], box[3]), fill=ORANGE + (255,))
    bd.line((cx, box[1], cx, box[3]), fill=BG2 + (255,), width=max(2, int(N * 0.012)))
    cap = Image.new('RGBA', (N, N), (0, 0, 0, 0)); cap.paste(body, (0, 0), mask)
    cap = cap.rotate(-28, resample=Image.BICUBIC, center=(cx, cy))
    im = Image.alpha_composite(im, cap)
    return im.resize((n, n), Image.LANCZOS)

for n in (180, 192, 512):
    draw_icon(n).save(OUT / f'icon-{n}.png'); print('icon', n)
# App Store 1024: 투명 없이 정사각(모서리는 iOS가 깎음)
draw_icon(1024, rounded=False).convert('RGB').save(OUT / 'icon-1024.png'); print('icon 1024')
# 안드로이드 어댑티브 아이콘 전경(안전 영역 고려해 작게)
fg = Image.new('RGBA', (1024, 1024), (0, 0, 0, 0)); ic = draw_icon(640)
fg.paste(ic, (192, 192), ic); fg.save(OUT / 'icon-foreground.png'); print('adaptive fg')
# 스플래시 2732
sp = Image.new('RGB', (2732, 2732), (243, 246, 244)); ic = draw_icon(560)
sp.paste(ic, ((2732 - 560) // 2, (2732 - 560) // 2 - 120), ic); sp.save(OUT / 'splash-2732.png'); print('splash')
