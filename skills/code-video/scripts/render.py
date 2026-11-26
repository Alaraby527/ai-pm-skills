#!/usr/bin/env python3
"""统一出片入口：自动识别 HyperFrames / Remotion 工程，渲染并校验产物。

用法：
    python3 render.py <项目目录>                       # 默认 draft 质量
    python3 render.py <项目目录> -q delivery
    python3 render.py <项目目录> --start 0 --end 10     # 只出前 10 秒样片
    python3 render.py <项目目录> --stills 1.5,6.5,10.5  # 同时抽关键帧供肉眼验收

脚本自己会把 ffmpeg/ffprobe 的缓存目录加进 PATH，调用方无需先 export。
"""

from __future__ import annotations

import argparse
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

CACHE_BIN = Path.home() / ".cache" / "code-video" / "bin"
CRF = {"draft": 28, "looks": 20, "delivery": 16}


def prepend_path() -> None:
    if CACHE_BIN.exists():
        os.environ["PATH"] = f"{CACHE_BIN}{os.pathsep}" + os.environ.get("PATH", "")


def which(name: str) -> str | None:
    found = shutil.which(name)
    if found:
        return found
    local = CACHE_BIN / name
    return str(local) if local.exists() else None


def detect_stack(proj: Path) -> str:
    if (proj / "hyperframes.json").exists():
        return "hyperframes"
    index = proj / "index.html"
    if index.exists() and "data-composition-id" in index.read_text(errors="ignore"):
        return "hyperframes"
    if (proj / "remotion.config.ts").exists() or (proj / "src" / "Root.tsx").exists():
        return "remotion"
    pkg = proj / "package.json"
    if pkg.exists() and '"remotion"' in pkg.read_text(errors="ignore"):
        return "remotion"
    raise SystemExit(f"无法识别工程类型：{proj}\n需要 hyperframes.json / data-composition-id 或 remotion.config.ts")


def hyperframes_pin(proj: Path) -> str:
    """优先复用工程里 pin 住的版本，避免每次渲染都去解析 latest。"""
    pkg = proj / "package.json"
    if pkg.exists():
        txt = pkg.read_text(errors="ignore")
        marker = "hyperframes@"
        if marker in txt:
            tail = txt.split(marker, 1)[1]
            ver = ""
            for ch in tail:
                if ch.isdigit() or ch == ".":
                    ver += ch
                else:
                    break
            if ver:
                return f"hyperframes@{ver}"
    return "hyperframes"


def remotion_entry(proj: Path) -> Path:
    for rel in ("src/index.ts", "src/index.tsx", "src/index.js", "index.ts"):
        if (proj / rel).exists():
            return proj / rel
    raise SystemExit("找不到 Remotion 入口文件（src/index.ts）")


def composition_id(proj: Path) -> str:
    root = proj / "src" / "Root.tsx"
    if root.exists():
        txt = root.read_text(errors="ignore")
        if 'id="' in txt:
            return txt.split('id="', 1)[1].split('"', 1)[0]
        if "id='" in txt:
            return txt.split("id='", 1)[1].split("'", 1)[0]
    return "Main"


def build_cmd(args, proj: Path, out: Path) -> list[str]:
    if args.stack == "hyperframes":
        npx = which("npx") or "npx"
        cmd = [
            npx, "--yes", hyperframes_pin(proj), "render", str(proj),
            "-o", str(out),
            "-q", args.quality,
        ]
        if args.fps:
            cmd += ["-f", str(args.fps)]
        if args.start is not None:
            cmd += ["--start", str(args.start)]
        if args.end is not None:
            cmd += ["--end", str(args.end)]
        if args.workers:
            cmd += ["-w", str(args.workers)]
        return cmd

    npx = which("npx") or "npx"
    cmd = [
        npx, "remotion", "render",
        str(remotion_entry(proj)),
        args.id or composition_id(proj),
        str(out),
        f"--crf={CRF.get(args.quality, 24)}",
    ]
    if args.fps:
        cmd += ["--fps", str(args.fps)]
    if args.start is not None or args.end is not None:
        # Remotion 的区间是帧，且必须自己换算
        fps = args.fps or 30
        s = int((args.start or 0) * fps)
        e = int(args.end * fps) if args.end is not None else None
        cmd += [f"--frames={s}-{e}" if e else f"--frames={s}-"]
    if args.workers:
        cmd += [f"--concurrency={args.workers}"]
    return cmd


