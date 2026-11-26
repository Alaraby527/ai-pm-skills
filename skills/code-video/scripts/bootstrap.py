#!/usr/bin/env python3
"""检查并补齐渲染依赖。

用法：
    python3 bootstrap.py            # 检查 + 自动修复
    python3 bootstrap.py --check    # 只检查，不改动
    python3 bootstrap.py --json     # 输出机器可读结果

修复策略（不依赖 Homebrew）：
    ffmpeg / ffprobe -> npm 静态二进制，落在 ~/.cache/code-video/bin
    Chrome headless  -> hyperframes browser ensure（HyperFrames）
                        Remotion 首次渲染时自行下载
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

HOME = Path.home()
CACHE = HOME / ".cache" / "code-video"
BIN = CACHE / "bin"


def run(cmd: list[str], cwd: Path | None = None, timeout: int = 600) -> tuple[int, str]:
    try:
        p = subprocess.run(
            cmd,
            cwd=str(cwd) if cwd else None,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
        return p.returncode, (p.stdout + p.stderr).strip()
    except FileNotFoundError:
        return 127, f"command not found: {cmd[0]}"
    except subprocess.TimeoutExpired:
        return 124, f"timeout: {' '.join(cmd)}"


def which(name: str) -> str | None:
    """先在 PATH 找，再在 skill 自带的 bin 目录找。"""
    found = shutil.which(name)
    if found:
        return found
    local = BIN / name
    return str(local) if local.exists() else None


def ensure_bin_dir() -> None:
    BIN.mkdir(parents=True, exist_ok=True)


def install_static_ffmpeg() -> tuple[bool, str]:
    """用 ffmpeg-static / ffprobe-static 装一份自带二进制。"""
    ensure_bin_dir()
    cache_pkg = CACHE / "package.json"
    if not cache_pkg.exists():
        cache_pkg.write_text('{"name":"code-video-runtime","private":true}\n')

    code, out = run(
        ["npm", "install", "--no-audit", "--no-fund", "ffmpeg-static", "ffprobe-static"],
        cwd=CACHE,
        timeout=900,
    )
    if code != 0:
        return False, f"npm install 失败:\n{out[-400:]}"

    # 解析真实路径（平台相关的目录结构交给 node 自己算）
    resolve = (
        "process.stdout.write([require('ffmpeg-static'),"
        "require('ffprobe-static').path].join('\\n'))"
    )
    code, out = run(["node", "-e", resolve], cwd=CACHE)
    if code != 0 or len(out.splitlines()) < 2:
        return False, f"无法解析二进制路径:\n{out[-400:]}"

    ffmpeg_src, ffprobe_src = out.splitlines()[:2]
    for name, src in (("ffmpeg", ffmpeg_src), ("ffprobe", ffprobe_src)):
        dst = BIN / name
        wrapper = f'#!/bin/sh\nexec "{src}" "$@"\n'
        dst.write_text(wrapper)
        dst.chmod(0o755)

    return True, f"已安装到 {BIN}"


def ensure_hyperframes_browser(check_only: bool) -> tuple[bool, str]:
    if check_only:
        chrome = HOME / ".cache" / "hyperframes" / "chrome"
        return chrome.exists(), "已存在" if chrome.exists() else "未下载（首次渲染会自动拉取）"
    code, out = run(["npx", "--yes", "hyperframes", "browser", "ensure"], timeout=900)
    detail = "ready" if code == 0 else "failed"
    for line in reversed([l.strip() for l in out.splitlines() if l.strip()]):
        if "Ready to render" in line or "Browser found" in line or "Download complete" in line:
            detail = line
            break
    return code == 0, detail


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--check", action="store_true", help="只检查，不安装")
    ap.add_argument("--json", action="store_true", help="输出 JSON")
    args = ap.parse_args()

    report: dict[str, object] = {"ok": True, "items": {}, "fixes": []}

    def record(key: str, status: bool, detail: str) -> None:
        report["items"][key] = {"ok": status, "detail": detail}
        if not status:
            report["ok"] = False

    # ---- Node 工具链 ----
    node = which("node")
    node_ver = ""
    if node:
        _, node_ver = run([node, "-v"])
    record("node", bool(node), node_ver or "缺失（需要 Node.js 18+）")

    npm = which("npm")
    record("npm", bool(npm), "可用" if npm else "缺失")

    toolchain_ok = bool(node and npm)

    # ---- ffmpeg / ffprobe ----
    for name in ("ffmpeg", "ffprobe"):
        found = which(name)
        if found:
            record(name, True, found)
        elif args.check:
            record(name, False, "缺失（未修复）")
        else:
            if not npm:
                record(name, False, "缺失，且没有 npm 无法自动安装")
                continue
            ok, msg = install_static_ffmpeg()
            found_after = which(name)
            record(name, ok and bool(found_after), msg if ok else msg)
            if ok:
                report["fixes"].append(f"{name} -> {found_after}")

    # ---- Chrome（HyperFrames 用；Remotion 自管）----
    if toolchain_ok:
        ok, msg = ensure_hyperframes_browser(args.check)
        record("hyperframes_chrome", ok, msg)

    # ---- 结论 ----
    if args.json:
        print(json.dumps(report, ensure_ascii=False, indent=2))
    else:
        for key, item in report["items"].items():
            mark = "✓" if item["ok"] else "✗"
            print(f"  {mark} {key:<20} {item['detail']}")
        if BIN.exists() and any(BIN.iterdir()):
            print(f"\n渲染前把下面这行加进环境：\n  export PATH=\"{BIN}:$PATH\"")
        print("\n结论：" + ("环境可用，可以出片。" if report["ok"] else "仍有缺失项，见上方提示。"))

    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
