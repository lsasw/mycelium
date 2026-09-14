# -*- coding: utf-8 -*-
"""
Moto image fetcher
从 cn.bing.com 图片搜索抓取指定车型的照片，评分筛选后下载到 images/ 目录。
"""
import json, os, re, html, subprocess, sys, time

BASE = os.path.dirname(os.path.abspath(__file__))
IMG_DIR = os.path.join(BASE, "images")
os.makedirs(IMG_DIR, exist_ok=True)

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")

# 车型清单: id -> (检索词, 用于相关性判断的关键词列表)
MODELS = [
    # 仿赛
    ("cf-450sr",      "春风450SR 摩托车",            ["450SR"]),
    ("kayo-450rr",    "凯越450RR 摩托车",            ["450RR"]),
    ("zx-500rr",      "张雪500RR 摩托车",            ["500RR"]),
    ("qj-sai600rs",   "钱江赛600RS 摩托车",          ["赛600"]),
    ("honda-cbr500r", "本田CBR500R 摩托车",          ["CBR500R"]),
    ("kawasaki-ninja400", "川崎Ninja400 摩托车",     ["Ninja", "400"]),
    ("ducati-panigalev4", "杜卡迪Panigale V4 摩托车", ["Panigale"]),
    # 街车
    ("cf-250nk",      "春风250NK 摩托车",            ["250NK"]),
    ("cf-800nk",      "春风800NK 摩托车",            ["800NK"]),
    ("qj-zhui600",    "钱江追600 摩托车",            ["追600"]),
    ("voge-525r",     "无极525R 摩托车",             ["525R"]),
    ("honda-cb400f",  "本田CB400F 摩托车",           ["CB400F"]),
    ("yamaha-mt07",   "雅马哈MT-07 摩托车",          ["MT-07", "MT07"]),
    ("kawasaki-z900", "川崎Z900 摩托车",             ["Z900"]),
    # 巡航
    ("benda-jinjila300", "奔达金吉拉300 摩托车",     ["金吉拉"]),
    ("benda-huishi250",  "奔达灰石250 摩托车",       ["灰石"]),
    ("voge-cu625",    "无极CU625 巡航摩托车",        ["CU625"]),
    ("voge-cu250",    "无极CU250 巡航摩托车",        ["CU250"]),
    ("qj-shan300s",   "钱江闪300S 摩托车",           ["闪300"]),
    ("honda-cm500",   "本田CM500 摩托车",            ["CM500"]),
    ("harley-sportsters", "哈雷Sportster S 摩托车",  ["Sportster"]),
    # 复古
    ("cf-700clx",     "春风700CL-X 复古摩托车",      ["CL-X", "700CL"]),
    ("voge-300ac",    "无极300AC 复古摩托车",        ["300AC"]),
    ("benelli-leoncino500", "贝纳利幼狮500 摩托车",  ["幼狮", "Leoncino"]),
    ("honda-cb350",   "本田CB350 复古摩托车",        ["CB350"]),
    ("triumph-trident660", "凯旋Trident660 摩托车",  ["Trident", "三叉戟"]),
    # 拉力 ADV
    ("kayo-525x",     "凯越525X 摩托车",             ["525X"]),
    ("voge-ds625x",   "无极DS625X 摩托车",           ["DS625X"]),
    ("cf-450mt",      "春风450MT 摩托车",            ["450MT"]),
    ("benelli-trk552", "贝纳利TRK552 摩托车",        ["TRK"]),
    ("honda-nx400",   "本田NX400 摩托车",            ["NX400"]),
    ("bmw-r1250gs",   "宝马R1250GS 水鸟 摩托车",     ["R1250", "GS"]),
    # 踏板
    ("haojue-uhr150", "豪爵UHR150 摩托车",           ["UHR150"]),
    ("voge-sr4max",   "无极SR4 Max 摩托车",          ["SR4"]),
    ("sdk-rt3",       "赛科龙RT3 摩托车",            ["RT3"]),
    ("sanyang-drg158","三阳DRG158 摩托车",           ["DRG"]),
    ("honda-pcx160",  "本田PCX160 摩托车",           ["PCX"]),
    ("yamaha-nmax155","雅马哈NMAX155 摩托车",        ["NMAX"]),
    ("yamaha-xmax300","雅马哈XMAX300 摩托车",        ["XMAX"]),
    # 越野 / 林道
    ("kayo-800x",     "凯越800X 摩托车",             ["800X"]),
    ("kaiwei-t250x",  "凯威Finder T250X 摩托车",     ["T250X", "Finder"]),
    ("honda-crf250l", "本田CRF250L 摩托车",          ["CRF"]),
    ("ktm-500exc",    "KTM 500 EXC-F 越野摩托车 实拍", ["500 EXC", "500EXC"]),
    # ── 扩充：仿赛 ──
    ("cf-675sr",      "春风675SR 摩托车",            ["675SR"]),
    ("voge-525rr",    "无极525RR 摩托车",            ["525RR"]),
    ("qj-sai550",     "钱江赛550 摩托车",            ["赛550"]),
    ("kayo-321rr",    "凯越321RR 摩托车",            ["321RR"]),
    ("kawasaki-zx4r", "川崎ZX-4R 摩托车",            ["ZX-4R", "ZX4R"]),
    ("aprilia-rs457", "阿普利亚RS457 摩托车",        ["RS457"]),
    ("honda-cbr650r", "本田CBR650R 摩托车",          ["CBR650R"]),
    ("yamaha-r3",     "雅马哈YZF-R3 摩托车",         ["R3"]),
    ("ktm-rc390",     "KTM RC390 摩托车",            ["RC390"]),
    # ── 扩充：街车 ──
    ("cf-450nk",      "春风450NK 摩托车",            ["450NK"]),
    ("qj-zhui550",    "钱江追550 摩托车",            ["追550"]),
    ("voge-625r",     "无极625R 摩托车",             ["625R"]),
    ("zontes-703r",   "升仕703R 摩托车",             ["703R"]),
    ("honda-cb650r",  "本田CB650R 摩托车",           ["CB650R"]),
    ("yamaha-mt09",   "雅马哈MT-09 摩托车",          ["MT-09", "MT09"]),
    ("kawasaki-z650", "川崎Z650 摩托车",             ["Z650"]),
    ("ktm-790duke",   "KTM 790 Duke 摩托车",         ["790"]),
    ("triumph-streettriple765", "凯旋Street Triple 765 摩托车", ["Street Triple", "765"]),
    ("yamaha-mt03",   "雅马哈MT-03 摩托车",          ["MT-03", "MT03"]),
    # ── 扩充：巡航 ──
    ("benda-jinjila500", "奔达金吉拉500 摩托车",     ["金吉拉"]),
    ("benda-heiqi500",   "奔达黑旗500 摩托车",       ["黑旗"]),
    ("benda-huishi707",  "奔达灰石707 摩托车",       ["灰石"]),
    ("voge-cu525",    "无极CU525 摩托车",            ["CU525"]),
    ("qj-shan500s",   "钱江闪500S 摩托车",           ["闪500"]),
    ("honda-cm1100",  "本田CM1100 Rebel1100 摩托车", ["CM1100", "Rebel"]),
    ("harley-nightster", "哈雷Nightster 摩托车",     ["Nightster"]),
    # ── 扩充：复古 ──
    ("voge-525ac",    "无极525AC 复古摩托车",        ["525AC"]),
    ("cf-250clx",     "春风250CL-X 摩托车",          ["CL-X", "250CL"]),
    ("benelli-leoncino800", "贝纳利幼狮800 摩托车",  ["幼狮", "Leoncino"]),
    ("benelli-imperiale400", "贝纳利帝国400 摩托车", ["帝国", "Imperiale"]),
    ("yamaha-xsr700", "雅马哈XSR700 摩托车",         ["XSR700", "XSR"]),
    ("triumph-speed400", "凯旋Speed400 摩托车",      ["Speed 400", "Speed400"]),
    ("re-classic350", "皇家恩菲尔德Classic350 摩托车", ["Classic 350", "Classic350"]),
    ("moto-guzzi-v7", "摩托古兹V7 摩托车",           ["V7"]),
    ("honda-cb1100",  "本田CB1100 摩托车",           ["CB1100"]),
    # ── 扩充：拉力ADV ──
    ("kayo-625x",     "凯越625X 摩托车",             ["625X"]),
    ("voge-ds900x",   "无极DS900X 摩托车",           ["DS900X"]),
    ("voge-ds525x",   "无极DS525X 摩托车",           ["DS525X"]),
    ("cf-800mt",      "春风800MT 摩托车",            ["800MT"]),
    ("cf-700mt",      "春风700MT 摩托车",            ["700MT"]),
    ("benelli-trk502x", "贝纳利TRK502X 摩托车",      ["TRK"]),
    ("honda-cb500x",  "本田CB500X 摩托车",           ["CB500X"]),
    ("suzuki-vstrom650", "铃木V-Strom650 摩托车",    ["V-Strom", "Vstrom"]),
    ("bmw-g310gs",    "宝马G310GS 摩托车",           ["G310"]),
    ("ktm-390adv",    "KTM 390 Adventure 摩托车",    ["390 Adventure", "390ADV"]),
    ("ktm-790adv",    "KTM 790 Adventure 摩托车",    ["790 Adventure", "790ADV"]),
    ("bmw-r1300gs",   "宝马R1300GS 摩托车",          ["R1300"]),
    # ── 扩充：踏板 ──
    ("haojue-ufr150", "豪爵UFR150 摩托车",           ["UFR150"]),
    ("haojue-afr125", "豪爵AFR125 摩托车",           ["AFR125"]),
    ("voge-sr250gt",  "无极SR250GT 摩托车",          ["SR250"]),
    ("sdk-rt2",       "赛科龙RT2 摩托车",            ["RT2"]),
    ("sanyang-xunyi150", "三阳巡弋150 摩托车",       ["巡弋"]),
    ("kymco-ct250",   "光阳CT250 摩托车",            ["CT250"]),
    ("kymco-saiti250", "光阳赛艇250 摩托车",         ["赛艇"]),
    ("honda-adv160",  "本田ADV160 摩托车",           ["ADV160"]),
    ("honda-forza350", "本田FORZA350 摩托车",        ["FORZA"]),
    ("yamaha-aerox155", "雅马哈Aerox155 摩托车",     ["Aerox"]),
    ("vespa-primavera150", "Vespa春天150 踏板摩托车", ["Vespa", "春天"]),
    ("peugeot-django150", "标致姜戈150 摩托车",      ["姜戈", "Django"]),
    ("suzuki-uy125",  "铃木UY125 摩托车",            ["UY125"]),
    # ── 扩充：越野 ──
    ("kayo-450rally", "凯越450 Rally 摩托车",        ["450 Rally", "450Rally"]),
    ("honda-crf300l", "本田CRF300L 摩托车",          ["CRF300"]),
    ("honda-crf250rally", "本田CRF250 Rally 摩托车", ["CRF250"]),
    ("yamaha-wr250r", "雅马哈WR250R 越野摩托车",     ["WR250"]),
    ("ktm-350exc",    "KTM 350 EXC-F 越野摩托车",    ["350 EXC", "350EXC"]),
    ("ktm-250exc",    "KTM 250 EXC-F 越野摩托车",    ["250 EXC", "250EXC"]),
    # ── 扩充：电动摩托 ──
    ("ninebot-e300p", "九号E300P 电动摩托车",        ["E300P", "E300"]),
    ("ninebot-e100",  "九号E100 电动摩托车",         ["E100"]),
    ("niucore-nxt",   "小牛NXT Ultra 电动车",        ["NXT"]),
    ("niucore-nqi",   "小牛NQi GT 电动车",           ["NQi"]),
    ("jihue-ae8",     "极核AE8 电动摩托车",          ["AE8"]),
]

