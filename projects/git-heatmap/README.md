# git-heatmap —— 终端版 Git 贡献热力图

在终端里用 GitHub 风格的热力图展示任意 git 仓库的提交活跃度。**单文件、零依赖**，Python 3.6+ 开箱即用。

## 效果预览

```text
     7月                          8月                                                                    9月
 一  ·········
 二  ·········
 三  ·········
 四  ········▓
 五  ········
 六  ········
 日  ········

  总提交 5 次 | 活跃天数 1 天 | 统计区间 2026-07-20 ~ 2026-09-17（60 天）
  少 ·░▒▓█ 多
```

在支持 ANSI 256 色的终端里会渲染成绿->深绿的色块，和 GitHub 个人主页的贡献图一个味道。

## 用法

```bash
python heatmap.py                    # 当前仓库，最近一年
python heatmap.py /path/to/repo      # 指定仓库
python heatmap.py --days 90          # 最近 90 天
python heatmap.py --author me@x.com  # 只统计某位作者（姓名或邮箱）
```

## 特性

- **零依赖**：只用 Python 标准库，不需要 `pip install` 任何东西
- **跨平台**：Windows / macOS / Linux 通用；管道输出时自动降级为字符模式（`·░▒▓█`）
- **彩色渲染**：TTY 下自动启用 ANSI 256 色色阶，5 档热度
- **作者过滤**：多人协作仓库里只看自己的提交
- **统计摘要**：总提交数、活跃天数、统计区间一目了然

## 实现原理

1. `git log --pretty=format:%ad --date=format:%Y-%m-%d` 取出每天的提交日期
2. 按 `Counter` 聚合出「日期 -> 提交次数」映射
3. 以周一为起点切分成周列，映射到 5 档热度色阶
4. TTY 检测决定彩色 / 字符两种渲染模式

整个核心逻辑不到 200 行，适合作为 Python 标准库综合运用的小例子（`argparse` / `subprocess` / `datetime` / `collections`）。

## License

MIT
