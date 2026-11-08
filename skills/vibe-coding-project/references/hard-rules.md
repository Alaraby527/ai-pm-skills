# 硬规则与自查命令

> 本文件是 `SKILL.md` 第 4 节「硬规则」的展开。
>
> **为什么需要这一节**：六阶段方法论靠自觉执行，但「自觉」在长会话里会失效。
> 这里把能机械判定的规则写成**你可以自己跑的检查命令**，把不能机械判定的写成
> **必须停下来问用户**的关卡。开工前跑一遍，收尾前再跑一遍。

---

## 0. 目录契约

本 skill 假设项目里用这套约定。如果你在别的项目里用，先按这套建目录：

```
<项目根>/
├── AGENTS.md                     # 项目规则（技术栈锁定 + 不可变约定）
├── specs/<slug>/                 # 每个功能一份规格
│   ├── spec.md                   # 五节：问题/需求/验收标准/不做清单/自动化边界
│   ├── plan.md                   # 七层方案
│   ├── tasks.md                  # 复选框任务
│   ├── .active                   # 激活标记（恰好一个规格有它）
│   ├── .phase                    # 当前阶段（requirements/design/mvp/testing/bugfix/delivery）
│   └── .accepted-<阶段>          # 人工验收标记
├── docs/
│   ├── smoke-report.md           # 只读冒烟报告
│   └── regression-report.md      # 回归证据
├── apps/api/                     # 后端
├── apps/web/                     # 前端
└── packages/contracts/           # 唯一允许两端共享的层
```

**为什么要有 `.active` 和 `.phase`**：AI 没有跨会话记忆。这两个文件让下一个会话
（或下一个 agent）能立刻知道自己处在哪一步，而不是重新猜。

---

## 1. 九条硬规则

每条都给出「规则 → 怎么自查 → 不通过怎么办」。

### 规则 1：规格先行

**规则**：写 `apps/api`、`apps/web`、`packages/contracts` 里的任何文件之前，必须存在
**恰好一个**活跃规格（`specs/<slug>/` 三件套齐全 + `.active`）。

**自查**：
```bash
ls specs/*/.active 2>/dev/null | wc -l    # 必须是 1
```

**不通过**：先建规格，不要「先写点代码试试」。试出来的代码会变成需要清理的技术债。

---

### 规则 2：spec.md 必须五节齐全

**规则**：`spec.md` 必须含这五个二级标题：

1. `## Problem` — 谁、什么场景、什么痛点
2. `## Requirements` — 要做什么
3. `## Acceptance Criteria` — 怎么算做完
4. `## 不做清单` — 第一版明确不做什么
5. `## 自动化边界` — 哪些能自动做、哪些必须人工决定

**自查**：
```bash
f=specs/<slug>/spec.md
for h in "Problem" "Requirements" "Acceptance Criteria" "不做" "自动化边界"; do
  grep -qE "^## .*${h}" "$f" && echo "ok   $h" || echo "MISS $h"
done
```

**不通过**：补齐缺的节。第 4、5 节最容易被跳过，但恰恰是这两节最能减少后续扯皮。

---

### 规则 3：plan.md 必须覆盖七层

**规则**：`plan.md` 必须逐层回答，缺一层不算完成：

数据层 / 评测层（或核心业务层）/ 执行层 / 异常层 / 展示层 / 改进产物层 / 风险层

**自查**：
```bash
grep -oE "数据层|评测层|核心业务层|执行层|异常层|展示层|改进产物层|风险层" \
  specs/<slug>/plan.md | sort -u | wc -l    # 应该是 7
```

**不通过**：补缺的层。缺哪层就写「缺」，不要用合理猜测填满——猜出来的方案会在
实现阶段反噬。

---

### 规则 4：AGENTS.md 必须固化不可变约定

**规则**：项目根目录必须有 `AGENTS.md`，且含 `## 不可变约定` 一节，写死技术栈、
目录结构、字段命名、状态枚举、端口路由。

**自查**：
```bash
test -f AGENTS.md && echo "ok 存在" || echo "MISS AGENTS.md"
grep -q "不可变约定" AGENTS.md && echo "ok 有不可变约定" || echo "MISS 不可变约定"
grep -nE "建议|可以考虑|视情况" AGENTS.md && echo "WARN 有软表达" || echo "ok 无软表达"
```

**不通过**：补写。规则里出现「建议」「可以考虑」等于没写——AI 会按自己的理解补。

---

### 规则 5：不留占位符

**规则**：`spec.md`、`plan.md`、`AGENTS.md` 里不得出现 `TODO`、`TBD`、`FIXME`、
「待确认」「待补充」。未确认的事写进「开放问题」一节并说明卡在哪。

**自查**：
```bash
grep -nE "TODO|TBD|FIXME|待确认|待补充" specs/<slug>/*.md AGENTS.md
```

**不通过**：把占位符换成具体问题，去问用户。

---

### 规则 6：三层验收，缺一不可

**规则**：MVP 阶段每个模块完成后，必须展示三层证据，用户确认后才能提交：

| 层 | 要展示什么 | 标记文件 |
|---|---|---|
| 状态层 | 后端测试输出 + 前端 build 输出 + 启动无阻塞错误 | `.accepted-mvp-state` |
| 内容层 | 数据库真实行数 + 错误表明细 + 输入=成功+失败 的对账 | `.accepted-mvp-content` |
| 页面链路层 | 从首页走完整链路 + 页面数字=API=数据库 + 截图 | `.accepted-mvp-page` |

**自查**：
```bash
for m in mvp-state mvp-content mvp-page; do
  test -f "specs/<slug>/.accepted-$m" && echo "ok   $m" || echo "MISS $m"
done
```

