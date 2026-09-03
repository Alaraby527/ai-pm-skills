# AI PM SkillKit

> 面向 AI 产品经理的工程化方法论 Skill 工具包：把用户研究、产品设计、数据分析和职业发展，拆成可直接调用的 Skill、Workflow、模板、提示词与案例。

[![GitHub](https://img.shields.io/badge/GitHub-Alaraby527%2Fai--pm--skills-181717?logo=github)](https://github.com/Alaraby527/ai-pm-skills)

## 这是什么

AI PM SkillKit 不是一组零散的 Prompt，而是 15 个可以独立使用的 AI 产品经理 Skill，以及 1 个将它们串成项目闭环的 Workflow。每个 Skill 都明确：

- **什么时候用**：用触发词快速定位方法
- **先做什么、再做什么**：按步骤推进，而不是直接生成结论
- **产出什么**：提供模板、提示词和案例作为交付标准
- **如何判断质量**：把常见遗漏、误区和校验点前置

它适合用来完成用户研究、需求分析、竞品拆解、体验复盘、数据诊断、方案验证和职业发展准备。

## Skill 总览

下表同时说明每个 Skill 的**中文名、英文目录名、适用问题和选择时机**。通常不需要逐个判断 Skill 怎么选：先看你当前要解决的问题，再沿着[项目闭环 Workflow](workflows/ai-pm-project-workflow/SKILL.md)自动串联必需步骤。

| 类别 | 中文名 | 英文目录名 | 什么时候用 | 主要产出 |
|---|---|---|---|---|
| 用户研究 | 用户访谈 | [`user-interview`](skills/user-interview/SKILL.md) | 还不清楚用户真实问题、行为和工作流时 | 访谈提纲、5Why 追问、洞察、用户画像 |
| 用户研究 | 调研问卷设计 | [`survey-questionnaire`](skills/survey-questionnaire/SKILL.md) | 需要扩大样本、验证假设或比较用户群体时 | 问卷、信效度检查、交叉分析、用户分层 |
| 用户研究 | 可用性测试 | [`usability-testing`](skills/usability-testing/SKILL.md) | 已有原型或 Demo，需要发现任务卡点时 | 测试方案、任务脚本、问题清单、SUS 结果 |
| 产品设计 | AI 需求分析 | [`ai-requirements-analysis`](skills/ai-requirements-analysis/SKILL.md) | 需求模糊，需要判断是否值得做、为什么用 AI 时 | 需求澄清、AI 可行性判断、MVP、PRD |
| 产品设计 | 产品体验报告 | [`product-experience-report`](skills/product-experience-report/SKILL.md) | 需要系统拆解一个产品的体验和问题时 | 五要素体验分析、问题定位、优化建议 |
| 产品设计 | 竞品调研 | [`competitive-research`](skills/competitive-research/SKILL.md) | 需要比较竞品、替代方案和差异化空间时 | 竞品地图、功能矩阵、体验对比、机会点 |
| 数据分析 | 数据分析 | [`data-analysis`](skills/data-analysis/SKILL.md) | 指标异常、漏斗下滑、用户表现分化或需要复盘时 | 指标体系、事件/漏斗分析、用户分层、异常诊断 |
| 对话设计 | 对话策略设计 | [`dialogue-strategy-designer`](skills/dialogue-strategy-designer/SKILL.md) | 需要根据业务场景设计销售、客服、外呼或服务对话时 | 对话战略地图、阶段化话术、异议处理、情绪分支 |
| 求职发展 | AI 产品经理求职兵法 | [`ai-pm-job-hunting`](skills/ai-pm-job-hunting/SKILL.md) | 需要整体规划 AI PM 求职准备时 | 求职规划、项目表达、投递策略、面试准备 |
| 求职发展 | 简历-JD 对齐 | [`resume-jd-align`](skills/resume-jd-align/SKILL.md) | 需要根据目标岗位重构简历和项目描述时 | JD 关键词、简历体检、项目描述、自我评价 |
| 求职发展 | 面试备战 | [`interview-prep`](skills/interview-prep/SKILL.md) | 需要准备项目深挖、行业认知、行为和费米估算题时 | 答题框架、模拟面试、分轮次准备方案 |
| 求职发展 | 面试复盘 | [`interview-retro`](skills/interview-retro/SKILL.md) | 面试未通过或需要定位求职转化短板时 | 面试还原、漏斗诊断、问题定位、改进清单 |
| 求职发展 | 逐字稿打磨 | [`script-polish`](skills/script-polish/SKILL.md) | 已有面试录音或逐字稿，需要优化表达时 | 逐句诊断、结构化回答、多时长版本 |
| 质量治理 | Skill 质量检测 | [`skill-quality-checker`](skills/skill-quality-checker/SKILL.md) | 需要审计 Skill 的可调用性、规范性和完整性时 | 质量评分、问题清单、改进方案、差距分析 |
| 日常管理 | 工作日报 | [`daily-report`](skills/daily-report/SKILL.md) | 需要整理每日工作进展、效果、问题处理、卡点和明日计划时 | 结构化日报、问题处理、学习内容融合、明日计划 |

### 固定流程：封装为一个 Workflow

这条固定路径本质上是“**从真实问题到 AI 产品交付**”的项目闭环，因此已封装为一个可复用 Workflow，而不是要求使用者手动串联 14 个 Skill：

[**AI PM 产品项目闭环 Workflow →**](workflows/ai-pm-project-workflow/SKILL.md)

```text
发现真实问题 → 验证问题 → 判断是否用 AI → 研究已有方案
      → 跑通并测试核心工作流 → 数据复盘与迭代 → 输出 PRD/报告/迭代计划
```

Workflow 会按需调用对应 Skill：

- **必经主链路**：用户访谈 → AI 需求分析 → 可用性测试 → 数据分析
- **可选增强**：调研问卷、竞品调研、产品体验报告
- **职业发展场景**：需要简历、投递或面试准备时，再使用 AI 产品经理求职兵法

因此，单个 Skill 仍然可以独立使用；当任务是完整项目时，优先调用 Workflow，由 Workflow 负责阶段编排、材料复用和质量检查。
## 安装与使用

### 方式一：下载 `.skill` 文件

1. 进入 [`dist/`](dist/) 目录，选择需要的 `.skill` 文件。
2. 在支持 Skill 导入的平台中上传并安装。
3. 使用自然语言触发，例如：

```text
帮我为一款企业知识库助手设计 5 位目标用户的访谈提纲，并给出 5Why 追问问题。

请分析这个 AI 客服需求是否真的需要大模型，输出 MVP、AI 参与模式和失败兜底方案。

DAU 连续两周下降，请用事件、漏斗和用户分层三个视角诊断可能原因。
```

### 方式二：阅读源码或接入自己的 Agent

```bash
git clone https://github.com/Alaraby527/ai-pm-skills.git
cd ai-pm-skills
```

每个 Skill 或 Workflow 的入口都是 `SKILL.md`。可以单独阅读，也可以从 Workflow 入口开始，让它按阶段调用各个 Skill；根据团队规范修改后即可重新打包。

### 重新打包

在 `skills/` 或 `workflows/` 目录下执行：

```bash
zip -r ../dist/<skill-name>.skill <skill-name>/
```

Windows PowerShell：

```powershell
Compress-Archive -Path .\<skill-name> -DestinationPath ..\dist\<skill-name>.skill -Force
```

## 目录结构

```text
ai-pm-skills/
├── README.md                              # 使用说明、Skill 总览与 Workflow 导航
├── skills/                                # 可独立调用的 Skill 源码
│   ├── user-interview/
│   │   ├── SKILL.md                       # 触发条件、工作流、质量要求
│   │   └── references/                    # 模板、提示词、案例
│   ├── survey-questionnaire/
│   ├── usability-testing/
│   ├── ai-requirements-analysis/
│   ├── product-experience-report/
│   ├── competitive-research/
│   ├── data-analysis/
│   ├── ai-pm-job-hunting/
│   ├── dialogue-strategy-designer/
│   ├── interview-prep/
│   ├── interview-retro/
│   ├── resume-jd-align/
│   ├── script-polish/
│   └── skill-quality-checker/
├── workflows/                             # 跨 Skill 的固定工作流
│   └── ai-pm-project-workflow/
│       └── SKILL.md                       # AI PM 产品项目闭环编排
├── dist/                                  # 可上传安装的 .skill 包
└── .gitignore
```

每个 Skill 遵循相同的阅读顺序：

1. 先看 `SKILL.md`：确认触发条件、输入信息和完整工作流；完整产品项目优先从 `workflows/` 入口开始。
2. 再看 `references/`：选择对应模板、提示词或案例。
3. 最后按质量检查项复核结果：不要只复制结论，要保留证据和决策过程。

## 用本工具包完成一个完整的 AI 产品项目

本节是通用的产品质量检查，不限定项目用途。无论是需求立项、原型验证、上线迭代、内部评审还是业务复盘，都应该优先保留判断、证据和修正过程，而不是只展示工具截图。

### 每个 AI 产品项目至少留下 6 类证据

- **问题证据**：访谈了谁、观察到什么行为、问题发生在哪个环节。
- **技术选择**：为什么需要大模型，而不是搜索、规则、表单或普通自动化。
- **工作流**：用户输入什么、模型调用什么数据/工具、哪里需要人工确认、失败如何回退。
- **评测证据**：准备小型测试集，记录任务完成率/准确性/耗时/成本及典型错误。
- **失败案例**：展示幻觉、遗漏条件、误解意图等真实失败，并说明如何修正。
- **迭代结果**：保留版本对比，说明改了什么、指标变化是什么、还有什么未解决。

### 推荐的 AI 产品项目六段结构

1. **业务背景**：具体、真实、可量化的痛点。
2. **用户场景**：明确目标用户，只聚焦一个核心场景。
3. **人机方案**：定义 AI 与人的分工、人工确认点和风险边界。
4. **AI 专项设计**：模型选型、Prompt、知识库/RAG、上下文、工具调用。
5. **流程闭环**：输入 → 智能处理 → 输出 → 异常兜底/故障恢复。
6. **量化复盘**：准确率、响应时间、Token 成本、转化/留存等指标，以及迭代前后对比。

### 交付前自检清单

- [ ] 有真实问题来源，而不是只有“用户有痛点”的判断。
- [ ] 解释了为什么用 AI，以及不用 AI 的替代方案是什么。
- [ ] 不是简单的“输入 → 模型回答”，而是完整业务工作流。
- [ ] 有测试集、量化指标和至少一个失败案例。
- [ ] 有至少一轮迭代，并保留修改前后的对比。
- [ ] 写清上下文、工具调用、人工确认和异常兜底边界。
- [ ] 重点突出核心含金量模块，而不是堆砌多个半成品。
- [ ] 数据、用户反馈和案例均标注来源；没有真实数据时明确说明假设。
- [ ] 交付物与使用场景匹配：可以是 PRD、体验报告、评测报告、迭代计划或汇报材料。
- [ ] 删除只展示工具操作、复杂特效和无关截图的内容。
## 设计原则

1. **先问题，后工具**：先证明问题真实，再讨论模型、框架和 Prompt。
2. **先闭环，后炫技**：优先把输入、处理、输出、异常和人工协同跑通。
3. **先证据，后结论**：所有关键判断都尽量留下访谈、测试、数据或版本对比。
4. **不把 Demo 当产品**：能运行只代表功能存在，不代表用户需要或业务有效。
5. **允许不确定性**：没有数据时标注假设，不编造用户、指标和上线结果。
6. **独立可用，组合增益**：每个 Skill 可以单独使用，也可以按项目阶段串联。

## 贡献与迭代

欢迎通过 Issue 或 Pull Request 参与改进：

- 修正方法论、模板或示例中的错误
- 补充真实业务场景与失败案例
- 增加适用于 AI 产品的评测、Agent、人机协同内容
- 优化 Skill 的触发条件、输入要求和输出质量检查

贡献前请尽量保持以下原则：

- 不堆砌概念，每个方法都要能落到步骤、模板或可验证产出。
- 不用虚构数据包装案例；示例应明确标注为示例或假设。
- 保持每个 Skill 的边界清晰，避免多个 Skill 重复解决同一问题。
- 更新 Skill 后同步更新本 README 的目录、用途与使用示例。

## 说明与许可证

- 本工具包的方法论来自 AI 产品经理实践经验与行业常用方法的整理，适合作为工作起点，请结合具体业务判断。
- 模板、提示词和案例应根据团队规范、数据权限和业务风险进行调整。
- 许可证信息以仓库根目录中的 `LICENSE` 文件为准；如需商业分发，请先确认仓库当前许可证声明。

---

如果你发现 Skill 的触发条件、模板或案例存在问题，欢迎在 [Issues](https://github.com/Alaraby527/ai-pm-skills/issues) 中反馈。







