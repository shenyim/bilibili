#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
bilibili_hot_json.py
功能：抓取 B 站热搜，生成同目录文件 bilibili.json
"""
from pathlib import Path
import time, json, random
import requests

HERE = Path(__file__).resolve().parent
OUT_JSON = HERE / "bilibili.json"

URL = "https://s.search.bilibili.com/main/hotword"
UA_POOL = [
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 14_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.5 Safari/605.1.15",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0 Safari/537.36",
]

def fetch(max_retry=4, timeout=8):
    last = None
    for i in range(max_retry):
        try:
            r = requests.get(
                URL,
                headers={
                    "User-Agent": random.choice(UA_POOL),
                    "Referer": "https://www.bilibili.com/",
                    "Accept": "application/json,text/plain,*/*",
                },
                timeout=timeout,
            )
            r.raise_for_status()
            return r.json()
        except Exception as e:
            last = e
            time.sleep(0.8 + 0.4 * i)
    raise SystemExit(f"[bilibili] fetch failed: {last}")

def normalize(raw):
    # 兼容不同字段：list / result / data.list / hotword
    items = None
    if isinstance(raw, dict):
        for key in ("list", "result", "hotword"):
            v = raw.get(key)
            if isinstance(v, list): items = v; break
        if items is None and isinstance(raw.get("data"), dict):
            d = raw["data"]
            for key in ("list", "result", "hotword"):
                v = d.get(key)
                if isinstance(v, list): items = v; break
    if not items: return []

    out = []
    for idx, it in enumerate(items[:10], 1):
        text = it.get("keyword") or it.get("show_name") or it.get("name") or it.get("word") or ""
        if not text: continue
        mark = it.get("icon") or it.get("img")
        if isinstance(mark, str) and mark.startswith("//"): mark = "https:" + mark
        out.append({"rank": idx, "text": text, "mark": mark})
    return out

def main():
    raw = fetch()
    items = normalize(raw)
    payload = {
        "source": "bilibili",
        "generated_at": time.strftime("%Y-%m-%d %H:%M:%S GMT", time.gmtime()),
        "items": items,
    }
    OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"[bilibili] wrote {OUT_JSON} ({len(items)} items)")

if __name__ == "__main__":
    main()