**不通过**：缺哪层补哪层证据。**不要自己创建 `.accepted-*` 标记**——标记的意义是
「用户看过证据并同意」，自己发通行证等于没验收。

---

### 规则 7：冒烟阶段只读

**规则**：项目测试阶段只记录问题，不改代码。用 `.smoke-lock` 标记锁住自己。

**自查**：
```bash
# 冒烟期间，工作区不应有未提交的源码改动
git status --porcelain apps/ packages/ | grep -v "^$" && echo "WARN 冒烟期间改了源码" || echo "ok 只读"
```

**不通过**：把发现写进 `docs/smoke-report.md`，等用户确认后再进 Bug 改进阶段修复。

---

### 规则 8：前后端分离

**规则**：前端不得 import 后端，后端不得 import 前端。跨端只走 `packages/contracts`。

**自查**：
```bash
# 前端里出现后端路径
grep -rnE "from ['\"].*(apps/api|/api/)" apps/web/src --include=*.ts --include=*.tsx --include=*.js 2>/dev/null
# 后端里出现前端路径
grep -rnE "from ['\"].*(apps/web|/web/)" apps/api --include=*.py --include=*.ts --include=*.js 2>/dev/null
```

**不通过**：把共享类型搬到 `packages/contracts`，两端都从契约导入。

---

### 规则 9：Git 纪律

**规则**：

- 只在 `feat/<slug>` 分支工作，不在 main / master / develop 上提交
- 一个 commit 只做一件事
- `git add` 指定文件，不用 `git add .`
- 不擅自 push、不擅自合并
- 不用 `git push --force`（确需覆盖用 `--force-with-lease`）

**自查**：
```bash
git branch --show-current                    # 不能是 main/master/develop
git status --porcelain | wc -l               # 提交前确认改动范围符合预期
grep -c "^- \[ \]" specs/<slug>/tasks.md     # 应该是 0（任务全勾）
```

**不通过**：建功能分支；把未完成任务做完并勾选。

---

## 2. 破坏性操作清单

以下命令**不要执行**，即使看起来能解决问题：

| 命令 | 风险 |
|---|---|
| `rm -rf` 指向 `/`、`~`、`..`、工作目录外 | 不可逆删除 |
| `git reset --hard` | 丢弃工作区改动 |
| `git clean -fdx` | 删除未跟踪文件 |
| `git checkout .` / `git restore .` | 丢弃全部工作区改动 |
| `chmod -R 777` | 放开全部权限 |
| `dd if=` | 直写磁盘 |
| `mkfs*` | 格式化文件系统 |
| `shutdown` / `reboot` | 关机重启 |

**遇到这类需求，停下来告诉用户，让用户自己执行。**

---

## 3. 开工前 / 收尾前检查清单

### 开工前（每个会话开始）

```bash
echo "=== 活跃规格 ==="; ls specs/*/.active 2>/dev/null
echo "=== 当前阶段 ==="; cat specs/*/.phase 2>/dev/null
echo "=== 当前分支 ==="; git branch --show-current
echo "=== 未完成任务 ==="; grep -c "^- \[ \]" specs/*/tasks.md 2>/dev/null
echo "=== 占位符 ==="; grep -nE "TODO|TBD|FIXME|待确认|待补充" specs/*/*.md AGENTS.md 2>/dev/null
```

### 提交前

```bash
# 1. 任务全勾了吗
grep -c "^- \[ \]" specs/<slug>/tasks.md     # 必须是 0

# 2. 三层验收齐了吗（MVP 阶段）
ls specs/<slug>/.accepted-mvp-* 2>/dev/null

# 3. 分支对吗
git branch --show-current

# 4. 改动范围符合预期吗
git status --porcelain

# 5. 有没有把不该提交的东西带上
git diff --cached --name-only | grep -E "\.env|node_modules|\.pem|\.key" && echo "WARN 敏感文件"
```

### 交付前

```bash
# 每条结论都要有证据：测试输出、数据库查询结果、页面截图、commit hash
git log --oneline -5
git status --porcelain          # 确认工作区干净或说明未提交原因
```

---

## 4. 常见借口与对应事实

| 你会想说的话 | 事实 |
|---|---|
| 「先写点代码试试，回头补规格」 | 试出来的代码要清理，成本比先写规格高 |
| 「测试通过了就算完成」 | 测试通过 ≠ 功能完成，接口 200 ≠ 验收通过 |
| 「这个我可以自己判断」 | 涉及产品决策、字段命名、状态枚举的，必须问用户 |
| 「先提交再说，回头改」 | 未验收的代码进历史会污染回滚点 |
| 「用户应该不会在意这个」 | 你在替用户做产品决策，停下来问 |
| 「我知道根因，直接改」 | 根因没验证清楚就改，是在赌 |
| 「换条路径能跑通就行」 | 回归必须沿原路径，否则等于没验证 |
| 「这次先跳过验收」 | 三层验收是门禁，不是可选项 |

---

## 5. 这套规则什么时候可以放宽

| 场景 | 可以放宽的部分 | 不能放宽的部分 |
|---|---|---|
| 一次性脚本、探索性代码 | 规格、任务拆分、三层验收 | 破坏性操作禁令、文件边界 |
| 纯文档项目 | 七层方案、三层验收 | 需求对齐、不做清单 |
| 无前端的项目 | 页面链路层、前后端分离 | 状态层、内容层 |
| 紧急线上修复 | 完整规格 | 根因诊断、原路径回归、分支纪律 |

**原则**：可以少写文档，但不能跳过「想清楚」和「验证过」。
