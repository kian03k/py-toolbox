#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
按关键词抓取 Bing 图片（requests + BeautifulSoup）

用途
----
给数据集补图：输入关键词，抓取 Bing 图片搜索结果里的图片并保存到本地。

依赖
----
    pip install requests beautifulsoup4

用法
----
    python bing_images.py "关键词" <保存目录> [--pages 1]

说明
----
- 抓取结果页里 <img> 的直链；Bing 有懒加载，翻页靠 ``first`` 参数
- 抓取行为请遵守目标站点条款与图片版权
"""
from __future__ import annotations

import argparse
import os

import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                   "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")
}


def download_images(url: str, save_folder: str) -> int:
    resp = requests.get(url, headers=HEADERS, timeout=15)
    soup = BeautifulSoup(resp.text, "html.parser")
    os.makedirs(save_folder, exist_ok=True)

    count = 0
    for img in soup.find_all("img"):
        img_url = img.get("src") or ""
        if not img_url:
            continue
        if not img_url.startswith("http"):            # 相对路径补全
            img_url = "https://cn.bing.com" + img_url
        try:
            data = requests.get(img_url, headers=HEADERS, timeout=15).content
        except requests.RequestException:
            continue
        with open(os.path.join(save_folder, f"image_{count}.jpg"), "wb") as f:
            f.write(data)
        count += 1
    return count


def main() -> None:
    ap = argparse.ArgumentParser(description="按关键词抓取 Bing 图片")
    ap.add_argument("keyword", help="搜索关键词")
    ap.add_argument("outdir", help="保存目录")
    ap.add_argument("--pages", type=int, default=1, help="抓取页数（默认 1）")
    args = ap.parse_args()

    total = 0
    for p in range(args.pages):
        url = (f"https://cn.bing.com/images/search?q={args.keyword}"
               f"&form=HDRSC2&first={p + 1}")
        total += download_images(url, args.outdir)
    print(f"共保存 {total} 张图片到 {args.outdir}")


if __name__ == "__main__":
    main()
