#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
连载页面正文批量抓取并拼接（requests + BeautifulSoup）

用途
----
抓取分页 / 连载形式的内容页，剥掉 html 标签只留纯文本，按顺序追加到一个 txt。
适合把论坛长帖、小说连载、文档分页之类的内容整篇扒下来。

依赖
----
    pip install requests beautifulsoup4

用法
----
    python text_series.py --url-template "https://example.com/post_{n}.html" \
        --start 1 --end 30 --selector "div.article" --out out.txt

- ``--url-template`` 用 ``{n}`` 占位页码
- ``--selector``     CSS 选择器，定位正文容器（默认 div.article）
- 第一页 URL 与后续不同时，用 ``--first-url`` 单独指定
- ``--delay``        每次请求间隔秒数，礼貌抓取（默认 0.5）
"""
from __future__ import annotations

import argparse
import time

import requests
from bs4 import BeautifulSoup

HEADERS = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}


def fetch_text(url: str, selector: str, encoding: str | None) -> str:
    r = requests.get(url, headers=HEADERS, timeout=15)
    r.encoding = encoding or r.apparent_encoding
    soup = BeautifulSoup(r.text, "html.parser")
    node = soup.select_one(selector)
    if node is None:
        return ""
    # 剥掉会混入噪音的内联标签，只保留正文文本
    for tag in node.find_all(["p", "a", "span", "div"]):
        tag.extract()
    return node.get_text(strip=True)


def main() -> None:
    ap = argparse.ArgumentParser(description="连载页面正文批量抓取")
    ap.add_argument("--url-template", required=True, help="含 {n} 占位的 URL 模板")
    ap.add_argument("--first-url", help="第一页专用 URL（可选）")
    ap.add_argument("--start", type=int, default=1, help="起始页码")
    ap.add_argument("--end", type=int, required=True, help="结束页码")
    ap.add_argument("--selector", default="div.article", help="正文 CSS 选择器")
    ap.add_argument("--out", default="output.txt", help="输出文本文件")
    ap.add_argument("--encoding", default=None, help="页面编码，默认自动识别")
    ap.add_argument("--delay", type=float, default=0.5, help="请求间隔秒数（礼貌抓取）")
    args = ap.parse_args()

    with open(args.out, "w", encoding="utf-8") as f:
        for n in range(args.start, args.end + 1):
            if n == args.start and args.first_url:
                url = args.first_url
            else:
                url = args.url_template.format(n=n)
            try:
                text = fetch_text(url, args.selector, args.encoding)
            except requests.RequestException as e:
                print(f"[{n}] 请求失败: {e}")
                continue
            print(f"[{n}] {len(text)} 字")
            f.write("\n" + text + "\n")
            time.sleep(args.delay)
    print(f"完成 -> {args.out}")


if __name__ == "__main__":
    main()
