# -*- coding: utf-8 -*-
"""
git-heatmap —— 终端版 Git 贡献热力图
用法：
    python heatmap.py                # 统计当前目录的 git 仓库，显示最近一年
    python heatmap.py /path/to/repo  # 统计指定仓库
    python heatmap.py --days 90      # 只看最近 90 天
    python heatmap.py --author 邮箱  # 只统计某位作者
零依赖，Python 3.6+，Windows / macOS / Linux 均可运行。
"""
import argparse
import datetime
import os
import subprocess
import sys
from collections import Counter

# 热力等级配色（ANSI 256 色），5 档：0 ~ 4+
LEVEL_COLORS = {0: 236, 1: 22, 2: 28, 3: 34, 4: 40}
# 无色终端退化方案
FALLBACK = {0: "·", 1: "░", 2: "▒", 3: "▓", 4: "█"}
WEEK_CN = ["一", "二", "三", "四", "五", "六", "日"]


def find_git():
    from shutil import which
    g = which("git")
    if g:
        return g
    for p in (r"C:\Program Files\Git\cmd\git.exe",
              r"C:\Program Files (x86)\Git\cmd\git.exe"):
        if os.path.exists(p):
            return p
    sys.exit("错误：找不到 git，请确认已安装")


def load_commits(repo, author=None):
    """返回 {date: 提交次数}"""
    cmd = [find_git(), "-C", repo, "log", "--pretty=format:%ad|%ae",
           "--date=format:%Y-%m-%d"]
    if author:
        cmd += ["--author", author]
    try:
        out = subprocess.run(cmd, capture_output=True, text=True,
                             encoding="utf-8", errors="replace").stdout
    except Exception as e:
        sys.exit(f"读取 git 日志失败：{e}")
    counter = Counter()
    for line in out.splitlines():
        if "|" in line:
            d, _ = line.split("|", 1)
            counter[d.strip()] += 1
    return counter


def level(n):
    if n == 0:
        return 0
    if n <= 2:
        return 1
    if n <= 4:
        return 2
    if n <= 6:
        return 3
    return 4


def render(counter, days):
    today = datetime.date.today()
    start = today - datetime.timedelta(days=days - 1)
    # 对齐到周一
    start -= datetime.timedelta(days=start.weekday())

    weeks = []
    d = start
    while d <= today:
        week = []
        for _ in range(7):
            if d > today:
                week.append(None)
            else:
                week.append(counter.get(d.isoformat(), 0))
            d += datetime.timedelta(days=1)
        weeks.append(week)

    def color(text, code, use_color):
        if not use_color:
            return text
        return f"\033[48;5;{code}m{text}\033[0m"

    use_color = sys.stdout.isatty() or os.environ.get("FORCE_COLOR")
    cell = "  " if use_color else FALLBACK  # 彩色模式画空格，纯文本用字符

    lines = []
    # 月份标尺
    months, last_m = [], -1
    for w in weeks:
        m = w[0] if w[0] is not None else 0
        d0 = start + datetime.timedelta(days=7 * len(months))
        if d0.month != last_m:
            months.append(f"{d0.month}月".ljust(5 if use_color else 14))
            last_m = d0.month
        else:
            months.append(" " * (5 if use_color else 14))
    lines.append("     " + "".join(months).rstrip())

    for row in range(7):
        line = f" {WEEK_CN[row]}  "
        for w in weeks:
            n = w[row]
            if n is None:
                line += "  " if use_color else " "
            else:
                lv = level(n)
                line += color(cell[lv] if not use_color else cell,
                              LEVEL_COLORS[lv], use_color) + ("" if not use_color else "")
                if not use_color:
                    pass
            if not use_color:
                line += ""
        lines.append(line.rstrip())

    total = sum(counter.values())
    active = sum(1 for v in counter.values() if v)
    span_days = days
    lines.append("")
    lines.append(f"  总提交 {total} 次 | 活跃天数 {active} 天 | "
                 f"统计区间 {start} ~ {today}（{span_days} 天）")
    # 图例
    legend = "  少 " + "".join(
        color("  " if use_color else FALLBACK[i], LEVEL_COLORS[i], use_color)
        for i in range(5)) + " 多"
    lines.append(legend)
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser(description="终端版 Git 贡献热力图")
    ap.add_argument("repo", nargs="?", default=".", help="git 仓库路径（默认当前目录）")
    ap.add_argument("--days", type=int, default=365, help="统计天数（默认 365）")
    ap.add_argument("--author", help="只统计指定作者（姓名或邮箱）")
    args = ap.parse_args()

    repo = os.path.abspath(args.repo)
    if not os.path.isdir(os.path.join(repo, ".git")):
        sys.exit(f"错误：{repo} 不是 git 仓库")

    counter = load_commits(repo, args.author)
    print(render(counter, args.days))


if __name__ == "__main__":
    main()
