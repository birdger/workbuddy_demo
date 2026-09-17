# -*- coding: utf-8 -*-
"""
workbuddy_demo 每日推送脚本
用法：python daily_push.py ["提交说明"]
功能：git add → commit → 依次推送到 gitee / gitcode / jihulab / github
  - 国内平台强制直连（不走代理）
  - github 依次尝试：环境代理 → 常见本地代理端口 → 直连；全部失败则跳过（下次补推）
令牌已保存在 .git/config 的远程地址中，请勿将本仓库 .git 目录外传。
"""
import os
import shutil
import subprocess
import sys
import time
from datetime import date

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# 定位 git
def find_git():
    g = shutil.which("git")
    if g:
        return g
    for p in [
        r"C:\Users\Administrator\.workbuddy\binaries\PortableGit\versions\1.2.0\cmd\git.exe",
        r"C:\Users\Administrator\.workbuddy\binaries\PortableGit\versions\1.2.0\bin\git.exe",
        r"C:\Program Files\Git\cmd\git.exe",
    ]:
        if os.path.exists(p):
            return p
    raise SystemExit("找不到 git，请检查安装")

GIT = find_git()

def git(*args, proxy=None, retries=1):
    """在仓库目录执行 git 命令；proxy=None 表示强制直连，proxy='auto' 不额外配置"""
    for attempt in range(retries):
        cmd = [GIT, "-C", REPO]
        if proxy is None:
            cmd += ["-c", "http.proxy=", "-c", "https.proxy="]
        elif proxy:
            cmd += ["-c", f"http.proxy={proxy}", "-c", f"https.proxy={proxy}"]
        cmd += list(args)
        r = subprocess.run(cmd, capture_output=True, text=True, encoding="utf-8", errors="replace")
        if r.returncode == 0:
            return True, (r.stdout or "").strip()
        if attempt < retries - 1:
            time.sleep(2)
    return False, (r.stderr or r.stdout or "").strip()[-500:]

def main():
    msg = sys.argv[1] if len(sys.argv) > 1 else f"docs: 每日更新 {date.today().isoformat()}"
    os.chdir(REPO)

    ok, out = git("add", "-A")
    if not ok:
        print("git add 失败:", out); sys.exit(1)

    # 没有变更也生成一个空提交，保证每日都有 push 记录
    ok, out = git("diff", "--cached", "--quiet")
    has_changes = not ok  # returncode!=0 表示有暂存变更

    ok, out = git("commit", "-m", msg, "--allow-empty")
    if not ok:
        print("commit 失败:", out); sys.exit(1)
    print(f"[commit] {msg}" + ("" if has_changes else "（空提交，保持热度）"))

    results = {}
    # 国内平台：强制直连；gitee 额外快进 master（其默认分支）
    for remote, refs in [("gitee", ["main", "main:master"]),
                         ("gitcode", ["main"]),
                         ("jihulab", ["main"])]:
        ok, out = git("push", remote, *refs, proxy=None, retries=2)
        results[remote] = ok
        print(f"[{'OK' if ok else 'FAIL'}] {remote}" + ("" if ok else f": {out}"))

    # github：尝试各种代理
    candidates = []
    for var in ["https_proxy", "http_proxy", "HTTPS_PROXY", "HTTP_PROXY"]:
        v = os.environ.get(var)
        if v and v not in candidates:
            candidates.append(v)
    candidates += ["http://127.0.0.1:7892", "http://127.0.0.1:4556", "http://127.0.0.1:7890",
                   "http://127.0.0.1:7897", "http://127.0.0.1:10809",
                   "http://127.0.0.1:9695", None]  # None = 直连
    gh_ok = False
    for p in candidates:
        ok, out = git("push", "github", "main", proxy=p)
        if ok:
            gh_ok = True
            print(f"[OK] github（经 {p or '直连'}）")
            break
        time.sleep(1)
    if not gh_ok:
        # 兜底：扫描本机所有监听端口，找一个能通 GitHub 的代理
        print("[INFO] 常规代理均不通，扫描本机端口...")
        for p in _scan_local_proxies():
            ok, out = git("push", "github", "main", proxy=f"http://127.0.0.1:{p}")
            if ok:
                gh_ok = True
                print(f"[OK] github（经扫描到的代理 127.0.0.1:{p}）")
                break
            time.sleep(0.5)
    if not gh_ok:
        print("[SKIP] github 暂不可达（代理/网络未恢复），下次运行自动补推")
    results["github"] = gh_ok

def _scan_local_proxies():
    """枚举本机监听端口，返回经测试能访问 github 的 HTTP 代理端口列表"""
    import socket
    ports = set()
    try:
        out = subprocess.run(["netstat", "-ano"], capture_output=True, text=True,
                             encoding="gbk", errors="replace").stdout or ""
        for line in out.splitlines():
            if "LISTENING" not in line:
                continue
            try:
                addr = line.split()
                port = int(addr[1].rsplit(":", 1)[1])
                if 0 < port < 65536:
                    ports.add(port)
            except (IndexError, ValueError):
                continue
    except Exception:
        pass
    good = []
    for port in sorted(ports):
        if port in (135, 139, 445):  # 系统端口跳过
            continue
        try:
            s = socket.create_connection(("127.0.0.1", port), timeout=0.3)
            s.close()
        except OSError:
            continue
        # 用 curl 实测能否代理访问 github
        r = subprocess.run(
            ["curl", "-s", "-o", os.devnull, "-w", "%{http_code}",
             "-x", f"http://127.0.0.1:{port}", "-m", "4", "https://github.com/"],
            capture_output=True, text=True)
        if (r.stdout or "").strip() == "200":
            good.append(port)
    return good

    ok_count = sum(results.values())
    print(f"\n推送完成：{ok_count}/4 个平台成功")
    sys.exit(0 if ok_count >= 3 else 1)  # github 单独失败不算整体失败

if __name__ == "__main__":
    main()
