#!/usr/bin/env python3
"""校验 dist/ 与 skills/ 内容级同步：包内每个条目必须等于 LF 归一后的源码字节。

CI 用内容级校验而非"重建后 git diff"：zip 容器字节会随平台/Python 小版本产生
元数据级差异，而"内容一致"才是要保证的不变量（防止 dist 再度发布过时方法论）。

用法：
    python scripts/check-dist.py   # 退出码 0 = 同步；1 = 不同步（附差异清单）
"""

import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"

BUNDLE_NAME = "ai-pm-job-hunting"
BUNDLE_MODULES = ["resume-jd-align", "interview-prep", "interview-retro", "script-polish"]


def norm(data: bytes) -> bytes:
    return data.replace(b"\r\n", b"\n")


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


def read_zip(path: Path) -> dict:
    with zipfile.ZipFile(path) as zf:
        return {n: zf.read(n) for n in zf.namelist() if not n.endswith("/")}


def check_single(d: Path, problems: list) -> None:
    zipped = read_zip(DIST / f"{d.name}.skill")
    src = {
        f"{d.name}/{p.relative_to(d).as_posix()}": norm(p.read_bytes())
        for p in sorted(d.rglob("*")) if p.is_file()
    }
    if set(zipped) != set(src):
        extra = sorted(set(zipped) - set(src))
        missing = sorted(set(src) - set(zipped))
        problems.append(f"{d.name}: 文件集不一致（包内多 {extra} / 缺 {missing}）")
    for k in sorted(set(zipped) & set(src)):
        if zipped[k] != src[k]:
            problems.append(f"{d.name}: 内容过时: {k}")


def check_bundle(problems: list) -> None:
    path = DIST / f"{BUNDLE_NAME}.skill"
    if not path.exists():
        problems.append(f"缺四合一包 {BUNDLE_NAME}.skill")
        return
    zipped = read_zip(path)
    sk = zipped.get(f"{BUNDLE_NAME}/SKILL.md", b"").decode("utf-8")
    for m in BUNDLE_MODULES:
        body = strip_frontmatter(
            norm((SKILLS / m / "SKILL.md").read_bytes()).decode("utf-8")
        ).strip()
        if body[:200] not in sk:
            problems.append(f"{BUNDLE_NAME}: 模块 {m} 正文不是最新版")
        for sp in sorted((SKILLS / m / "references").glob("*")):
            arc = f"{BUNDLE_NAME}/references/{sp.name}"
            if sp.name == "prompts.md":
                merged = zipped.get(arc, b"").decode("utf-8")
                src_prompt = norm(sp.read_bytes()).decode("utf-8")
                if src_prompt.strip() and src_prompt not in merged:
                    problems.append(f"{BUNDLE_NAME}: prompts.md 缺模块 {m} 最新内容")
            elif arc not in zipped:
                problems.append(f"{BUNDLE_NAME}: 缺 {arc}")
            elif zipped[arc] != norm(sp.read_bytes()):
                problems.append(f"{BUNDLE_NAME}: 内容过时: {arc}")


def main() -> int:
    problems: list = []
    names = sorted(d.name for d in SKILLS.iterdir() if d.is_dir())
    for n in names:
        if not (DIST / f"{n}.skill").exists():
            problems.append(f"缺包: {n}.skill")
            continue
        check_single(SKILLS / n, problems)
    check_bundle(problems)
    if problems:
        print("dist/ 与 skills/ 不同步：")
        for p in problems:
            print(" -", p)
        print("请运行 python scripts/build-dist.py 后重新提交。")
        return 1
    print(f"dist/ 与 skills/ 内容同步（{len(names)} 单包 + 四合一包）")
    return 0


if __name__ == "__main__":
    sys.exit(main())
