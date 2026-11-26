#!/usr/bin/env python3
"""从内置模板起一个新工程。

用法：
    python3 new_project.py ../我的片子 --stack hyperframes
    python3 new_project.py ../我的片子 --stack remotion --install
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from pathlib import Path

SKILL_DIR = Path(__file__).resolve().parent.parent
ASSETS = SKILL_DIR / "assets"

HYPERFRAMES_JSON = {
    "$schema": "https://hyperframes.heygen.com/schema/hyperframes.json",
    "registry": "https://raw.githubusercontent.com/heygen-com/hyperframes/main/registry",
    "paths": {"blocks": "compositions", "components": "compositions/components", "assets": "assets"},
    "media": {"autoProxy": True},
}


def copy_hyperframes(dst: Path) -> None:
    src = ASSETS / "hyperframes-starter" / "index.html"
    if not src.exists():
        raise SystemExit(f"模板缺失：{src}")
    shutil.copy2(src, dst / "index.html")
    (dst / "hyperframes.json").write_text(json.dumps(HYPERFRAMES_JSON, indent=2, ensure_ascii=False) + "\n")
    (dst / "package.json").write_text(
        json.dumps(
            {
                "name": dst.name,
                "private": True,
                "type": "module",
                "scripts": {
                    "dev": "npx --yes hyperframes preview",
                    "lint": "npx --yes hyperframes lint .",
                    "render": "npx --yes hyperframes render . -o out/video.mp4",
                },
            },
            indent=2,
        )
        + "\n"
    )
    (dst / "meta.json").write_text(
        json.dumps({"id": dst.name, "name": dst.name}, indent=2, ensure_ascii=False) + "\n"
    )


def copy_remotion(dst: Path, install: bool) -> None:
    src = ASSETS / "remotion-starter"
    ignore = shutil.ignore_patterns("node_modules", "out", "*.png", ".git")
    shutil.copytree(src, dst, ignore=ignore, dirs_exist_ok=True)
    if install:
        code = subprocess.run(
            ["npm", "install", "--no-audit", "--no-fund"], cwd=str(dst)
        ).returncode
        if code != 0:
            raise SystemExit("npm install 失败，进工程目录手动重试")


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("target")
    ap.add_argument("--stack", choices=["hyperframes", "remotion"], default="hyperframes")
    ap.add_argument("--install", action="store_true", help="Remotion 工程顺便装依赖")
    ap.add_argument("--force", action="store_true", help="目录非空也写入")
    args = ap.parse_args()

    dst = Path(args.target).expanduser().resolve()
    if dst.exists() and any(dst.iterdir()) and not args.force:
        raise SystemExit(f"目录非空：{dst}（加 --force 覆盖）")
    dst.mkdir(parents=True, exist_ok=True)

    if args.stack == "hyperframes":
        copy_hyperframes(dst)
        print(f"✓ HyperFrames 工程：{dst}")
        print(f"  预览：cd \"{dst}\" && npm run dev")
        print(f"  出片：python3 {Path(__file__).parent / 'render.py'} \"{dst}\"")
    else:
        copy_remotion(dst, args.install)
        print(f"✓ Remotion 工程：{dst}")
        if not args.install:
            print(f"  先装依赖：cd \"{dst}\" && npm install")
        print(f"  预览：cd \"{dst}\" && npm run studio")
        print(f"  出片：python3 {Path(__file__).parent / 'render.py'} \"{dst}\"")

    print("  下一步：改 index.html / src，把内容换成你的脚本，再渲染验证。")
    return 0


if __name__ == "__main__":
    sys.exit(main())
