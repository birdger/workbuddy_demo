#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
dirsize —— 终端目录体积分析器（dust 的零依赖 Python 精简版）

用法：
    python dirsize.py [路径] [-n 显示条数] [-d 递归深度] [--files] [--reverse]

示例：
    python dirsize.py                 # 分析当前目录
    python dirsize.py G:/code -n 15   # 显示最大的 15 个子项
    python dirsize.py . -d 2          # 递归展示到第 2 层
    python dirsize.py . --files       # 文件也参与排序（默认只排目录）

特点：纯标准库、单文件、Windows/Linux/macOS 通吃。
灵感来源：https://github.com/bootandy/dust
"""

import argparse
import os
import sys

BAR_WIDTH = 28
BLOCK = "█"


def human_size(n: float) -> str:
    """字节数转人类可读格式。"""
    for unit in ("B", "K", "M", "G", "T", "P"):
        if n < 1024 or unit == "P":
            return f"{n:.1f}{unit}" if unit != "B" else f"{int(n)}B"
        n /= 1024
    return f"{n:.1f}P"


def dir_size(path: str) -> int:
    """递归累加目录大小，出错（权限等）静默跳过。"""
    total = 0
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_file():
                        total += entry.stat().st_size
                    elif entry.is_dir():
                        total += dir_size(entry.path)
                except OSError:
                    continue
    except OSError:
        pass
    return total


def scan(path: str, include_files: bool):
    """扫描 path 的直接子项，返回 [(名称, 大小, 是否目录), ...] 按大小降序。"""
    items = []
    try:
        with os.scandir(path) as it:
            for entry in it:
                try:
                    if entry.is_symlink():
                        continue
                    if entry.is_dir():
                        items.append((entry.name, dir_size(entry.path), True))
                    elif include_files and entry.is_file():
                        items.append((entry.name, entry.stat().st_size, False))
                except OSError:
                    continue
    except OSError as e:
        print(f"无法读取 {path}: {e}", file=sys.stderr)
    items.sort(key=lambda x: x[1], reverse=True)
    return items


def print_tree(path: str, depth: int, top_n: int, include_files: bool,
               prefix: str = "", root_total: int = None):
    """以树形 + 条形图打印目录体积。"""
    items = scan(path, include_files)
    if root_total is None:
        root_total = sum(s for _, s, _ in items) or 1

    shown = items[:top_n]
    rest = items[top_n:]
    rows = list(shown)
    if rest:
        rows.append((f"（其余 {len(rest)} 项）", sum(s for _, s, _ in rest), None))

    for i, (name, size, is_dir) in enumerate(rows):
        last = i == len(rows) - 1
        connector = "└── " if last else "├── "
        pct = size / root_total * 100
        bar_len = max(1, round(size / root_total * BAR_WIDTH)) if size else 0
        bar = BLOCK * bar_len
        label = f"{name}/" if is_dir else name
        print(f"{prefix}{connector}{bar:<{BAR_WIDTH}} {pct:5.1f}% {human_size(size):>8}  {label}")
        if is_dir and depth > 1:
            extension = "    " if last else "│   "
            print_tree(os.path.join(path, name), depth - 1, top_n,
                       include_files, prefix + extension, root_total)


def main():
    ap = argparse.ArgumentParser(description="终端目录体积分析器（dust 精简版）")
    ap.add_argument("path", nargs="?", default=".", help="要分析的目录（默认当前目录）")
    ap.add_argument("-n", "--number", type=int, default=10, help="每层显示的最大子项数（默认 10）")
    ap.add_argument("-d", "--depth", type=int, default=1, help="递归展示深度（默认 1）")
    ap.add_argument("--files", action="store_true", help="文件也参与排序")
    args = ap.parse_args()

    root = os.path.abspath(args.path)
    if not os.path.isdir(root):
        print(f"错误：{root} 不是目录", file=sys.stderr)
        sys.exit(1)

    print(f"\n📦 {root}\n")
    print_tree(root, args.depth, args.number, args.files)
    print()


if __name__ == "__main__":
    main()
