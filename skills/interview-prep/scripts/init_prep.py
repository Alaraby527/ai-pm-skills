#!/usr/bin/env python3
"""Scaffold an interview-prep workspace from the bundled templates.

Usage:
    python3 init_prep.py --company "腾讯" --role "AI产品经理" [--dir "./面试准备"] [--force]

The script only reads files inside this skill's assets/templates directory and
writes into the user-specified target directory. It performs no network access,
no shell execution, and never deletes existing files unless --force is given.
"""

import argparse
import datetime as _dt
import sys
from pathlib import Path

TEMPLATES = [
    ("prep-brief.md", "01-岗位分析.md"),
    ("material-bank.md", "02-素材库.md"),
    ("self-intro.md", "03-自我介绍稿.md"),
    ("story-card.md", "04-项目故事卡.md"),
    ("question-bank.md", "05-题库.md"),
    ("ask-list.md", "06-提问清单.md"),
    ("review.md", "07-复盘.md"),
    ("checklist.md", "08-时间表自检.md"),
]


def main() -> int:
    parser = argparse.ArgumentParser(description="Initialize an interview preparation workspace.")
    parser.add_argument("--company", required=True, help="Target company name")
    parser.add_argument("--role", required=True, help="Target role / position")
    parser.add_argument("--dir", default="./面试准备", help="Output directory (default: ./面试准备)")
    parser.add_argument("--project", default=None, help="Optional project name used by the story card")
    parser.add_argument("--force", action="store_true", help="Overwrite files that already exist")
    args = parser.parse_args()

    assets_dir = Path(__file__).resolve().parent.parent / "assets" / "templates"
    if not assets_dir.is_dir():
        print("ERROR: template directory not found: %s" % assets_dir, file=sys.stderr)
        return 2

    target = Path(args.dir).expanduser()
    target.mkdir(parents=True, exist_ok=True)

    today = _dt.date.today().isoformat()
    replacements = {
        "{{COMPANY}}": args.company,
        "{{ROLE}}": args.role,
        "{{DATE}}": today,
        "{{PROJECT}}": args.project or (args.role + " 的代表项目"),
    }

    created, skipped = [], []
    for src_name, dst_name in TEMPLATES:
        src = assets_dir / src_name
        if not src.is_file():
            print("WARN: missing template %s" % src_name, file=sys.stderr)
            continue
        text = src.read_text(encoding="utf-8")
        for token, value in replacements.items():
            text = text.replace(token, value)
        dst = target / dst_name
        if dst.exists() and not args.force:
            skipped.append(dst_name)
            continue
        dst.write_text(text, encoding="utf-8")
        created.append(dst_name)

    print("面试准备工作区已就绪: %s" % target.resolve())
    print("公司/岗位: %s · %s" % (args.company, args.role))
    print("新建文件: %d" % len(created))
    for name in created:
        print("  + %s" % name)
    if skipped:
        print("已存在(未覆盖): %s" % ", ".join(skipped))
    print("")
    print("下一步:")
    print("  1. 填写 01-岗位分析.md（先拆 JD，再回答岗位四问）")
    print("  2. 填写 02-素材库.md（异常值三步法 + 三个标签维度）")
    print("  3. 写 03-自我介绍稿.md，然后跑体检:")
    print("     python3 %s/lint_intro.py \"%s/03-自我介绍稿.md\" --target 90"
          % (Path(__file__).resolve().parent, target))
    return 0


if __name__ == "__main__":
    sys.exit(main())
