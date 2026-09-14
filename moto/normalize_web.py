# -*- coding: utf-8 -*-
"""生成 WebP 版图片（源为 _img_src 备份），并清掉旧 jpg。

用法: python normalize_web.py [quality] [maxw]
默认 q=70 / maxw=800 —— 从 8.8MB 降到约 3.9MB。
宽高比不变，index.html 里的 contain 标记无需改动；
但页面引用需从 .jpg 改为 .webp（index.html 仅一处）。
"""
import os, glob, shutil, sys
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
SRC = os.path.join(BASE, "_img_src")
IMGDIR = os.path.join(BASE, "images")
Q = int(sys.argv[1]) if len(sys.argv) > 1 else 70
MAXW = int(sys.argv[2]) if len(sys.argv) > 2 else 800

if not os.path.isdir(SRC):
    raise SystemExit("_img_src 不存在，无法重新生成")

for f in glob.glob(os.path.join(IMGDIR, "*.jpg")):
    os.remove(f)

files = sorted(glob.glob(os.path.join(SRC, "*.jpg")))
total = 0
for p in files:
    mid = os.path.splitext(os.path.basename(p))[0]
    im = Image.open(p)
    im.load()
    im = im.convert("RGB")
    w, h = im.size
    if w > MAXW:
        im = im.resize((MAXW, round(h * MAXW / w)), Image.LANCZOS)
    out = os.path.join(IMGDIR, mid + ".webp")
    im.save(out, "WEBP", quality=Q, method=6)
    total += os.path.getsize(out)

print("q=%d maxw=%d -> %.2f MB  (%d 张, 平均 %dKB)"
      % (Q, MAXW, total / 1048576, len(files), total / len(files) / 1024))