BLACK = ["黑板报", "素材", "模板", "矢量", "简笔画", "壁纸", "头像", "表情",
         "玩具", "手办", "贴纸", "涂色", "线稿", "png", "logo", "标志",
         "配色", "海报", "插画", "图片大全", "高清图片", "psd", "t shirt",
         "wallpaper", "coloring", "clip art", "vector", "svg"]

GOOD_DOMAIN = ["cfmoto", "qjmotor", "qjmotors", "voge", "kayo", "zontes",
               "benda", "benelli", "haojue", "honda", "yamaha", "kawasaki",
               "bmw", "ducati", "triumph", "harley", "ktm", "suzuki",
               "58moto", "autoimg", "bitautoimg", "autohome", "huaban",
               "motor", "moto", "bike", "riders", "yiche", "dongchedi"]


def bing_search(query):
    """返回 [(murl, turl, title, w, h)]"""
    import urllib.parse
    url = ("https://cn.bing.com/images/search?q=" + urllib.parse.quote(query) +
           "&form=HDRSC2&mkt=zh-CN&first=1")
    try:
        out = subprocess.run(["curl", "-sSL", "-m", "25", "-A", UA,
                              "-H", "Accept-Language: zh-CN,zh;q=0.9",
                              url], capture_output=True)
        page = out.stdout.decode("utf-8", "ignore")
    except Exception as e:
        print("  search fail", e)
        return []
    items = re.findall(r'class="iusc"[^>]*m="([^"]+)"', page)
    res = []
    for it in items:
        try:
            d = json.loads(html.unescape(it))
        except Exception:
            continue
        murl, turl, title = d.get("murl", ""), d.get("turl", ""), d.get("t", "")
        w = h = 0
        md = d.get("md", "")
        m = re.match(r"(\d+)\s*[x×]\s*(\d+)", md) if md else None
        if m:
            w, h = int(m.group(1)), int(m.group(2))
        res.append((murl, turl, title, w, h))
    return res


