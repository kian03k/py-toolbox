#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""检测本机是否安装 FFmpeg，未安装时按平台打印安装指引。"""
from __future__ import annotations

import platform
import subprocess

INSTALL_HINTS = {
    "Windows": (
        "1. 到 https://www.gyan.dev/ffmpeg/builds/ 下载预编译包\n"
        "2. 解压后把其中 bin 目录加入系统 PATH 环境变量\n"
        "3. 重开命令行，运行 ffmpeg -version 验证"
    ),
    "Darwin": "brew install ffmpeg",
    "Linux": "sudo apt install ffmpeg   # Debian/Ubuntu；Fedora 用 dnf，Arch 用 pacman",
}


def check() -> bool:
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE,
                       stderr=subprocess.PIPE, check=True)
        print("FFmpeg 已安装 ✓")
        return True
    except (OSError, subprocess.CalledProcessError):
        # OSError 覆盖 FileNotFoundError(没装) 与 PermissionError(不可执行) 等情况
        print("FFmpeg 未安装或不可用。安装指引：")
        print(INSTALL_HINTS.get(platform.system(), "请参考 https://ffmpeg.org/download.html"))
        return False


if __name__ == "__main__":
    check()
