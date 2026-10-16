#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
视频掐头去尾（基于 FFmpeg，无损裁剪）

用途
----
删掉视频开头 / 结尾的若干秒，不重新编码（``-c copy``），速度快、几乎无画质损失。
常见于：去掉片头片尾、掐掉多余片段。

要点
----
- 先 ``ffprobe`` 读总时长，再换算裁剪区间
- ``-c copy`` 无损，但受关键帧对齐影响，开头可能残留少量画面；
  额外加 ``-fflags +genpts`` 重写时间戳，避免播放器时间轴错乱
- 需要"帧精确"剪辑时应去掉 ``-c copy`` 改为重编码（慢、有损）

依赖
----
- FFmpeg / ffprobe

用法
----
    python video_trim.py <输入> <输出> --start 5 --end 10

``--start`` / ``--end`` 分别表示「开头删掉」和「结尾删掉」的秒数。
"""
from __future__ import annotations

import argparse
import subprocess


def probe_duration(path: str) -> float:
    """用 ffprobe 读取媒体总时长（秒）。"""
    cmd = ["ffprobe", "-i", path, "-show_entries", "format=duration",
           "-v", "quiet", "-of", "csv=p=0"]
    out = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return float(out.stdout.strip())


def trim(input_file: str, output_file: str, start: float = 0.0, end: float = 0.0) -> None:
    total = probe_duration(input_file)
    stop = total - end
    if start >= stop:
        print(f"裁剪区间无效：start={start}s 已超出视频长度 {total:.2f}s")
        return
    cmd = [
        "ffmpeg", "-y", "-hide_banner", "-loglevel", "error",
        "-i", input_file, "-ss", str(start), "-to", str(stop),
        "-c", "copy", "-fflags", "+genpts",      # 无损 + 修复时间戳
        output_file,
    ]
    subprocess.run(cmd, check=True)
    print(f"完成：{input_file} -> {output_file}（保留 {start:.2f}s ~ {stop:.2f}s）")


def main() -> None:
    ap = argparse.ArgumentParser(description="视频掐头去尾（FFmpeg 无损）")
    ap.add_argument("input", help="输入视频")
    ap.add_argument("output", help="输出视频")
    ap.add_argument("--start", type=float, default=0.0, help="开头删除秒数")
    ap.add_argument("--end", type=float, default=0.0, help="结尾删除秒数")
    args = ap.parse_args()
    trim(args.input, args.output, args.start, args.end)


if __name__ == "__main__":
    main()