def score(item, keys):
    murl, turl, title, w, h = item
    tl = (title or "").lower()
    score = 0
    # 相关性：标题命中关键型号
    for k in keys:
        if k.lower() in tl:
            score += 60
            break
    else:
        score -= 25
    # 黑名单
    for b in BLACK:
        if b in tl:
            score -= 120
    # 域名偏好
    for g in GOOD_DOMAIN:
        if g in murl.lower():
            score += 18
            break
    # 尺寸偏好（横向、够大）
    if w and h:
        if w >= 900:
            score += 25
        elif w >= 600:
            score += 12
        if h and w / h >= 1.15:
            score += 8
        if w < 400:
            score -= 20
    if murl.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        score += 5
    return score


def valid_image(path):
    try:
        if os.path.getsize(path) < 12000:
            return False
        with open(path, "rb") as f:
            head = f.read(16)
    except Exception:
        return False
    return (head.startswith(b"\xff\xd8\xff") or head.startswith(b"\x89PNG") or
            head[:4] == b"RIFF" or head[:6] in (b"GIF87a", b"GIF89a"))


def download(url):
    ext = ".jpg"
    low = url.lower().split("?")[0]
    if low.endswith(".png"):
        ext = ".png"
    elif low.endswith(".webp"):
        ext = ".webp"
    tmp = os.path.join(IMG_DIR, "_tmp" + ext)
    if os.path.exists(tmp):
        os.remove(tmp)
    try:
        subprocess.run(["curl", "-sSL", "-m", "30", "-A", UA,
                        "-H", "Referer: https://cn.bing.com/",
                        "-o", tmp, url], capture_output=True)
    except Exception:
        return None
    return tmp if valid_image(tmp) else None


