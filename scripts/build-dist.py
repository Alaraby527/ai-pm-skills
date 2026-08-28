#!/usr/bin/env python3
"""从 skills/ 重新生成 dist/ 下全部 .skill 包（12 个单包 + 求职四合一包）。

每次修改 SKILL.md 或 references 后必须重跑本脚本并提交，CI 会校验 dist 与 skills 是否同步。
历史上 dist 曾与源码脱节（旧包停留在过时方法论），此脚本是防止复发的唯一打包入口。

用法：
    python scripts/build-dist.py
"""

import shutil
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SKILLS = ROOT / "skills"
DIST = ROOT / "dist"

# 求职四合一包：由以下模块合并生成（references 无文件名冲突，仅 prompts.md 分节合并）
BUNDLE = {
    "name": "ai-pm-job-hunting",
    "modules": ["resume-jd-align", "interview-prep", "interview-retro", "script-polish"],
}

BUNDLE_DESC = (
    "AI 产品经理求职四合一：简历-JD 对齐 + 面试备战 + 面试复盘 + 逐字稿打磨。"
    "当用户说「优化简历」「简历匹配JD」「三梯队投递」「面试准备」「模拟面试」"
    "「面试复盘」「面试挂了」「逐字稿」「打磨回答」等求职相关表达时触发。"
)


def strip_frontmatter(text: str) -> str:
    lines = text.splitlines()
    if lines and lines[0].strip() == "---":
        for i in range(1, len(lines)):
            if lines[i].strip() == "---":
                return "\n".join(lines[i + 1:]).lstrip("\n")
    return text


def _write_entry(zf: zipfile.ZipFile, arc: str, data: bytes) -> None:
    # 确定性构建：固定时间戳与权限位，保证内容不变时 zip 字节完全一致（CI 可 diff 校验）
    zi = zipfile.ZipInfo(arc, date_time=(1980, 1, 1, 0, 0, 0))
    zi.external_attr = 0o644 << 16
    zi.compress_type = zipfile.ZIP_DEFLATED
    zf.writestr(zi, data)


def add_dir_to_zip(zf: zipfile.ZipFile, src: Path, arc_prefix: str) -> None:
    for p in sorted(src.rglob("*")):
        if p.is_file():
            arc = f"{arc_prefix}/{p.relative_to(src).as_posix()}"
            # 统一换行为 LF：Windows 检出（CRLF）与 CI 检出（LF）产出相同的包
            _write_entry(zf, arc, p.read_bytes().replace(b"\r\n", b"\n"))


def build_single(name: str) -> None:
    with zipfile.ZipFile(DIST / f"{name}.skill", "w", zipfile.ZIP_DEFLATED) as zf:
        add_dir_to_zip(zf, SKILLS / name, name)


def build_bundle() -> None:
    name, mods = BUNDLE["name"], BUNDLE["modules"]
    tmp = DIST / "_bundle_tmp"
    bdir = tmp / name
    refs = bdir / "references"
    shutil.rmtree(tmp, ignore_errors=True)
    refs.mkdir(parents=True)

    # 复制四模块 references（文件名不冲突的直接共用；prompts.md 冲突，分节合并）
    for m in mods:
        for p in sorted((SKILLS / m / "references").glob("*")):
            if p.name != "prompts.md" and not (refs / p.name).exists():
                shutil.copy(p, refs / p.name)
    parts = []
    for m in mods:
        body = (SKILLS / m / "references" / "prompts.md").read_text(encoding="utf-8")
        parts.append(f"\n\n---\n\n# 以下提示词来自模块：{m}\n\n{body}")
    (refs / "prompts.md").write_text(
        "# 提示词合集（四模块合并版，按模块分节）\n" + "".join(parts), encoding="utf-8"
    )

    # 合并 SKILL.md：新 frontmatter + 总说明 + 四模块正文（去掉各自 frontmatter）
    head = (
        f"---\nname: {name}\ndescription: \"{BUNDLE_DESC}\"\n---\n\n"
        "# AI PM 求职四合一 Skill\n\n"
        "求职全链路四件套合并包，四个模块按求职漏斗串联：\n"
        "1. 简历-JD 对齐（拿到面试）→ 2. 面试备战（素材+题型框架）→ "
        "3. 逐字稿打磨（表达落地）→ 4. 面试复盘（短板回流补强简历与素材）。\n\n"
        "**references/ 为四模块合并目录**：模板文件名不冲突、直接共用；"
        "`prompts.md` 为四模块提示词的合并版，按模块分节查阅。\n"
    )
    for m in mods:
        body = strip_frontmatter((SKILLS / m / "SKILL.md").read_text(encoding="utf-8"))
        head += f"\n\n---\n\n{body}"
    (bdir / "SKILL.md").write_text(head, encoding="utf-8")

    with zipfile.ZipFile(DIST / f"{name}.skill", "w", zipfile.ZIP_DEFLATED) as zf:
        add_dir_to_zip(zf, bdir, name)
    shutil.rmtree(tmp)


def main() -> None:
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir()
    names = sorted(p.name for p in SKILLS.iterdir() if p.is_dir())
    for n in names:
        build_single(n)
    build_bundle()
    print(f"已生成 {len(names) + 1} 个包：")
    for p in sorted(DIST.iterdir()):
        print(" ", p.name)


if __name__ == "__main__":
    main()