def probe(path: Path) -> dict:
    ffprobe = which("ffprobe")
    if not ffprobe:
        return {"ok": False, "error": "ffprobe 不可用，先跑 bootstrap.py"}
    code = subprocess.run(
        [
            ffprobe, "-v", "error", "-show_entries",
            "format=duration,size:stream=width,height,r_frame_rate,codec_name",
            "-of", "json", str(path),
        ],
        capture_output=True, text=True,
    )
    if code.returncode != 0:
        return {"ok": False, "error": (code.stderr or "").strip()[:300]}
    data = json.loads(code.stdout or "{}")
    streams = data.get("streams") or [{}]
    fmt = data.get("format") or {}
    v = streams[0]
    return {
        "ok": True,
        "path": str(path),
        "duration_s": round(float(fmt.get("duration", 0)), 3),
        "size_mb": round(float(fmt.get("size", 0)) / 1e6, 2),
        "width": v.get("width"),
        "height": v.get("height"),
        "fps": v.get("r_frame_rate"),
        "codec": v.get("codec_name"),
    }


def grab_stills(video: Path, times: list[float], outdir: Path) -> list[str]:
    ffmpeg = which("ffmpeg")
    if not ffmpeg:
        return []
    outdir.mkdir(parents=True, exist_ok=True)
    made = []
    for t in times:
        dst = outdir / f"still_{t:g}s.png"
        subprocess.run(
            [ffmpeg, "-v", "error", "-ss", str(t), "-i", str(video),
             "-frames:v", "1", "-y", str(dst)],
            capture_output=True, text=True,
        )
        if dst.exists():
            made.append(str(dst))
    return made


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("project", help="工程目录")
    ap.add_argument("--stack", choices=["auto", "hyperframes", "remotion"], default="auto")
    ap.add_argument("-o", "--out", help="输出文件路径")
    ap.add_argument("-q", "--quality", choices=["draft", "looks", "delivery"], default="draft")
    ap.add_argument("--fps", type=int)
    ap.add_argument("--start", type=float, help="起始秒，做样片用")
    ap.add_argument("--end", type=float, help="结束秒")
    ap.add_argument("--stills", help="逗号分隔的时间点，抽帧供肉眼验收")
    ap.add_argument("--id", help="Remotion composition id")
    ap.add_argument("--workers", type=int, help="并行 worker 数")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()

    prepend_path()
    proj = Path(args.project).expanduser().resolve()
    if not proj.is_dir():
        raise SystemExit(f"目录不存在：{proj}")
    if not which("ffmpeg"):
        raise SystemExit("缺 ffmpeg / ffprobe，先运行：python3 bootstrap.py")

    args.stack = detect_stack(proj) if args.stack == "auto" else args.stack

    out = Path(args.out).expanduser() if args.out else (
        proj / "out" / f"{proj.name}_{time.strftime('%H%M%S')}.mp4"
    )
    out.parent.mkdir(parents=True, exist_ok=True)

    cmd = build_cmd(args, proj, out)
    started = time.time()
    # 必须在工程目录里跑：remotion 的 CLI 在工程本地 node_modules 里
    proc = subprocess.run(cmd, cwd=str(proj), capture_output=True, text=True)
    elapsed = time.time() - started
    tail = "\n".join(
        line for line in (proc.stdout + proc.stderr).splitlines()
        if "Render:trace" not in line and "hf-progress" not in line
    )[-1200:]

    if proc.returncode != 0 or not out.exists():
        result = {
            "ok": False,
            "stack": args.stack,
            "cmd": cmd,
            "elapsed_s": round(elapsed, 1),
            "error": tail,
        }
        print(json.dumps(result, ensure_ascii=False, indent=2) if args.json else
              f"渲染失败（{args.stack}）\n{tail}")
        return 1

    info = probe(out)
    stills = grab_stills(out, [float(x) for x in args.stills.split(",")], out.parent / "stills") if args.stills else []
    result = {
        "ok": True,
        "stack": args.stack,
        "elapsed_s": round(elapsed, 1),
        "output": out,
        **info,
        "stills": stills,
        "log_tail": tail[-400:] if args.quality == "draft" else "",
    }

    if args.json:
        print(json.dumps(result, ensure_ascii=False, indent=2, default=str))
    else:
        print(f"✓ {out}")
        print(f"  {info.get('duration_s')}s · {info.get('width')}x{info.get('height')} · "
              f"{info.get('fps')} fps · {info.get('size_mb')} MB · 用时 {elapsed:.1f}s")
        if stills:
            print("  关键帧：" + "  ".join(stills))
    return 0


if __name__ == "__main__":
    sys.exit(main())
