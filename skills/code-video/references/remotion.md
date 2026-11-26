# Remotion 模式

React 组件就是视频。画面是 `f(帧号)` 的返回值，`useCurrentFrame()` 给你当前帧，剩下的交给 CSS 和你的数学。

## 最小工程

```
project/
├── package.json          # remotion + @remotion/cli + react
├── tsconfig.json
├── remotion.config.ts    # 输出格式、质量、覆盖策略
└── src/
    ├── index.ts          # registerRoot
    ├── Root.tsx          # <Composition> 定义画幅/帧率/时长
    ├── theme.ts          # 设计令牌，色值只写在这里
    ├── fonts.tsx         # 字体加载闸门
    └── Main.tsx          # 主时间轴 + 各场景组件
```

## 三个核心 API

```tsx
// 1. 定义一条片子
<Composition id="Main" component={Main}
  durationInFrames={360} fps={30} width={1920} height={1080} />

// 2. 拿时间
const frame = useCurrentFrame();          // 0 … durationInFrames-1
const { fps, durationInFrames } = useVideoConfig();

// 3. 把时间换算成画面参数
const opacity = interpolate(frame, [0, 30], [0, 1], { extrapolateRight: "clamp" });
const scale = spring({ frame: frame - 6, fps, config: { damping: 18, mass: 0.8 } });
```

`Sequence` 用来切场景，`from` 是绝对帧：

```tsx
<Sequence from={0}   durationInFrames={120}><SceneCover /></Sequence>
<Sequence from={120} durationInFrames={120}><SceneDiagram /></Sequence>
```

`AbsoluteFill` 是铺满画布的定位容器。素材用 `staticFile("audio/bgm.mp3")` 从 `public/` 取。

## 铁律：每一帧都是纯函数

渲染器是「跳到第 N 帧、渲染、截图」，它不会先播 0…N-1 帧。所以任何跨帧累积的状态都会错：

| 禁止 | 原因 | 替代 |
|---|---|---|
| `setTimeout` / `setInterval` | 截图时不执行 | 用 `frame` 算 |
| `requestAnimationFrame` | 同上 | 用 `spring` / `interpolate` |
| CSS `transition` / `@keyframes` | 截图时处于起始态 | 内联 style + 帧插值 |
| `Math.random()` | 每帧不同，画面抖动 | `random(seed)`，同 seed 同值 |
| `Date.now()` | 每帧不同 | 用帧号 |
| 组件内 `useState` 累积 | 渲染顺序不保证 | 由 props / 帧号推导 |

动画本质是 `frame → 样式` 的一次函数调用，写完要能在任意帧独立成立。

## 字体必须显式等待

逐帧截图不会等字体。不加载完就拍，会拍到 fallback 字形（中文最常见：宋体变黑体）。

```tsx
const [handle] = useState(() => delayRender("Loading fonts"));

useEffect(() => {
  const link = document.createElement("link");
  link.rel = "stylesheet";
  link.href = "https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;600&display=swap";
  link.onload = async () => {
    await document.fonts.load('600 16px "Noto Serif SC"', "实际会出现的文字");
    continueRender(handle);
  };
  document.head.appendChild(link);
}, [handle]);
```

要点：`document.fonts.load()` 要带上**真实会渲染的文字**，CJK 才会按子集下载；加载失败也要 `continueRender`，宁可字形降级不要卡死。完整实现见 `assets/remotion-starter/src/fonts.tsx`。

## CLI

```bash
npx remotion studio src/index.ts                      # 浏览器里实时预览，改代码即刷新
npx remotion render src/index.ts Main out/main.mp4    # 出片
npx remotion render src/index.ts Main out/d.mp4 --crf=28 --scale=0.5   # 半分辨率草稿
npx remotion still  src/index.ts Main out/f.png --frame=45             # 单帧截图
```

| 参数 | 说明 |
|---|---|
| `--crf` | 18 左右接近视觉无损，28 是草稿，12 是归档 |
| `--scale` | 0.5 = 半分辨率，样片阶段最省时间 |
| `--frames` | 帧区间，如 `--frames=0-59`（脚本里的 `--start/--end` 会自动换算） |
| `--concurrency` | 并行标签页数，默认按 CPU 核数 |
| `--codec` | `h264` 默认；需要透明通道用 `vp9` + `--pixel-format=yuva420p` |

Remotion 自带合成器，**不需要系统装 ffmpeg**；HyperFrames 需要。

## 坑

1. **首次渲染会下载 Chrome headless**（约 100MB+），离线环境先跑一次 `npx remotion browser ensure`。
2. **`src/index.ts` 是入口**，`registerRoot` 只能调一次；`Composition` 的 `id` 与 CLI 第二个参数必须一致。
3. **`Sequence` 内的时间是相对的**：`SceneCover` 里 `useCurrentFrame()` 从 0 开始，不是从 `from` 开始。想做全片统一的进度条，把它放在 `Sequence` 外面。
4. **SVG 的 `transform-origin` 容易跑偏**：SVG 元素上做 scale 需配 `transform-box: fill-box`，否则用位移 + 透明度更稳。
5. **不要在组件里读文件系统**：素材走 `staticFile()` 放 `public/`。
6. **异步数据**用 `delayRender` / `continueRender` 包裹，别让首帧拍到空状态。

## 已验证的骨架

`assets/remotion-starter/` 与 HyperFrames 模板是**同一支片子**（12 秒、1920×1080、30fps、深色知识风），跑通并抽帧比对过，两套栈出片视觉一致。可以把它当作「同一分镜、两种实现」的对照样本。
