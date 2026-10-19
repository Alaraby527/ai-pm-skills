#!/usr/bin/env python3
"""Mechanical lint for an interview self-introduction script.

Usage:
    python3 lint_intro.py <file.md> [--target 90] [--keywords "用户洞察,数据驱动"] [--strict]

Checks performed:
    1. Estimated speaking duration (Chinese speech ~= 4 chars/second)
    2. Red-line wording ("匹配" and its slogan variants)
    3. Empty bragging words ("逻辑强", "沟通好", ...) with no evidence attached
    4. Structural completeness of the six required anchors
    5. Quantitative evidence inside each hard story
    6. Filler words ("然后", "嗯", ...) left in the written script
    7. JD keyword coverage (only when --keywords is supplied)
    8. AI-slop signatures (S1-S10 from references/anti-slop.md): meta-framing
       opener, list-carrying argument, nominalization clusters, generic examples,
       no first-person, prompt residue, hedge clusters, buzzword stuffing,
       flattened uncertainty

The script is read-only with respect to everything except its own report,
performs no network access, and never modifies the input file.
"""

import argparse
import re
import sys
from pathlib import Path

CHARS_PER_SECOND = 4.0

ANCHORS = [
    ("【核心人设】", True),
    ("【硬核故事A", True),
    ("【硬核故事B", True),
    ("【生命力彩蛋】", False),
    ("【动机】", True),
    ("【钩子】", True),
]

DISPLAY = {
    "【核心人设】": "① 核心人设 【核心人设】",
    "【硬核故事A": "② 硬核故事A/专业硬实力 【硬核故事A】",
    "【硬核故事B": "③ 硬核故事B/软素质 【硬核故事B】",
    "【生命力彩蛋】": "④ 生命力彩蛋 【生命力彩蛋】",
    "【动机】": "⑤ 动机/未来可期 【动机】",
    "【钩子】": "⑥ 钩子 【钩子】",
}

RED_LINE_WORDS = [
    "匹配", "非常适合", "完全符合", "我很契合", "高度契合", "契合该岗位",
    "岗位要求我都", "我就是你们要找的人",
]

EMPTY_BRAG_WORDS = [
    "逻辑强", "逻辑能力强", "沟通好", "沟通能力强", "学习能力强", "学习能力强",
    "抗压能力强", "协作能力强", "团队合作能力强", "有责任心", "踏实肯干",
    "勤奋好学", "乐于助人",
]

FILLER_WORDS = ["然后", "嗯", "就是说", "可能吧", "反正", "那个那个"]

SLANG_WORDS = ["赋能", "抓手", "闭环", "打法", "颗粒度", "平台大", "技术氛围好"]

# --- AI 味 / slop 检测词表（依据 references/anti-slop.md） ---
S1_PATTERNS = [
    r"接下来我将", r"我将从", r"从以下(?:几|三|四|五)个(?:方面|维度)",
    r"下面我将", r"我将从(?:三|四)个", r"简单介绍一下自己",
]
S6_WORDS = ["总的来说", "综上所述", "以上就是我的", "希望有机会加入", "谢谢聆听", "感谢聆听", "望给予机会"]
S3_PATTERNS = [
    r"(?:进行|完成|实现|开展|推动)(?:了)?[^，。]{0,10}(?:的)?(?:赋能|优化|落地|打通|沉淀|升级|改造|建设|体系化)",
    r"(?:实现了|完成了|形成了|构建了)[^，。]{0,8}(?:闭环|机制|体系|能力|价值)",
]
S4_WORDS = ["某公司", "一家公司", "某企业", "一个项目", "相关工作", "相关经验", "一些工作", "某平台", "负责相关"]
ME_ACTION_PATTERN = r"我(?:先|就|当时|后来|把|改|拆|定|跑|做|协调|推动|砍|压|重新|发现|判断|坚持|说服|扛)"
SLANG_WORDS_EXT = SLANG_WORDS + ["沉淀", "对齐", "心智", "护城河", "打法", "颗粒度", "价值转化", "生态位"]
CONSTRAINT_WORDS = [
    "限制", "约束", "只有", "没有", "缺", "不足", "代价", "踩坑", "踩过", "失败",
    "推翻", "被否", "重来", "预算有限", "时间紧", "不会", "不懂", "盲区", "只能",
]

