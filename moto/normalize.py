# -*- coding: utf-8 -*-
"""统一图片为真实 JPEG、限制尺寸并压缩，输出宽高比报告。"""
import os, glob, json
from PIL import Image

BASE = os.path.dirname(os.path.abspath(__file__))
IMGDIR = os.path.join(BASE, "images")
MAXW = 1200
Q = 84

report, portrait = {}, []
before = after = 0
files = sorted(glob.glob(os.path.join(IMGDIR, "*.jpg")) +
               glob.glob(os.path.join(IMGDIR, "*.png")))

for p in files:
    mid = os.path.splitext(os.path.basename(p))[0]
    if mid.startswith("_"):
        continue
    before += os.path.getsize(p)
    try:
        im = Image.open(p)
        im.load()
        fmt = im.format
        if im.mode in ("RGBA", "LA", "P"):
            im = im.convert("RGBA")
            bg = Image.new("RGB", im.size, (245, 245, 243))
            bg.paste(im, mask=im.split()[-1])
            im = bg
        else:
            im = im.convert("RGB")
        w, h = im.size
        if w > MAXW:
            im = im.resize((MAXW, round(h * MAXW / w)), Image.LANCZOS)
        out = os.path.join(IMGDIR, mid + ".jpg")
        im.save(out, "JPEG", quality=Q, optimize=True, progressive=True)
        # 清理同名 png 残留
        legacy = os.path.join(IMGDIR, mid + ".png")
        if os.path.exists(legacy) and os.path.abspath(legacy) != os.path.abspath(p):
            os.remove(legacy)
        nw, nh = im.size
        ratio = round(nw / nh, 2)
        report[mid] = {"w": nw, "h": nh, "ratio": ratio, "src_fmt": fmt}
        if ratio < 1.2:
            portrait.append(mid)
        after += os.path.getsize(out)
        print(f"{mid:24s} {fmt:5s} {w}x{h} -> {nw}x{nh}  ratio={ratio}  {os.path.getsize(out)//1024}KB")
    except Exception as e:
        print("FAIL", mid, e)

json.dump(report, open(os.path.join(BASE, "image_report.json"), "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print("\n总计: %.1f MB -> %.1f MB" % (before / 1048576, after / 1048576))
print("非横图(ratio<1.2)需 contain 显示:", ", ".join(portrait) if portrait else "无")
