#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
统计目录下每个子项占用的体积，降序输出（自动 B/KB/MB/GB）

用途
----
快速找出"谁最占地方"，磁盘清理 / 仓库瘦身时反复要用。

用法
----
    python dir_size.py <目录>
"""
from __future__ import annotations

import argparse
import os
import sys


def dir_size(path: str) -> int:
    """递归累计目录下所有文件字节数，无法访问的文件跳过。"""
    total = 0
    for parent, _dirs, files in os.walk(path):
        for name in files:
            try:
                total += os.path.getsize(os.path.join(parent, name))
            except OSError:
                continue
    return total


def human(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB"):
        if n < 1024:
            return f"{n:.1f}{unit}"
        n /= 1024
    return f"{n:.1f}PB"


def main() -> None:
    ap = argparse.ArgumentParser(description="列出目录内各子项体积（降序）")
    ap.add_argument("path", help="要分析的目录")
    args = ap.parse_args()

    root = args.path
    if not os.path.isdir(root):
        sys.exit(f"目录不存在: {root}")

    entries = []
    for name in os.listdir(root):
        full = os.path.join(root, name)
        entries.append((name, dir_size(full) if os.path.isdir(full) else os.path.getsize(full)))
    entries.sort(key=lambda x: x[1], reverse=True)

    print(f"{root} 共 {len(entries)} 项：")
    for name, size in entries:
        print(f"{human(size):>10}  {name}")


if __name__ == "__main__":
    main()
