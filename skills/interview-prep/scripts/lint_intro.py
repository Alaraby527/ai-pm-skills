#!/usr/bin/env python3
"""Mechanical lint for an interview self-introduction script.

Usage:
    python3 lint_intro.py <file.md> [--target 90] [--keywords "用户洞察,数据驱动"] [--strict]

Checks performed:
    1. Estimated speaking duration (Chinese speech ~= 4 chars/second)
    2. Red-line wording ("匹配" and its slogan variants)
    3. Empty bragging words ("逻辑强", "沟通好", ...) with no evidence attached
    4. Structural completeness of the six required anchors (checked on the FULL
       file; anchors live in the workspace zone)
    5. Quantitative evidence inside each hard story
    6. Filler words ("然后", "嗯", ...) left in the written script
    7. JD keyword coverage (only when --keywords is supplied)
    8. AI-slop signatures (S1-S15 from references/anti-slop.md +
       references/human-voice-spec.md): meta-framing opener, list-carrying
       argument, nominalization clusters, generic examples, no first-person,
       prompt residue, hedge clusters, buzzword stuffing, flattened
       uncertainty, structural exposure (S11: bullets/numbering/labels leaked
       into the speech text), uniform rhythm (S12), director-style
       structural transitions (S13), workspace jargon leaked into speech
       (S14), deliberate rhetoric bridges (S15)
    9. Positive human-voice features (timeline markers, oral markers,
       concession) from references/human-voice-spec.md

All content checks (1-3, 5-9) run against the speech zone only: the text
between <!-- speech:start --> / <!-- speech:end --> markers. Without markers,
the whole file is linted (legacy behavior).

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

RED_LINE_PATTERNS = [
    r"我(?:很|非常)?匹配", r"(?:很|非常|高度|完全)匹配", r"匹配(?:这个|该|贵司|贵公司|岗位|要求|方向)",
    r"非常适合", r"完全符合", r"我很契合", r"高度契合", r"契合该岗位",
    r"岗位要求我都", r"我就是你们要找的人", r"方向[^，。]{0,10}对得[上来]", r"完全对得上",
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

# --- 拟人化检测（依据 references/human-voice-spec.md） ---
SPEECH_START = "<!-- speech:start -->"
SPEECH_END = "<!-- speech:end -->"

# S11 结构外显：成稿区出现任何"提纲形状"即 Tier-1
STRUCT_MARKER_PATTERNS = [
    (r"^\s*[①②③④⑤⑥⑦⑧⑨]", "圈号序数 ①②③"),
    (r"^\s*(?:\d+\s*[\.、]|[一二三四五六七八九]\s*[、\.])", "数字/汉字序号"),
    (r"^\s*[-*•·]\s+", "列表符号 -/•"),
    (r"^\s*#{1,6}\s", "markdown 标题"),
    (r"^\s*\*\*[^*\n]+\*\*", "加粗小标题"),
    (r"^\s*(?:背景|问题|过程|结果|定位|证据|动机|钩子|收尾|故事\s*[AB]|专业能力|项目经历|求职动机)\s*[:：]", "字段标签「背景：」式"),
    (r"【[^】\n]{1,20}】", "正文中的【标签】"),
    (r"[①②③④⑤⑥]", "正文中的圈号"),
]

TIMELINE_MARKERS = [
    "当时", "的时候", "那时候", "那天", "后来", "接手时", "一开始", "那阵子", "那三个月",
    "上线初期", "上线前", "前两周", "第一周", "实习第", "实习那", "大三", "大四",
    "那两个月", "那个月", "那两周", "那年", "在读",
]
ORAL_MARKERS = ["其实", "说白了", "说实话", "这么说吧", "坦白讲", "挺", "蛮", "结果", "问题在于", "这块"]
CONCESSION_MARKERS = [
    "一开始", "更准确地说", "后来发现", "做错了", "选错", "我不太想说", "被推翻",
]

# S13 编导式转场（结构播报，human-voice-spec A13）——词表只是兜底，人工判定为准
DIRECTOR_TRANSITION_PATTERNS = [
    r"就说这段", r"聊聊这个", r"话锋一转", r"从头讲", r"接下来这段", r"下面这段",
    r"说回正题", r"轮到(?:交互|技术|项目|结果|动机|治理|产品)",
]

# S14 术语泄漏（工作台词汇进了成稿，human-voice-spec A14）
JARGON_LEAK_PATTERNS = [
    r"最硬的", r"深水区", r"弹药", r"北极星", r"埋钩子", r"留钩子", r"钩子是", r"贴标签",
]

# S15 刻意修辞桥（悬念句/反转句/设计回指，human-voice-spec A15）
RHETORIC_BRIDGE_PATTERNS = [
    r"就是这么来的", r"我没先(?:碰|动|做)", r"不是[^，。]{1,8}调出来的", r"就是这么挣来的",
]

# S16 模糊动词壳（human-voice-spec H12：既非手段也非成果的动量词短语）
MUSHY_VERB_PATTERNS = [
    r"重做了一?轮", r"做了一?轮迭代", r"下手做", r"搞了一?波", r"迭代了一?轮",
]

# S17 具体日历时间（自我介绍不写日历时间——简历上有，口语用相对/场景时间）
CALENDAR_PATTERNS = [r"20\d{2}\s*年", r"\d{1,2}\s*月份?到"]


def cjk_count(text: str) -> int:
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def extract_speech_zones(text: str):
    """Return list of 开讲版 zones between speech markers (empty list if none)."""
    zones = []
    rest = text
    while True:
        i = rest.find(SPEECH_START)
        if i == -1:
            break
        rest = rest[i + len(SPEECH_START):]
        j = rest.find(SPEECH_END)
        if j == -1:
            zones.append(rest)
            break
        zones.append(rest[:j])
        rest = rest[j + len(SPEECH_END):]
    return zones


def extract_speech(text: str) -> str:
    """All speech zones joined; falls back to whole text (legacy behavior)."""
    zones = extract_speech_zones(text)
    return "\n".join(zones).strip() if zones else text


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
    parser.add_argument("--zone", type=int, default=0, help="Lint only the Nth speech zone (1-based); 0 = all zones joined")
    parser.add_argument("--strict", action="store_true", help="Exit 1 when any hard check fails")
    args = parser.parse_args()

    path = Path(args.file).expanduser()
    if not path.is_file():
        print("ERROR: file not found: %s" % path, file=sys.stderr)
        return 2
    text = path.read_text(encoding="utf-8")
    zones = extract_speech_zones(text)
    if zones and args.zone > 0:
        if args.zone > len(zones):
            print("ERROR: only %d speech zone(s) found, --zone %d out of range" % (len(zones), args.zone), file=sys.stderr)
            return 2
        speech = zones[args.zone - 1].strip()
        zone_desc = "开讲版第 %d/%d 段" % (args.zone, len(zones))
    elif zones:
        speech = "\n".join(zones).strip()
        zone_desc = "开讲版全部 %d 段（合并计时，可用 --zone 分段）" % len(zones)
    else:
        speech = text
        zone_desc = "全文（未找到 speech 标记，按旧版行为）"
    linting_speech_zone = speech != text

    hard_fail = 0
    soft_warn = 0
    lines = []

    lines.append("# 自我介绍体检报告")
    lines.append("")
    lines.append("- 文件: `%s`" % path)
    lines.append("- 目标时长: %d 秒" % args.target)
    lines.append("- 检测区域: %s" % zone_desc)
    lines.append("")

    # 1. duration
    seconds = estimated_seconds(speech)
    delta = abs(seconds - args.target)
    lines.append("## 1. 时长估算")
    lines.append("")
    lines.append("中文字符数: %d，按 4 字/秒估算 **%.0f 秒**（目标 %d 秒）" % (cjk_count(speech), seconds, args.target))
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
    red_hits = [(p, m.start()) for p in RED_LINE_PATTERNS for m in re.finditer(p, speech)]
    if not red_hits:
        lines.append("✅ 未发现红线词")
    else:
        hard_fail += 1
        lines.append("❌ 发现 %d 处红线词，全部删除后重跑：" % len(red_hits))
        for w, pos in red_hits:
            snippet = speech[max(0, pos - 20):pos + 20].replace("\n", " ")
            lines.append("   - `%s` …%s…" % (w, snippet))
        lines.append("   - 改法：删掉「我很匹配/非常适合」，改成讲一个让面试官自己得出匹配的故事")
    lines.append("")

    # 3. empty bragging
    lines.append("## 3. 空泛优势词检查")
    lines.append("")
    brag_hits = sorted({w for w in EMPTY_BRAG_WORDS if w in speech})
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
    filler_hits = sorted({w for w in FILLER_WORDS if w in speech})
    slang_hits = sorted({w for w in SLANG_WORDS if w in speech})
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
            (hit if k in speech else miss).append(k)
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

    body = speech
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

    # S11 结构外显（Tier-1）：开讲版里出现序号/列表/标签/标题/字段冒号
    s11_labels = []
    for pat, label in STRUCT_MARKER_PATTERNS:
        if re.search(pat, body, re.M):
            s11_labels.append(label)
    if s11_labels:
        tier1.append(("S11", "结构外显", "成稿里出现 %s——公式骨架被外显成了输出格式（分点答题的直接根因）。把分点连成连续的话，转场用内容词（后来/另一件事/说回到），标签只允许留在工作台区" % "、".join(sorted(set(s11_labels)))))

    # S12 节奏（逗号链过长——出声读会憋气；短句不强制要求，刻意造 mic-drop 反而是 A16）
    sents = [s.strip() for s in re.split(r"[。！？!?；]", body) if s.strip() and cjk_count(s.strip()) >= 3]
    long_comma = [s for s in sents if s.count("，") >= 4 or s.count(",") >= 4]
    if long_comma:
        tier2.append(("S12", "逗号链过长", "有 %d 句逗号 ≥4——出声读会憋气，拆成两句" % len(long_comma)))

    # S13 编导式转场（结构播报，词表兜底）
    s13_hits = [p for p in DIRECTOR_TRANSITION_PATTERNS if re.search(p, body)]
    if s13_hits:
        tier2.append(("S13", "编导式转场", "发现 %s——转场在播报结构而不是推进内容（真人转场带时间/因果/话题信息，或不转直接说下一件事）；删掉这句看前后是否仍直接相连，能相连就删" % "、".join(s13_hits)))

    # S14 术语泄漏（工作台词汇进了成稿）
    s14_hits = [p for p in JARGON_LEAK_PATTERNS if re.search(p, body)]
    if s14_hits:
        tier2.append(("S14", "术语泄漏", "发现 %s——这些是准备过程的工作台行话，面试官没读过你的方法论；换成面试官视角的自然说法（报经历用「最核心的一段是在 X 做 Y，主要负责 Z」）" % "、".join(s14_hits)))

    # S15 刻意修辞桥（悬念/反转/设计回指）
    s15_hits = [p for p in RHETORIC_BRIDGE_PATTERNS if re.search(p, body)]
    if s15_hits:
        tier2.append(("S15", "刻意修辞桥", "发现 %s——为效果而非为信息服务的句子；删掉后信息无损的悬念句/回指句一律删，报经历=手段→成果平铺直叙" % "、".join(s15_hits)))

    # S16 模糊动词壳（既非手段也非成果）
    s16_hits = [p for p in MUSHY_VERB_PATTERNS if re.search(p, body)]
    if s16_hits:
        tier2.append(("S16", "模糊动词壳", "发现 %s——既不是手段也不是成果的动量词短语；成果句用标准形态「通过【名词级手段】，把【指标】从 A 提升到 B」" % "、".join(s16_hits)))

    # S17 具体日历时间（自我介绍不写日历时间）
    if re.search(r"20\d{2}\s*年", body):
        tier2.append(("S17", "具体日历时间", "自我介绍里出现 20XX 年——简历上有日历时间，口语里说它不携带增量；换成相对/场景时间（接手的时候/一开始/那阵子/前两周）"))

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
    lines.append("## 9. 拟人特征正向检查（human-voice-spec H3/H5/H8）")
    lines.append("")

    if any(w in body for w in TIMELINE_MARKERS):
        lines.append("✅ 有叙事时间标记（当时/后来/上线前…）")
    else:
        soft_warn += 1
        lines.append("⚠️ 没有叙事时间标记——把「实习期间我负责…」改成「实习那两个月，当时…」（总结态→叙事态）")

    oral_n = sum(body.count(w) for w in ORAL_MARKERS)
    if 3 <= oral_n <= 8:
        lines.append("✅ 口语标记 %d 个（目标 3–6）" % oral_n)
    else:
        soft_warn += 1
        lines.append("⚠️ 口语标记 %d 个（目标 3–6：其实/说白了/挺/蛮/这么说吧）——0 个是通稿感，>8 是表演感" % oral_n)

    if any(w in body for w in CONCESSION_MARKERS):
        lines.append("✅ 有让步/自我修正（一开始…后来发现…）")
    else:
        soft_warn += 1
        lines.append("⚠️ 没有让步或修正——加恰好一处（说实话这块我一开始做错了 / 更准确地说 / 一开始我想…后来发现不行）")

    lines.append("")

    lines.append("人工核对（脚本不自动判）：**S2 删掉分点后论点是否还成立**、**S7 是否 >60% 段落都是「总起+三句+收尾」同一形状**、**接缝检查（随机删一句前后仍自然衔接）**。")
    lines.append("")
    lines.append("对照样例见 `references/anti-slop.md`；AI 味与拟人化规范见 `references/human-voice-spec.md`；说话方式校准见 `references/voice-calibration.md`。")
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
# ​‌​​​​​‌​‌‌​‌‌​​​‌‌​​​​‌​‌‌‌​​‌​​‌‌​​​​‌​‌‌​​​‌​​‌‌‌‌​​‌​​‌‌​‌​‌​​‌‌​​‌​​​‌‌​‌‌‌​‌‌‌‌‌​​​‌‌​​​​‌​‌‌​‌​​‌​​‌​‌‌​‌​‌‌‌​​​​​‌‌​‌‌​‌​​‌​‌‌​‌​‌‌‌​​‌‌​‌‌​‌​‌‌​‌‌​‌​​‌​‌‌​‌‌​​​‌‌​‌‌​​​‌‌‌​​‌‌​‌‌‌‌‌​​​​‌‌​​‌​​​‌‌​​​​​​‌‌​​‌​​​‌‌​‌‌​​​‌​‌‌​‌​​‌‌​​​‌​​‌‌​​​​​​‌​‌‌​‌​​‌‌​​‌​​​‌‌​‌​​