def main():
    only = sys.argv[1] if len(sys.argv) > 1 else None
    manifest, fail = {}, []
    for mid, query, keys in MODELS:
        if only and only != mid:
            continue
        final = os.path.join(IMG_DIR, mid + ".jpg")
        if os.path.exists(final) and os.path.getsize(final) > 12000:
            manifest[mid] = {"file": "images/" + mid + ".jpg", "src": "cached"}
            print("[skip]", mid)
            continue
        print("[search]", mid, "|", query)
        cands = bing_search(query)
        if not cands:
            fail.append(mid)
            print("   ! no result")
            continue
        cands.sort(key=lambda x: score(x, keys), reverse=True)
        got = None
        for it in cands[:8]:
            for url in (it[0], it[1]):
                if not url:
                    continue
                p = download(url)
                if p:
                    got = (p, url, it[2])
                    break
            if got:
                break
        if not got:
            fail.append(mid)
            print("   ! download fail")
            continue
        p, url, title = got
        os.replace(p, final)
        manifest[mid] = {"file": "images/" + mid + ".jpg",
                         "src": title[:80], "url": url}
        print("   ok", os.path.getsize(final), title[:60])
        time.sleep(0.4)

    mf = os.path.join(BASE, "images.json")
    old = {}
    if os.path.exists(mf):
        old = json.load(open(mf, encoding="utf-8"))
    old.update(manifest)
    json.dump(old, open(mf, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("\nDONE. ok=%d fail=%d" % (len(manifest), len(fail)))
    if fail:
        print("FAILED:", ", ".join(fail))


if __name__ == "__main__":
    main()
