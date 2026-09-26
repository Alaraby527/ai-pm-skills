#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
gen_pkeys.py — 从飞书 csv-get 快照生成 P 键排序辅助列。

输入：csv-get 落盘的 JSON（需含 annotated_csv；列以制表符分隔，每行带 "[row=N] " 前缀）。
输出（默认 stdout）：单列 P 键，每行一个整数，顺序与快照数据行一致（可直接 csv-put 到 P2）。

分组（升序）：活跃 1,000,000 → 待投递 3,000,000 → 复盘 5,000,000
             → 线下双选会 7,000,000 → 空行 9,000,000；
组内键 = 组常量 + 物理行号 n，保证同组稳定、新投递行(n 最大)落活跃块底部。

用法：
  python3 gen_pkeys.py snapshot.json                 # 打印 P 键到 stdout
  python3 gen_pkeys.py snapshot.json -o pkeys.csv    # 写入文件
  python3 gen_pkeys.py snapshot.json --applied 12    # 强制把物理行 12 也算已投递
"""
import argparse
import csv
import io
import json
import re
import sys

ACTIVE, PENDING, REVIEW, OFFLINE, EMPTY = 1_000_000, 3_000_000, 5_000_000, 7_000_000, 9_000_000

# 主表列字母 → 0-based 下标（A…P）
COL = {c: i for i, c in enumerate("ABCDEFGHIJKLMNOP")}
ACTIVE_STATUS = {"已投递", "笔试中", "面试中", "已offer", "已挂", "已截止", "已沟通"}

ROW_RE = re.compile(r"^\[row=(\d+)\]\s?(.*)$")


def parse_annotated_csv(text):
    """把 annotated_csv 解析成 [(物理行号, [字段…]), …]，仅保留数据行（跳过表头）。"""
    rows = []
    reader = csv.reader(io.StringIO(text), delimiter="\t")
    header = None
    for raw in reader:
        if not raw:
            continue
        m = ROW_RE.match(raw[0])
        if not m:
            continue
        n = int(m.group(1))
        raw[0] = m.group(2)
        if header is None:
            header = raw  # 第一行=表头，定位列用
            continue
        rows.append((n, raw))
    return rows


def field(row, letter):
    i = COL[letter]
    return row[i].strip() if i < len(row) else ""


def pkey(n, row, force_applied=False):
    g, m = field(row, "G"), field(row, "M")
    content = any(field(row, c) for c in "ABCDEFGHIJKLMNO")
    if not content:
        return EMPTY + n
    if g == "复盘":
        return REVIEW + n
    if g == "线下双选会":
        return OFFLINE + n
    if force_applied or m in ACTIVE_STATUS:
        return ACTIVE + n
    return PENDING + n


def main():
    ap = argparse.ArgumentParser(description="生成主表 P 键排序辅助列")
    ap.add_argument("snapshot", help="csv-get 落盘的 JSON 文件")
    ap.add_argument("-o", "--output", help="输出文件（默认 stdout）")
    ap.add_argument("--applied", type=int, action="append", default=[],
                    help="强制把该行算已投递（可多次传）")
    args = ap.parse_args()

    with open(args.snapshot, "r", encoding="utf-8") as f:
        data = json.load(f)
    text = data.get("annotated_csv") or (data.get("data") or {}).get("annotated_csv") or ""
    if not text:
        sys.exit("快照中未找到 annotated_csv")

    forced = set(args.applied)
    keys = [pkey(n, row, force_applied=(n in forced)) for n, row in parse_annotated_csv(text)]

    out = "\n".join(str(k) for k in keys) + "\n"
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(out)
    else:
        sys.stdout.write(out)


if __name__ == "__main__":
    main()
