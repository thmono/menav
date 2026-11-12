#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从浏览器导出的书签 HTML 生成 MeNav 配置：
  · 按「应用类型」重新归类（taxonomy.py）
  · 用 Chrome 历史给书签排点击次数，生成「常用」「最近访问」
  · 内网/自建类站点单独输出，不进公开站

用法：
    python3 build_site.py bookmarks.html            # 输出 config/user/pages/bookmarks.yml
    python3 build_site.py bookmarks.html --top 20   # 常用/最近各取 20 条
    python3 build_site.py bookmarks.html --no-history
"""

import argparse
import collections
import datetime
import os
import re
import sys
from urllib.parse import urlsplit

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import build_from_chrome as B
import taxonomy as T
from gen_bookmarks import BookmarkParser

ALLOWED_SCHEMES = {"http", "https"}
EXCLUDE_CATS_FROM_PUBLIC = {"selfhost", "private"}
# 这些原文件夹里的东西一律不进公开站（成人内容 / 翻墙工具）
PRIVATE_FOLDER_HINTS = ("blue", "翻墙", "porn", "adult", "sex", "梯子")


def clean(s):
    s = (s or "").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = B.INVISIBLE_RE.sub("", s)
    s = re.sub(r"\s{2,}", " ", s).strip(" -|·")
    return s


def norm(url):
    p = urlsplit(url)
    return f"{p.scheme.lower()}://{p.netloc.lower()}{p.path.rstrip('/')}" + (f"?{p.query}" if p.query else "")


CHROME_JSON_CANDIDATES = [
    "~/Library/Application Support/Google/Chrome/Default/AccountBookmarks",
    "~/Library/Application Support/Google/Chrome/Default/EncryptedAccountBookmarks2",
    "~/Library/Application Support/Google/Chrome/Default/Bookmarks.bak",
    "~/Library/Application Support/Google/Chrome/Default/Bookmarks",
]


def items_from_chrome_json(path):
    import json
    data = json.load(open(os.path.expanduser(path), encoding="utf-8"))
    out = []

    def rec(node, path_):
        for c in node.get("children", []) or []:
            if c.get("type") == "url":
                out.append({"url": c.get("url", ""), "name": c.get("name", ""), "path": list(path_)})
            else:
                rec(c, path_ + [clean(c.get("name"))])

    for root in (data.get("roots") or {}).values():
        if isinstance(root, dict):
            rec(root, [])
    return out


def find_chrome_json():
    for cand in CHROME_JSON_CANDIDATES:
        f = os.path.expanduser(cand)
        if not os.path.isfile(f):
            continue
        try:
            items = items_from_chrome_json(f)
        except Exception:
            continue
        if items:
            return f, items
    return None, []


def walk(node, path, out):
    for child in node.get("children", []):
        if child.get("type") in ("url", "bookmark"):
            out.append({"url": child.get("url", ""), "name": child.get("name", ""), "path": list(path)})
        else:
            name = clean(child.get("name"))
            container = (name == "" or name.lower() in {"书签栏", "其他书签", "bookmarks bar",
                                                        "bookmarks toolbar", "other bookmarks",
                                                        "书签工具栏", "书签菜单"})
            walk(child, path if container else path + [name], out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("source", nargs="?", default="")
    ap.add_argument("--out-dir", default="config/user/pages")
    ap.add_argument("--title", default="我的书签站")
    ap.add_argument("--subtitle", default="")
    ap.add_argument("--top", type=int, default=15)
    ap.add_argument("--profile", default="Default")
    ap.add_argument("--no-history", action="store_true")
    args = ap.parse_args()
    top_n = max(10, args.top)

    src = args.source
    if src and src.lower().endswith(".json"):
        items = items_from_chrome_json(src)
        print(f"数据源：{src}（Chrome JSON）")
    elif src:
        parser = BookmarkParser()
        parser.feed(open(src, "rb").read().decode("utf-8", errors="replace"))
        items = []
        walk(parser.root, [], items)
        print(f"数据源：{src}（导出 HTML）")
    else:
        found, items = find_chrome_json()
        if not found:
            sys.exit("❌ 没找到 Chrome 书签文件，请手动传入导出的 bookmarks.html")
        print(f"数据源：{found}（自动探测）")
        # 留一份快照，方便回溯
        snap_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "snapshots")
        os.makedirs(snap_dir, exist_ok=True)
        snap = os.path.join(snap_dir, datetime.datetime.now().strftime("account-%Y%m%d.json"))
        try:
            import shutil
            shutil.copyfile(found, snap)
            olds = sorted(f for f in os.listdir(snap_dir) if f.startswith("account-"))
            for f in olds[:-8]:
                os.remove(os.path.join(snap_dir, f))
        except Exception as e:
            print(f"⚠️ 快照失败：{e}", file=sys.stderr)
    print(f"书签 {len(items)} 条")

    # ---- 历史：点击数 / 最近访问
    hist_exact, hist_host = {}, {}
    if not args.no_history:
        try:
            rows = B.read_history(os.path.join(B.CHROME_DIR, args.profile))
        except Exception as e:
            rows = []
            print(f"⚠️ 历史读取失败 {e}", file=sys.stderr)
        for url, _t, vc, lt in rows:
            if not url.startswith(("http://", "https://")):
                continue
            ts = B.chrome_time(lt)
            hist_exact[norm(url)] = (vc or 0, ts)
            host = re.sub(r"^https?://(www\.)?", "", url).split("/")[0].lower()
            hv, hl = hist_host.get(host, (0, None))
            hist_host[host] = (hv + (vc or 0), hl if (hl and (not ts or hl > ts)) else ts or hl)
        print(f"历史 {len(rows)} 条可用于排序")

    seen = set()
    sites, dropped = [], collections.Counter()
    for it in items:
        url = (it["url"] or "").strip()
        p = urlsplit(url)
        if p.scheme.lower() not in ALLOWED_SCHEMES or not p.netloc:
            dropped["非网页链接"] += 1
            continue
        key = norm(url)
        if key in seen:
            dropped["重复"] += 1
            continue
        seen.add(key)
        host = re.sub(r"^(www\.)?", "", p.netloc.lower())
        if B.IMAGE_PATH_RE.search(p.path):
            dropped["图片"] += 1
            continue

        bare = host.split(":")[0]
        title = clean(it["name"])
        folders = it["path"]
        name = B.SITE_NAMES.get(bare) or (title[:26] if title else bare)
        if not name:
            continue

        ev, el = hist_exact.get(key, (0, None))
        hv, hl = hist_host.get(host, (0, None))
        # 站点级热度优先（同一站点多个深链接不会互相压分）
        vc = max(ev or 0, 0)
        vc = hv if (hv or 0) > vc else vc
        lt = max(filter(None, [el, hl]), default=None)

        cat = T.classify(bare, f"{title} {' '.join(folders)}", folders)
        if B.is_private_host(host) or bare in B.SKIP_HOSTS and False:
            cat = "selfhost"
        if B.is_private_host(host):
            cat = "selfhost"
        folder_text = " ".join(folders).lower()
        if any(h in folder_text for h in PRIVATE_FOLDER_HINTS):
            cat = "private"

        sites.append({
            "name": name, "url": url, "host": bare, "cat": cat,
            "visits": vc or 0, "last": lt,
            "favicon": B.FAVICON_MAP.get(bare),
            "folder": " / ".join(folders[-2:]),
            "original": url,
        })

    print(f"收录 {len(sites)} 条；丢弃 " + " / ".join(f"{k} {v}" for k, v in dropped.items()) or "")

    public = [s for s in sites if s["cat"] not in EXCLUDE_CATS_FROM_PUBLIC]
    private = [s for s in sites if s["cat"] in EXCLUDE_CATS_FROM_PUBLIC]

    def q(v):
        return "'" + clean(str(v)).replace("'", "''") + "'"

    def ds(dt):
        return dt.strftime("%m-%d") if dt else ""

    def block(s, desc):
        out = [f"      - name: {q(s['name'])}", f"        url: {q(s['url'])}", "        icon: 'fas fa-link'"]
        if s["favicon"]:
            out.append(f"        faviconUrl: {q(s['favicon'])}")
        out.append(f"        description: {q(desc)}")
        return out

    def desc(s, mode=""):
        bits = []
        if mode == "clicks" and s["visits"]:
            bits.append(f"点击 {s['visits']} 次")
        if mode == "recent" and s["last"]:
            bits.append(f"最近 {ds(s['last'])}")
        if s["folder"]:
            bits.append(s["folder"])
        return " · ".join(bits) or "收藏"

    def build_yaml(title, subtitle, groups):
        out = [
            "# 由 build_site.py 自动生成：书签按应用类型重新归类，点击数来自 Chrome 历史。",
            f"# 生成时间：{datetime.datetime.now():%Y-%m-%d %H:%M}",
            "",
            f"title: {q(title)}",
            f"subtitle: {q(subtitle)}",
            "template: bookmarks",
            "",
            "categories:",
        ]
        for name, icon, entries, mode in groups:
            if not entries:
                continue
            out += [f"  - name: {q(name)}", f"    icon: {q(icon)}", "    sites:"]
            for s in entries:
                out += block(s, desc(s, mode))
        return "\n".join(out) + "\n"

    # 常用
    def top_by(key_fn, pool):
        seen_hosts, picked = set(), []
        for s in pool:
            if s["host"] in seen_hosts:
                continue
            seen_hosts.add(s["host"])
            picked.append(s)
            if len(picked) >= top_n:
                break
        return picked

    common = top_by(None, sorted([s for s in public if s["visits"] > 0], key=lambda s: -s["visits"]))
    recent = top_by(None, sorted([s for s in public if s["last"]], key=lambda s: s["last"], reverse=True))

    groups = [(T.CATEGORIES["common"][0], T.CATEGORIES["common"][1], common, "clicks"),
              (T.CATEGORIES["recent"][0], T.CATEGORIES["recent"][1], recent, "recent")]
    order = ["ecom", "ai", "content", "design", "dev", "research", "biz", "freelance",
             "office", "learn", "read", "net", "social", "fun", "other"]
    for key in order:
        grp = [s for s in public if s["cat"] == key]
        if not grp:
            continue
        grp.sort(key=lambda s: (-s["visits"], s["folder"], s["name"]))
        groups.append((T.CATEGORIES[key][0], T.CATEGORIES[key][1], grp, ""))

    subtitle = args.subtitle or f"{len(public)} 个收藏 · 按应用类型归类 · 常用按点击次数排序"
    os.makedirs(args.out_dir, exist_ok=True)
    main_out = os.path.join(args.out_dir, "bookmarks.yml")
    open(main_out, "w", encoding="utf-8").write(build_yaml(args.title, subtitle, groups))
    print(f"✅ 公开站 {main_out}（{len(public)} 个站点）")

    if private:
        private.sort(key=lambda s: (-s["visits"], s["name"]))
        pgroups = []
        for key in ("selfhost", "private"):
            grp = [s for s in private if s["cat"] == key]
            if grp:
                pgroups.append((T.CATEGORIES[key][0], T.CATEGORIES[key][1], grp, ""))
        priv_out = os.path.join(args.out_dir, "bookmarks-内网-勿上传.yml")
        open(priv_out, "w", encoding="utf-8").write(
            build_yaml("内网与自建", "NAS / 路由 / 面板 —— 公网打不开，别上传", pgroups))
        print(f"✅ 内网 {priv_out}（{len(private)} 个站点，私密）")

    dist = collections.Counter(s["cat"] for s in public)
    print("   公开分类：" + " / ".join(f"{T.CATEGORIES[k][0]} {v}" for k, v in dist.most_common()))
    others = [s for s in public if s["cat"] == "other"]
    if others:
        print("   其他样例：" + "，".join(f"{s['name']}[{s['folder']}]" for s in others[:15]))


if __name__ == "__main__":
    main()