NUMBER_PATTERNS = [
    r"\d+\s*%", r"\d+\s*个百分点", r"\d+倍", r"从\s*[^\s，。]{1,10}\s*(?:到|降至|提升至|提升到)\s*[^\s，。]{1,10}",
    r"\d+(?:\.\d+)?\s*(?:万|亿|千|人|天|周|个月|秒|次|条|篇)",
]


def cjk_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def estimated_seconds(text: str) -> float:
    return cjk_count(text) / CHARS_PER_SECOND


def has_quant(text: str) -> bool:
    return any(re.search(p, text) for p in NUMBER_PATTERNS)


def split_sections(text: str):
    """Return list of (anchor_label, body) preserving order of appearance."""
    positions = []
    for idx, (anchor, _required) in enumerate(ANCHORS):
        for m in re.finditer(re.escape(anchor), text):
            positions.append((m.start(), anchor, idx))
    positions.sort()
    sections = []
    for i, (pos, anchor, _idx) in enumerate(positions):
        end = positions[i + 1][0] if i + 1 < len(positions) else len(text)
        sections.append((anchor, text[pos:end]))
    return sections


def main() -> int:
    parser = argparse.ArgumentParser(description="Lint an interview self-introduction script.")
    parser.add_argument("file", help="Path to the self-introduction markdown/text file")
    parser.add_argument("--target", type=int, default=90, help="Target duration in seconds (default: 90)")
    parser.add_argument("--keywords", default="", help="Comma separated JD keywords to check coverage")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any hard check fails")
    args = parser.parse_args()

    path = Path(args.file).expanduser()
    if not path.is_file():
        print("ERROR: file not found: %s" % path, file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")

    hard_fail = 0
    soft_warn = 0
    lines = []

    lines.append("# 自我介绍体检报告")
    lines.append("")
    lines.append("- 文件: `%s`" % path)
    lines.append("- 目标时长: %d 秒" % args.target)
    lines.append("")

    # 1. duration
    seconds = estimated_seconds(text)
    delta = abs(seconds - args.target)
    lines.append("## 1. 时长估算")
    lines.append("")
    lines.append("中文字符数: %d，按 4 字/秒估算 **%.0f 秒**（目标 %d 秒）" % (cjk_count(text), seconds, args.target))
    if delta <= 15:
        lines.append("✅ 时长在合理区间内（±15 秒）")
    elif delta <= 30:
        lines.append("⚠️ 时长偏差 %.0f 秒，建议微调内容量" % delta)
        soft_warn += 1
    else:
        lines.append("❌ 时长偏差 %.0f 秒，明显超时/过短，必须重写或压缩" % delta)
        hard_fail += 1
    lines.append("")

    # 2. red line
    lines.append("## 2. 红线词检查（喊「匹配」＝邀请面试官反驳你）")
    lines.append("")
    red_hits = [(w, m.start()) for w in RED_LINE_WORDS for m in re.finditer(re.escape(w), text)]
    if not red_hits:
        lines.append("✅ 未发现红线词")
    else:
        hard_fail += 1
        lines.append("❌ 发现 %d 处红线词，全部删除后重跑：" % len(red_hits))
        for w, pos in red_hits:
            snippet = text[max(0, pos - 20):pos + 20].replace("\n", " ")
            lines.append("   - `%s` …%s…" % (w, snippet))
        lines.append("   - 改法：删掉「我很匹配/非常适合」，改成讲一个让面试官自己得出匹配的故事")
    lines.append("")

    # 3. empty bragging
    lines.append("## 3. 空泛优势词检查")
    lines.append("")
    brag_hits = sorted({w for w in EMPTY_BRAG_WORDS if w in text})
    if not brag_hits:
        lines.append("✅ 未发现无佐证的优势形容词")
    else:
        soft_warn += 1
        lines.append("⚠️ 发现 %d 个空泛优势词：%s" % (len(brag_hits), "、".join(brag_hits)))
        lines.append("   - 改法：删除这些形容词，换成一段能证明它的经历（限制 → 行动 → 结果）")
    lines.append("")

    # 4. structure
    lines.append("## 4. 结构完整性（六要素）")
    lines.append("")
    sections = split_sections(text)
    found = {anchor for anchor, _ in sections}
    missing_required = [a for a, required in ANCHORS if required and a not in found]
    missing_optional = [a for a, required in ANCHORS if not required and a not in found]
    for anchor, required in ANCHORS:
        label = DISPLAY.get(anchor, anchor)
        if anchor in found:
            lines.append("✅ %s" % label)
        elif required:
            lines.append("❌ 缺少 %s（必填）" % label)
        else:
            lines.append("⚠️ 未使用 %s（可选，但强烈建议加上——这是你区别于其他候选人的地方）" % label)
    if missing_required:
        hard_fail += 1
    if missing_optional:
        soft_warn += 1
    lines.append("")

    # 5. quantitative evidence in stories
    lines.append("## 5. 硬核故事的证据强度")
    lines.append("")
    story_sections = [(a, b) for a, b in sections if a.startswith("【硬核故事")]
    if not story_sections:
        lines.append("⚠️ 未检测到硬核故事段落，无法检查证据")
        soft_warn += 1
    else:
        for anchor, body in story_sections:
            label = DISPLAY.get(anchor, anchor)
            if has_quant(body):
                lines.append("✅ %s 含量化证据（数字 / 从 X 到 Y）" % label)
            else:
                soft_warn += 1
                lines.append("⚠️ %s 未检测到数字，必须补；没有数字时至少要给出三种定性替代之一：相对对比 / 交付物 / 边界说明" % label)
    lines.append("")

    # 6. filler & slang
    lines.append("## 6. 口语赘余与黑话")
    lines.append("")
    filler_hits = sorted({w for w in FILLER_WORDS if w in text})
    slang_hits = sorted({w for w in SLANG_WORDS if w in text})
    if not filler_hits:
        lines.append("✅ 未发现口头禅")
    else:
        soft_warn += 1
        lines.append("⚠️ 发现口头禅：%s" % "、".join(filler_hits))
    if not slang_hits:
        lines.append("✅ 未发现万能黑话")
    else:
        soft_warn += 1
        lines.append("⚠️ 发现黑话/万能句：%s" % "、".join(slang_hits))
        lines.append("   - 改法：换成具体事实，例如「赋能业务」→「把转人工率从 42% 降到 19%」")
    lines.append("")

    # 7. JD keywords
    lines.append("## 7. JD 关键词命中")
    lines.append("")
    kws = [k.strip() for k in args.keywords.split(",") if k.strip()]
    if not kws:
        lines.append("（未传 --keywords，跳过。建议把 JD 三类关键词传进来检查命中）")
    else:
        hit, miss = [], []
        for k in kws:
            (hit if k in text else miss).append(k)
        if hit:
            lines.append("✅ 已命中：%s" % "、".join(hit))
        if miss:
            soft_warn += 1
            lines.append("⚠️ 未命中：%s" % "、".join(miss))
            lines.append("   - 目标：90 秒稿至少命中 3–5 个 JD 关键词，且每个词都在提示面试官可以追问")
    lines.append("")

    # 8. AI 味 / slop 签名扫描（依据 references/anti-slop.md）
    lines.append("## 8. AI 味检测（Slop 签名，依据 references/anti-slop.md）")
    lines.append("")

    body = text
    n_chars = max(cjk_count(body), 1)
    tier1, tier2 = [], []

    # S1 元框架开场
    s1_hits = [p for p in S1_PATTERNS if re.search(p, body[:200])]
    if s1_hits:
        tier1.append(("S1", "元框架开场", "首段出现「接下来我将/我将从…方面」——删掉，第一句直接给标签或结论"))

    # S2 列表撑论点（首先/其次/最后 或 1.2.3. 撑起全篇）
    if re.search(r"首先", body) and re.search(r"其次|再者", body) and re.search(r"最后|综上", body):
        tier1.append(("S2", "列表撑论点", "全篇靠「首先/其次/最后」支撑——删掉分点，改成两件具体的事"))

    # S6 提示词残留
    s6_hits = sorted({w for w in S6_WORDS if w in body})
    if s6_hits:
        tier1.append(("S6", "提示词残留", "发现 %s——这些是模型收尾腔，人不会这么说；结尾换成钩子" % "、".join(s6_hits)))

    # S3 名词化堆砌（每 100 字 >3）
    s3_count = sum(len(re.findall(p, body)) for p in S3_PATTERNS)
    if s3_count / (n_chars / 100.0) > 3:
        tier2.append(("S3", "名词化堆砌", "抽象名词化结构约 %.1f 处/100 字（阈值 3）——把「进行了…的赋能」改成「我改了什么、结果变成多少」" % (s3_count / (n_chars / 100.0))))

    # S4 泛化例子
    s4_hits = sorted({w for w in S4_WORDS if w in body})
    if s4_hits:
        tier2.append(("S4", "泛化例子", "发现 %s——必须给出具体公司/产品名、数字、时间" % "、".join(s4_hits)))

    # S5 无第一人称（找不到「我 + 具体动作」）
    if not re.search(ME_ACTION_PATTERN, body):
        tier2.append(("S5", "无第一人称", "通篇找不到「我 + 具体动作动词」（我拆了/我改了/我定了/我协调了）——面试官会判定你没做过"))

    # S8 模糊限定堆（任意 50 字窗口内 ≥2）
    hedges = ["可能", "大概", "某种程度上", "一定程度上", "或许", "应该算"]
    window_hit = False
    for i in range(0, max(len(body) - 50, 1)):
        seg = body[i:i + 50]
        if sum(seg.count(h) for h in hedges) >= 2:
            window_hit = True
            break
    if window_hit:
        tier2.append(("S8", "模糊限定堆", "50 字内出现 ≥2 个模糊限定（可能/大概/某种程度上）——要么给数字，要么删掉限定"))

    # S9 黑话堆砌（≥3）
    s9_hits = sorted({w for w in SLANG_WORDS_EXT if w in body})
    if len(s9_hits) >= 3:
        tier2.append(("S9", "黑话堆砌", "发现 %d 个黑话：%s——全部换成具体事实" % (len(s9_hits), "、".join(s9_hits))))

    # S10 不确定性被抹平（全篇无限制/代价/失败）
    if not any(w in body for w in CONSTRAINT_WORDS):
        tier2.append(("S10", "不确定性被抹平", "全篇没有一处限制、代价或失败——原方法论要求「先讲限制，再讲成果」，没有限制的成果不可信"))

    if not tier1 and not tier2:
        lines.append("✅ 未触发任何 slop 签名")
    else:
        if tier1:
            hard_fail += 1
            lines.append("❌ Tier-1（硬性，必改）——命中 %d 条：" % len(tier1))
            for code, name, fix in tier1:
                lines.append("   - **%s %s**：%s" % (code, name, fix))
        if tier2:
            if len(tier2) >= 3:
                hard_fail += 1
                lines.append("❌ Tier-2 命中 %d 条（≥3 条判定为硬性不合格）：" % len(tier2))
            else:
                soft_warn += 1
                lines.append("⚠️ Tier-2 命中 %d 条（1–2 条需人工改写确认）：" % len(tier2))
            for code, name, fix in tier2:
                lines.append("   - **%s %s**：%s" % (code, name, fix))

    lines.append("")
    lines.append("人工核对（脚本不自动判）：**S2 删掉分点后论点是否还成立**、**S7 是否 >60% 段落都是「总起+三句+收尾」同一形状**。")
    lines.append("")
    lines.append("对照样例见 `references/anti-slop.md`；说话方式校准见 `references/voice-calibration.md`。")
    lines.append("")

    # verdict
    lines.append("## 结论")
    lines.append("")
    if hard_fail == 0 and soft_warn == 0:
        lines.append("✅ **PASS** — 全部检查通过，可以进入 mock 环节")
    elif hard_fail == 0:
        lines.append("⚠️ **PASS（有提醒）** — %d 项需优化，不阻断交付，但建议按提示改完再练" % soft_warn)
    else:
        lines.append("❌ **FAIL** — %d 项硬性问题必须先修复，修完重跑本脚本" % hard_fail)
    lines.append("")
    lines.append("> 提醒：脚本只能做机械体检，通不过一定要改；通过了也不代表讲得好——还必须对镜/录音练到脱稿。")

    report = "\n".join(lines)
    print(report)

    if args.strict and hard_fail > 0:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
