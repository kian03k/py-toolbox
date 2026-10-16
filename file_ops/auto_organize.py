#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文件夹自动整理：按体积排序重命名 + 逐字节去重 + 可选常驻监听

用途
----
把一堆乱序命名的文件（例如爬下来的一批图片）统一重命名为 ``前缀+序号``，
删掉内容完全相同的重复文件；加 ``--watch`` 后常驻监听，新文件一进来就自动处理。

三段能力
--------
1. ``sort_by_size``   ：按文件大小升序改名
2. ``find_duplicates`` ：先按大小排序，只和相邻文件做 ``filecmp`` 逐字节比对（省 IO）
3. ``watch``          ：基于 ``watchdog`` 监听目录，命中新建文件时重跑 1、2

依赖
----
    pip install watchdog      # 仅 --watch 模式需要

用法
----
    python auto_organize.py <目录> --prefix img_ --start 1 [--ext .jpg] [--watch]
"""
from __future__ import annotations

import argparse
import filecmp
import os
import time
from typing import Optional

try:
    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer
except ImportError:                              # watchdog 仅监听模式需要
    Observer = None


def sort_by_size(folder: str, prefix: str, start: int, ext: Optional[str] = None) -> int:
    """按文件大小升序，把文件重命名为 ``prefix + 序号 + 扩展名``，返回处理数。"""
    items = []
    for name in os.listdir(folder):
        p = os.path.join(folder, name)
        if os.path.isfile(p):
            items.append((p, os.path.getsize(p)))
    items.sort(key=lambda x: x[1])

    i = start
    for old, _ in items:
        suffix = ext or os.path.splitext(old)[1]
        new = os.path.join(folder, f"{prefix}{i}{suffix}")
        while os.path.exists(new):               # 防撞名
            i += 1
            new = os.path.join(folder, f"{prefix}{i}{suffix}")
        os.rename(old, new)
        i += 1
    print(f"已按大小排序重命名 {len(items)} 个文件")
    return len(items)


def find_duplicates(folder: str) -> list[str]:
    """返回重复文件路径列表（保留每个重复组里先出现的一个，其余视为重复）。"""
    names = [f for f in os.listdir(folder) if os.path.isfile(os.path.join(folder, f))]
    names.sort(key=lambda f: os.path.getsize(os.path.join(folder, f)))
    dups = []
    for a, b in zip(names, names[1:]):
        pa, pb = os.path.join(folder, a), os.path.join(folder, b)
        try:
            if filecmp.cmp(pa, pb, shallow=False):   # shallow=False = 真比内容
                dups.append(pb)
        except OSError:
            continue
    return dups


def remove_duplicates(paths: list[str]) -> None:
    for p in paths:
        os.remove(p)
        print(f"删除重复: {os.path.basename(p)}")


def run_once(folder: str, prefix: str, start: int, ext: Optional[str]) -> None:
    sort_by_size(folder, prefix, start, ext)
    dups = find_duplicates(folder)
    if dups:
        remove_duplicates(dups)
    else:
        print("没有发现重复文件")


def watch(folder: str, prefix: str, start: int, ext: Optional[str]) -> None:
    """常驻监听，新增文件后自动执行排序+去重。Ctrl+C 退出。"""
    if Observer is None:
        raise SystemExit("需要 watchdog：pip install watchdog")

    class Handler(FileSystemEventHandler):
        def on_created(self, event):
            if not event.is_directory:
                print(f"检测到新文件: {event.src_path}")
                run_once(folder, prefix, start, ext)

    obs = Observer()
    obs.schedule(Handler(), folder, recursive=True)
    obs.start()
    print(f"开始监听 {folder}（Ctrl+C 退出）...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        obs.stop()
    obs.join()


def main() -> None:
    ap = argparse.ArgumentParser(description="文件夹自动整理（重命名 + 去重 + 监听）")
    ap.add_argument("folder", help="目标目录")
    ap.add_argument("--prefix", default="img_", help="重命名前缀（默认 img_）")
    ap.add_argument("--start", type=int, default=1, help="起始序号（默认 1）")
    ap.add_argument("--ext", default=None, help="强制统一扩展名，如 .jpg")
    ap.add_argument("--watch", action="store_true", help="常驻监听新文件")
    args = ap.parse_args()

    if not os.path.isdir(args.folder):
        raise SystemExit(f"目录不存在: {args.folder}")
    run_once(args.folder, args.prefix, args.start, args.ext)
    if args.watch:
        watch(args.folder, args.prefix, args.start, args.ext)


if __name__ == "__main__":
    main()
