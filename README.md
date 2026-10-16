# py-toolbox

日常自用的一小撮 Python 脚本，按用途分组。每个脚本都做成了命令行工具，
带 `-h` 帮助，路径/参数不再硬编码。

> 定位：**能复用、非平凡**的实用脚本。像"批量重命名"这种几行就能写的东西不收，
> 相关技巧整理在笔记里。

## 目录

```
py-toolbox/
├── media/        # 音视频（依赖 FFmpeg）
│   ├── audio_to_mp3.py   批量音频转 MP3（多线程、保留目录结构、临时文件防半成品）
│   ├── video_trim.py     视频掐头去尾（-c copy 无损 + 修复时间戳）
│   ├── extract_audio.py  从视频提取音频（原样复制 / 重编码 MP3 两种策略）
│   └── ffmpeg_check.py   检测 FFmpeg 是否安装并给安装指引
├── file_ops/     # 文件批处理
│   ├── auto_organize.py  按体积排序重命名 + 逐字节去重 + watchdog 常驻监听
│   └── dir_size.py       统计目录内各子项体积（降序，自动单位）
├── data/         # 数据处理
│   └── csv_relabel.py    CSV 列交换 + 取值映射（数据集预处理）
└── spider/       # 网页抓取
    ├── bing_images.py    按关键词抓取 Bing 图片
    └── text_series.py    连载页面正文批量抓取拼接
```

## 依赖

- Python 3.8+
- FFmpeg（`media/` 下四个脚本需要，先跑 `python media/ffmpeg_check.py` 自检）
- 第三方库：

```bash
pip install -r requirements.txt
```

## 用法速查

```bash
# 批量音频转 MP3
python media/audio_to_mp3.py ./raw ./mp3 ./others -j 8

# 视频掐头去尾：删掉开头 5 秒、结尾 10 秒
python media/video_trim.py in.mp4 out.mp4 --start 5 --end 10

# 提取音频（原样复制，快）
python media/extract_audio.py in.mp4 --mode copy

# 文件夹整理 + 常驻监听
python file_ops/auto_organize.py ./images --prefix img_ --watch

# 看看哪个目录最占地方
python file_ops/dir_size.py .

# CSV：交换前两列，并把第 2 列的 1/0 换成 正面/负面
python data/csv_relabel.py in.csv out.csv --swap 0,1 --map-col 1 --map 1=正面,0=负面

# 抓图片 / 抓连载文本
python spider/bing_images.py "关键词" ./out --pages 2
python spider/text_series.py --url-template "https://example.com/post_{n}.html" --start 1 --end 30
```

## 说明

- 脚本均为「单文件、可直接运行」，不做包化，方便随取随用。
- `spider/` 下的脚本请遵守目标站点的 robots 与版权规定，控制抓取频率。
