# AI PM SkillKit

> 面向 AI 产品经理的工程化 Skill 工具包：把研究、设计、分析、审核、求职和日常表达拆成可独立调用的 Skill，并用 Workflow 串成完整项目闭环。

[![GitHub](https://img.shields.io/badge/GitHub-Alaraby527%2Fai--pm--skills-181717?logo=github)](https://github.com/Alaraby527/ai-pm-skills)

## 这是什么

AI PM SkillKit 不是零散的 Prompt，而是一套按工作职责组织的 AI 产品经理工具箱。当前保留 17 个独立 Skill 和 1 个项目 Workflow。

每个 Skill 都包含：

- 触发条件：什么时候使用
- 输入要求：需要提供什么材料
- 工作流程：先做什么、再做什么
- 产出定义：最终应该得到什么
- 质量检查：如何判断结果是否合格
- references：模板、案例或方法论补充

## 按工作职责选择 Skill

### 1. 研究与信息收集

| Skill | 主要用途 |
|---|---|
| [user-interview](skills/user-interview/SKILL.md) | 用户访谈、5Why 追问、洞察和用户画像 |
| [survey-questionnaire](skills/survey-questionnaire/SKILL.md) | 问卷设计、用户分层、交叉分析 |
| [usability-testing](skills/usability-testing/SKILL.md) | 可用性测试、任务脚本、问题清单 |
| [competitive-research](skills/competitive-research/SKILL.md) | 竞品调研、竞品矩阵和机会点 |

### 2. 需求与方案设计

| Skill | 主要用途 |
|---|---|
| [ai-requirements-analysis](skills/ai-requirements-analysis/SKILL.md) | AI 需求澄清、可行性评估、MVP 和 PRD |
| [dialogue-strategy-designer](skills/dialogue-strategy-designer/SKILL.md) | 客服、销售、运营等场景的对话策略 |
| [prompt-writing](skills/prompt-writing/SKILL.md) | Prompt 结构、任务模板、调试和优化 |

### 3. 数据与产品分析

| Skill | 主要用途 |
|---|---|
| [data-analysis](skills/data-analysis/SKILL.md) | 指标、漏斗、用户分层和异常诊断 |
| [product-experience-report](skills/product-experience-report/SKILL.md) | 产品体验、五要素和体验问题分析 |

### 4. 审核、评估与质量控制

这一类 Skill 的主要职责是检查成果是否达标、证据是否充分、风险是否可控，不是单纯从零生成内容。

| Skill | 主要用途 |
|---|---|
| [ai-product-portfolio-review](skills/ai-product-portfolio-review/SKILL.md) | 审核 AI PM 作品集、项目案例、项目证据、成熟度和表达质量 |
| [skill-quality-checker](skills/skill-quality-checker/SKILL.md) | 审核 Skill 的触发条件、结构、工作流、边界和完整性 |

### 5. 求职与面试执行

| Skill | 主要用途 |
|---|---|
| [interview-prep](skills/interview-prep/SKILL.md) | 项目深挖、行业认知、行为题和模拟面试准备 |
| [interview-retro](skills/interview-retro/SKILL.md) | 面试复盘、问题归因、漏斗诊断和改进清单 |
| [resume-jd-align](skills/resume-jd-align/SKILL.md) | 简历与 JD 对齐、关键词匹配和项目描述优化 |

### 6. 日常工作与内容表达

| Skill | 主要用途 |
|---|---|
| [daily-report](skills/daily-report/SKILL.md) | 工作日报、效果、问题处理、卡点和明日计划 |
| [script-polish](skills/script-polish/SKILL.md) | 汇报稿、口播稿、视频脚本和表达润色 |

### 7. Skill 开发与维护

| Skill | 主要用途 |
|---|---|
| [skill-creator](skills/skill-creator/SKILL.md) | 创建 Skill、设计触发条件、输入输出和异常兜底 |

## 项目 Workflow

[AI PM 项目闭环 Workflow](workflows/ai-pm-project-workflow/SKILL.md) 用于编排多个 Skill：

```text
研究真实问题
→ 验证用户需求
→ 判断是否使用 AI
→ 研究竞品与替代方案
→ 设计产品和 Prompt
→ 跑通工作流
→ 数据评测与迭代
→ 作品集审核与交付
```

单个 Skill 可以独立使用；需要完成完整 AI 产品项目时，优先从 Workflow 入口开始。

## 目录结构

```text
ai-pm-skills/
├── README.md
├── skills/
│   ├── 研究与信息收集
│   │   └── user-interview / survey-questionnaire / usability-testing / competitive-research
│   ├── 需求与方案设计
│   │   └── ai-requirements-analysis / dialogue-strategy-designer / prompt-writing
│   ├── 数据与产品分析
│   │   └── data-analysis / product-experience-report
│   ├── 审核与质量控制
│   │   ├── ai-product-portfolio-review
│   │   └── skill-quality-checker
│   ├── 求职与面试执行
│   │   └── interview-prep / interview-retro / resume-jd-align
│   ├── 日常工作与内容表达
│   │   └── daily-report / script-polish
│   └── Skill 开发与维护
│       └── skill-creator
├── workflows/
│   └── ai-pm-project-workflow/
└── dist/
```

> 上面的分类是 README 导航分类；实际 GitHub 目录仍保持 `skills/<skill-name>/` 平铺，避免影响现有加载路径。

## 源码与打包状态

当前 `dist/` 中有 10 个已打包文件，均与当前保留的源码或 Workflow 对应。

以下 Skill 当前有源码，但还没有对应的 `.skill` 包：

```text
ai-product-portfolio-review
daily-report
interview-prep
interview-retro
prompt-writing
resume-jd-align
script-polish
skill-quality-checker
```

打包文件只是安装产物，源码目录中的 `SKILL.md` 才是维护入口。新增或修改 Skill 后，应同步更新 README 和对应打包文件。

## 使用方式

### 阅读源码

```bash
git clone https://github.com/Alaraby527/ai-pm-skills.git
cd ai-pm-skills
```

每个 Skill 的入口都是 `SKILL.md`。需要补充模板或案例时，再读取对应的 `references/`。

### 安装打包文件

进入 [dist/](dist/) 目录，选择需要的 `.skill` 文件，在支持 Skill 导入的平台中安装。

### 项目模式

如果任务包含完整的 AI 产品项目，建议使用：

```text
ai-pm-project-workflow
```

由 Workflow 按阶段调用研究、设计、分析和审核类 Skill。

## 设计原则

1. 先问题，后工具。
2. 先闭环，后炫技。
3. 先证据，后结论。
4. Demo 不等于生产产品。
5. 没有数据时标记待补，不编造用户、指标或上线结果。
6. 每个 Skill 独立可用，组合后形成项目闭环。
7. 审核类 Skill 负责发现问题和判断质量，不与内容生成类 Skill 混为一类。

## 贡献与迭代

改进 Skill 时，请同步检查：

- 触发条件是否清楚
- 输入和输出是否定义
- 工作流程是否完整
- 异常情况是否有兜底
- references 链接是否有效
- README 分类和数量是否同步
- 是否需要重新生成 `dist/` 打包文件

## 许可证

方法论、模板和案例应结合具体业务、数据权限和风险边界使用。许可证信息以仓库中的实际声明为准。
