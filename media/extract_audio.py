#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
从视频中提取音频（基于 FFmpeg）

两种策略
--------
- ``copy``：``-acodec copy`` 直接复制原始音频流，**不重新编码**，快且无损，
  但输出编码随源文件（常见 mp4 -> aac/m4a）
- ``mp3`` ：重编码为 MP3（``-q:a 0`` 最高音质），通用性最好，代价是耗时、有损

用法
----
    python extract_audio.py <视频> [输出] --mode copy|mp3

省略「输出」时，自动在源文件同目录生成同名 .aac / .mp3。
"""
from __future__ import annotations

import argparse
import os
import subprocess


def extract(video: str, output: str, mode: str) -> None:
    if mode == "copy":
        codec = ["-vn", "-acodec", "copy"]
    else:                                         # mp3
        codec = ["-vn", "-q:a", "0", "-map", "a"]
    cmd = ["ffmpeg", "-y", "-hide_banner", "-loglevel", "error", "-i", video, *codec, output]
    subprocess.run(cmd, check=True)
    print(f"已提取音频: {output}")


def main() -> None:
    ap = argparse.ArgumentParser(description="从视频提取音频")
    ap.add_argument("video", help="输入视频文件")
    ap.add_argument("output", nargs="?", help="输出音频文件（可省略）")
    ap.add_argument("--mode", choices=["copy", "mp3"], default="copy",
                    help="copy=直接复制音频流(快/无损)；mp3=重编码为MP3")
    args = ap.parse_args()

    if args.output:
        output = args.output
    else:
        stem = os.path.splitext(args.video)[0]
        output = stem + (".aac" if args.mode == "copy" else ".mp3")
    extract(args.video, output, args.mode)


if __name__ == "__main__":
    main()
