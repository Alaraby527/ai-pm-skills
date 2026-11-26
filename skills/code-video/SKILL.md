---
name: code-video
description: 用代码（HTML/React）把内容渲染成视频并导出 MP4，而不是用 AI 视频模型生成画面。基于 HyperFrames（HTML + data-* 时间轴 + GSAP）或 Remotion（React 组件 + useCurrentFrame）两套框架，覆盖需求归一、知识稿、分镜表、视觉令牌、样片、全片渲染的完整流水线，内置可直接跑的环境自检、建工程、渲染校验脚本和两套已验证模板。当用户要：用代码/前端/HTML/React 做视频、程序化生成视频、把文章或脚本或 PPT 转成视频、批量模板化出片、导出 MP4、用 Remotion 或 HyperFrames、做文字与图表密集的科普/数据/产品介绍视频时使用。也用于排查这类流水线里的典型故障：渲染出来全静止、文字模糊或字体被替换、图片空白、时长对不上。
---

# 代码生成视频

## 这是什么

视频不是「生成的画面」，是**算出来的画面**。每一帧都是帧号的纯函数：渲染器跳到第 N 帧、把网页画出来、截一张图，再用 ffmpeg 拼成 MP4。所以文字永远清晰、图表永远是矢量、改一个字重渲染即可。

和 AI 视频模型的分工：模型负责出插画或实拍感素材，代码负责排版、时间轴和动效。两者可以混用，但不要把这条流水线当成「自动生成画面」。

## 选哪套框架

| 情况 | 选择 |
|---|---|
| 文字、图表、流程图为主，要快出片，团队不熟 React | **HyperFrames** |
| 复杂动效、数据驱动、要复用现有 React 组件库 | **Remotion** |
| 透明通道、Three.js 三维、逐帧精确控制 | Remotion |
| 同一模板批量产 N 条（换文案换数据） | Remotion（props 驱动） |
| 只需要一段 10 秒的验证样片 | HyperFrames（起工程最快） |

默认先 HyperFrames，卡住了再换 Remotion。两套模板是**同一支片子**，出片视觉一致，可以随时对照迁移。

## 三步上手

命令都在本 Skill 目录下执行（脚本路径相对 SKILL.md 所在目录）。

```bash
# 1. 环境自检 + 自动补齐（ffmpeg/ffprobe 走 npm 静态二进制，Chrome 走 hyperframes）
python3 scripts/bootstrap.py            # 只检查加 --check

# 2. 从模板起工程
python3 scripts/new_project.py /path/to/film --stack hyperframes
python3 scripts/new_project.py /path/to/film --stack remotion --install

# 3. 出片并抽帧验收
python3 scripts/render.py /path/to/film -q draft  --start 0 --end 10 --stills 1.5,6.5
python3 scripts/render.py /path/to/film -q delivery
```

`render.py` 自动识别工程类型、自己补 PATH、渲染后会用 ffprobe 校验时长/分辨率/帧率/体积，并打印关键帧路径供肉眼验收。渲染成功不等于片子对，**必须看抽出来的帧**。

## 工作流（细节见 references/workflow.md）

1. **需求归一**：题材、受众、时长、画幅、语言、音轨、用途，一次问齐。
2. **知识稿**：写成事实卡片（主张 / 怎么可视化 / 出处 / 易误解点），没有出处的不进片子。
3. **分镜表**：序号、入点、出点、屏幕文字、旁白、视觉模式、素材。这是唯一真相来源，代码是它的实现。
4. **视觉令牌**：先定一套主题（`references/visual-system.md`），**先出一张静态样图确认**，再批量做。
5. **样片**：只做信息最密的那 10-20 秒，不满意就改令牌，不要在单屏上反复微调。
6. **全片 + 抽帧验收**。

分镜表模板、四类提示词骨架、失败模式对照表都在 `references/workflow.md`。

## 硬性工程约束（写代码时必须满足）

1. **禁止实时动画**：不能出现 `setTimeout`、`requestAnimationFrame`、CSS `transition`/`@keyframes`。渲染是逐帧截图，不播时间。动画只能由时间轴或帧号显式计算。
2. **时间轴单一真相**：HyperFrames 一个 paused GSAP timeline；Remotion 一个 `durationInFrames` + 若干 `Sequence`。场景时长对齐整秒（30fps 下 4s = 120 帧）。
3. **字体先加载再渲染**：HyperFrames 用 Google Fonts `<link>`（系统字体只在本机能用，`lint` 会报错）；Remotion 用 `delayRender`/`continueRender` 等 `document.fonts.load()`。
4. **中文用 DOM/SVG 排版**，不要画进 canvas，会糊。
5. **素材落本地**，相对工程路径，不要远程 URL 和绝对路径；远程图会在加载完成前被截成空白。
6. **纯函数**：不用 `Math.random()`（Remotion 用 `random(seed)`）、不用 `Date.now()`、不靠组件内累积状态。

## 验收清单

- `lint` / `check` 报 0 error（HyperFrames 的 `timeline_track_too_dense` 是 warning，可接受）
- 时长与分镜表一致（±0.1s）、分辨率帧率符合需求
- 抽 3-5 帧看：文字在安全区内、没溢出、没贴边
- 中文字形正确，没被 fallback 替换（宋体变黑体是典型症状）
- 深色底正文不低于 `#8C9099` 的亮度
- 有音频时人声与字幕对齐，结尾不截断

## 参考与资源

- `references/workflow.md` — 六步流程、分镜表模板、提示词骨架、失败模式对照
- `references/hyperframes.md` — data-* 契约、GSAP 用法、CLI 参数、五个必踩的坑
- `references/remotion.md` — 组件模型、动画 API、字体闸门、CLI 参数、六个坑
- `references/visual-system.md` — 三套主题令牌、版式常量、动效参数表、七种画面模式
- `assets/hyperframes-starter/index.html` — 12s / 1080p / 30fps / lint 0 error 的成品模板
- `assets/remotion-starter/` — 同一条片子的 Remotion 实现，含字体加载闸门
- `scripts/bootstrap.py`、`scripts/new_project.py`、`scripts/render.py` — 均已实测
