#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV 列重排 / 值映射（数据集预处理）

用途
----
读入一个 CSV，按需交换两列的顺序，并把某一列的取值按映射表替换
（例如把标签 1/0 换成「正面/负面」），输出到新文件。

用法
----
    python csv_relabel.py <输入.csv> <输出.csv> [--swap 0,1] [--map-col 1 --map 1=正面,0=负面]

- ``--swap a,b``    交换第 a、b 列（下标从 0 开始）
- ``--map-col n``   指定要替换取值的列
- ``--map k=v,...`` 取值映射表
- ``--encoding``    文件编码（默认 utf-8；中文 Windows 导出常为 gbk）

注意：处理顺序是**先 swap 后 map**，``--map-col`` 针对的是交换之后的列位置。
"""
from __future__ import annotations

import argparse
import csv


def parse_swap(text: str) -> tuple[int, int]:
    a, b = text.split(",")
    return int(a), int(b)


def parse_map(text: str) -> dict[str, str]:
    mapping = {}
    for pair in text.split(","):
        k, v = pair.split("=", 1)
        mapping[k] = v
    return mapping


def main() -> None:
    ap = argparse.ArgumentParser(description="CSV 列重排 / 值映射")
    ap.add_argument("src", help="输入 CSV")
    ap.add_argument("dst", help="输出 CSV")
    ap.add_argument("--swap", help="交换两列，如 0,1")
    ap.add_argument("--map-col", type=int, help="要替换取值的列号")
    ap.add_argument("--map", dest="mapping", help="取值映射，如 1=正面,0=负面")
    ap.add_argument("--encoding", default="utf-8", help="文件编码（默认 utf-8）")
    args = ap.parse_args()

    with open(args.src, newline="", encoding=args.encoding) as f:
        rows = list(csv.reader(f))

    if args.swap:
        a, b = parse_swap(args.swap)
        for row in rows:
            if len(row) > max(a, b):
                row[a], row[b] = row[b], row[a]

    if args.map_col is not None and args.mapping:
        mapping = parse_map(args.mapping)
        for row in rows:
            if len(row) > args.map_col and row[args.map_col] in mapping:
                row[args.map_col] = mapping[row[args.map_col]]

    with open(args.dst, "w", newline="", encoding=args.encoding) as f:
        csv.writer(f).writerows(rows)
    print(f"完成：{args.src} -> {args.dst}（{len(rows)} 行）")


if __name__ == "__main__":
    main()
