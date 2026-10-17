#!/usr/bin/env python3
# 공개 데이터 3종 + 사용자 트레이 라벨을 YOLO(1클래스 'pill') 형식으로 합치기.
# 입력: CountingPills(yolov8 zip, 폴리곤 라벨) / Pill Detection(yolov8 zip, 74클래스) / Pill-Counter(git) / user_lab
import os, sys, glob, csv, zipfile, shutil, subprocess
from PIL import Image
WORK = sys.argv[1] if len(sys.argv) > 1 else '/content/work'
CP_ZIP, KR_ZIP = sys.argv[2], sys.argv[3]
USER_LAB = sys.argv[4] if len(sys.argv) > 4 else ''
OUT = f'{WORK}/data'
for sp in ['train', 'val', 'test']:
    os.makedirs(f'{OUT}/{sp}/images', exist_ok=True); os.makedirs(f'{OUT}/{sp}/labels', exist_ok=True)
n = {'train': 0, 'val': 0, 'test': 0}
def put(img, lines, sp, name, maxside=640, q=88):
    im = Image.open(img).convert('RGB'); s = min(1, maxside / max(im.size))
    if s < 1: im = im.resize((round(im.width * s), round(im.height * s)), Image.LANCZOS)
    im.save(f'{OUT}/{sp}/images/{name}.jpg', quality=q)
    open(f'{OUT}/{sp}/labels/{name}.txt', 'w').write('\n'.join(lines) + ('\n' if lines else '')); n[sp] += 1
# 1) Pill-Counter (256장 실사진, 세션 단위 split)
if not os.path.exists(f'{WORK}/pc'):
    subprocess.run(['git', 'clone', '-q', '--depth', '1', 'https://github.com/TetraHikari/Pill-Counter', f'{WORK}/pc'], check=True)
split = {r['photo']: r['split'] for r in csv.DictReader(open(f'{WORK}/pc/data/real/split.csv'))}
for photo, sp in split.items():
    img = f'{WORK}/pc/data/real/images/{photo}'
    if not os.path.exists(img):
        c = glob.glob(f'{WORK}/pc/data/real/**/{photo}', recursive=True); img = c[0] if c else None
    if not img: continue
    lab = f'{WORK}/pc/data/real/labels/' + photo.replace('.jpg', '.txt')
    lines = ['0 ' + ' '.join(l.split()[1:5]) for l in open(lab) if len(l.split()) >= 5] if os.path.exists(lab) else []
    from PIL import ImageOps
    im = ImageOps.exif_transpose(Image.open(img)); tmp = f'{WORK}/_tmp.jpg'; im.save(tmp, quality=95)
    put(tmp, lines, sp, 'pc_' + photo[:-4], maxside=900)
# 2) CountingPills: 폴리곤 → bbox, 증강 복제본(.rf.해시) 중 원본 1장만
d = f'{WORK}/cp'; zipfile.ZipFile(CP_ZIP).extractall(d)
for src, sp in [('train', 'train'), ('valid', 'val'), ('test', 'test')]:
    seen = set()
    for img in sorted(glob.glob(f'{d}/{src}/images/*.jpg')):
        base = os.path.basename(img); key = base.split('.rf.')[0]
        if key in seen: continue
        seen.add(key); lab = f'{d}/{src}/labels/' + base.rsplit('.', 1)[0] + '.txt'; lines = []
        if os.path.exists(lab):
            for l in open(lab):
                v = list(map(float, l.split()[1:]))
                if len(v) < 6: continue
                xs, ys = v[0::2], v[1::2]; x0, x1, y0, y1 = min(xs), max(xs), min(ys), max(ys)
                lines.append(f'0 {(x0+x1)/2:.5f} {(y0+y1)/2:.5f} {x1-x0:.5f} {y1-y0:.5f}')
        put(img, lines, sp, 'cp_' + key)
# 3) Pill Detection (국내약 74종 → 1클래스), 150장은 val
d = f'{WORK}/kr'; zipfile.ZipFile(KR_ZIP).extractall(d)
imgs = sorted(glob.glob(f'{d}/*/images/*.jpg')); import random; random.seed(0); random.shuffle(imgs)
for i, img in enumerate(imgs):
    lab = img.replace('/images/', '/labels/').rsplit('.', 1)[0] + '.txt'
    lines = ['0 ' + ' '.join(l.split()[1:5]) for l in open(lab) if len(l.split()) >= 5] if os.path.exists(lab) else []
    put(img, lines, 'val' if i < 150 else 'train', 'kr_' + os.path.basename(img).split('.rf.')[0])
# 4) 사용자 트레이 라벨 (3번 복제)
if USER_LAB and os.path.exists(f'{USER_LAB}/tri30.jpg'):
    lines = [l.strip() for l in open(f'{USER_LAB}/tri30.txt') if l.strip()]
    for k in range(3): put(f'{USER_LAB}/tri30.jpg', lines, 'train', f'user_tri30_{k}', maxside=900)
open(f'{OUT}/data.yaml', 'w').write(f"path: {OUT}\ntrain: train/images\nval: val/images\ntest: test/images\nnc: 1\nnames: ['pill']\n")
print('dataset', n)
