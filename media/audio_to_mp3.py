#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
批量音频转 MP3（基于 FFmpeg）

用途
----
把一个目录（含子目录）里的所有音频统一转成 MP3，其余非音频文件原样复制到
另一个目录。适合整理音乐库、播客、录音。

特性
----
- 保留原子目录结构
- 已是 MP3 的文件直接复制，不重新编码
- 先用 ``unsure_xxx.mp3`` 临时文件承接转换结果，成功后再改名，
  中途中断不会留下"半成品 MP3"
- 多线程并行（默认 8，可调）
- 目标文件已存在则跳过，重复跑不会重复转换

依赖
----
- 系统需安装 FFmpeg（命令行能跑通 ``ffmpeg -version``）

用法
----
    python audio_to_mp3.py <源目录> <MP3输出目录> <其它文件输出目录> [-j 线程数]

示例::

    python audio_to_mp3.py "D:/music/raw" "D:/music/mp3" "D:/music/others" -j 8
"""
from __future__ import annotations

import argparse
import concurrent.futures
import logging
import shutil
import subprocess
from pathlib import Path

# 视为音频的扩展名（统一小写比较）
AUDIO_EXTENSIONS = {".flac", ".ogg", ".wav", ".aac", ".m4a", ".wma", ".ape", ".alac", ".mp3"}


def convert_one(src: Path, src_root: Path, dst_audio: Path, dst_other: Path) -> None:
    """处理单个文件：音频 -> 转/复制 MP3；其它 -> 复制到另一目录。"""
    try:
        rel = src.relative_to(src_root)          # 保留相对目录结构
        ext = src.suffix.lower()

        if ext not in AUDIO_EXTENSIONS:          # 非音频 -> 直接复制
            out = dst_other / rel
            out.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, out)
            logging.info("复制非音频: %s", rel)
            return

        out = (dst_audio / rel).with_suffix(".mp3")
        if out.exists():                         # 已转好 -> 跳过
            logging.info("已存在，跳过: %s", out)
            return
        out.parent.mkdir(parents=True, exist_ok=True)

        if ext == ".mp3":                        # 本身是 MP3 -> 复制
            shutil.copy2(src, out)
            logging.info("复制 MP3: %s", rel)
            return

        # 非 MP3 音频 -> FFmpeg 转码；先写临时文件，成功后再改名
        tmp = out.parent / f"unsure_{out.name}"
        cmd = [
            "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
            "-i", str(src), "-codec:a", "libmp3lame", "-b:a", "320k", str(tmp),
        ]
        r = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        if r.returncode != 0:
            logging.error("转换失败 %s: %s", src, r.stderr.decode(errors="ignore").strip())
            tmp.unlink(missing_ok=True)
            return
        tmp.rename(out)
        logging.info("转换完成: %s", rel)
    except Exception as e:                       # 单个文件失败不影响整体
        logging.error("处理 %s 出错: %s", src, e)


def main() -> None:
    ap = argparse.ArgumentParser(description="批量音频转 MP3（FFmpeg）")
    ap.add_argument("src", help="源目录（会递归）")
    ap.add_argument("dst_audio", help="MP3 输出目录")
    ap.add_argument("dst_other", help="非音频文件输出目录")
    ap.add_argument("-j", "--threads", type=int, default=8, help="并行线程数（默认 8）")
    args = ap.parse_args()

    src_root = Path(args.src)
    dst_audio, dst_other = Path(args.dst_audio), Path(args.dst_other)
    if not src_root.is_dir():
        logging.error("源目录不存在: %s", src_root)
        return
    dst_audio.mkdir(parents=True, exist_ok=True)
    dst_other.mkdir(parents=True, exist_ok=True)

    files = [f for f in src_root.rglob("*") if f.is_file()]
    logging.info("源目录共 %d 个文件", len(files))
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.threads) as pool:
        futures = [pool.submit(convert_one, f, src_root, dst_audio, dst_other) for f in files]
        concurrent.futures.wait(futures)
    logging.info("全部完成")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
    main()
