# HyperFrames 模式

HTML 就是视频。一个 `index.html` 就是一条片子，时间不用写代码，用 `data-*` 属性声明；动画交给 GSAP；长相交给 CSS。

## 最小可跑工程

```
project/
├── index.html          # 唯一必需文件，就是一个 composition
├── hyperframes.json    # 可选，登记 blocks/components/assets 路径
└── package.json        # 可选，只是 npm run 的快捷方式
```

已实测：只有 `index.html` 也能渲染。

## 契约（写错就不出画面）

**根元素**必须是 composition：

```html
<div id="root"
     data-composition-id="main"
     data-start="0"
     data-duration="12"      <!-- 总时长（秒），决定总帧数 -->
     data-width="1920"
     data-height="1080"
     data-fps="30">          <!-- 不写默认 30 -->
```

**时间轴元素**（clip）必须带三件套：

```html
<h1 class="clip"
    data-start="0.5"        <!-- 秒，可以写数字，也可以引用另一个 clip 的 id -->
    data-duration="3"
    data-track-index="1">标题</h1>
```

- `data-track-index` 同时决定**层级**（数字大在前面）和**轨道分组**。
- 同一轨道上的 clip **时间不能重叠**。
- 根元素之外的普通元素（没有 `class="clip"`）永远可见，用来做背景、网格、暗角、进度条。
- 每个 clip 必须有 `data-duration`；`<video>` / `<audio>` 可省略，取素材原长。

**相对时间**：`data-start` 可以直接写另一个 clip 的 `id`，表示「在那个 clip 开始后再开始」，比写死秒数更抗改动。

## 动画：GSAP 时间轴

```html
<script src="https://cdn.jsdelivr.net/npm/gsap@3.15.0/dist/gsap.min.js"></script>
<script>
  const tl = gsap.timeline({ paused: true });   // 必须 paused
  tl.fromTo("#title", { opacity: 0, y: 40 }, { opacity: 1, y: 0, duration: 0.8, ease: "power3.out" }, 0);
  window.__timelines["main"] = tl;               // 运行时会预建这个对象
  tl.seek(0);
</script>
```

- 时间轴**必须 paused**，播放权归框架，它按帧 `seek`。
- 只给 `window.__timelines[id]` 赋值，**不要** `window.__timelines = {}`，那会覆盖运行时预建的对象，动画全失效。
- 每个 tween 的绝对时间放在最后一个参数，和 `data-start` 对齐。
- 只动可插值的属性：`opacity`、`x/y/scale/rotation`、`filter`、`attr`（SVG 数值属性）。不要动触发重排的布局属性。

可用动画库：GSAP、CSS、Web Animations、Anime.js、Lottie、Three.js、Canvas 2D。

## 禁止清单

- 不要用脚本 `play()` / `pause()` / 改 `currentTime` 操作音视频——框架管播放和同步。
- 不要用脚本按时间显示/隐藏 clip——框架按 `data-start`/`data-duration` 做挂载卸载，两套逻辑会打架。
- 不用 `setTimeout` / `setInterval` 做动画。
- 转场（淡入、滑入）属于「挂载后的视觉变化」，写在脚本里没问题；显隐本身不要自己管。

## 结构建议

- 一个文件里 clip 超过 ~8 个，就该拆成子场景：`compositions/scene-01.html` 等，父级用 `data-composition-src` 挂载。`lint` 会以 `timeline_track_too_dense` 提醒你。
- 单文件适合 ≤3 个场景的短片；多场景系列片拆文件，改一屏不动其他屏。
- 一个 clip 里不要再嵌时间轴元素（`nested_structure_needs_subcomposition`），否则时间轴只有顶层一行可读。

## CLI（实测可用）

```bash
npx --yes hyperframes init <name> --example blank --non-interactive --skip-skills --resolution landscape
npx --yes hyperframes browser ensure          # 首次渲染前装 Chrome headless
npx --yes hyperframes preview                 # studio 实时预览
npx --yes hyperframes lint .                  # 结构与字体检查（报 error 必须修）
npx --yes hyperframes check                   # lint + 运行时校验 + 布局检查
npx --yes hyperframes snapshot                # 指定时间点出 PNG，用来肉眼验收
npx --yes hyperframes render . -o out.mp4 -q draft --start 0 --end 10 -f 30
```

`render` 常用参数：

| 参数 | 说明 |
|---|---|
| `-q draft\|looks\|delivery` | CRF 28 / 16；草稿用 draft，成片用 delivery |
| `--start` / `--end` | 秒，出样片时只渲染一段（要求整帧率 24/25/30/60） |
| `-f` | 帧率，默认取根元素 `data-fps` |
| `--format` | `mp4` / `webm` / `mov`（带 alpha）/ `gif` / `png-sequence` |
| `-w` | 并行 worker 数，每个 worker 一个 Chrome 进程（约 256MB） |

没有本地 Chrome/ffmpeg 时可用 `hyperframes cloud`（HeyGen 云端渲染，需账号）。

## 坑

1. **字体**。`font-family` 写了系统字体（PingFang SC、Songti SC），`lint` 会报 `font_family_without_font_face`：本机渲染能用，云端渲染没有这个字体就会降级。跨机器稳定的做法是用 Google Fonts 家族并在 `<head>` 里链好：

```html
<link href="https://fonts.googleapis.com/css2?family=Noto+Serif+SC:wght@400;500;600&family=Noto+Sans+SC:wght@300;400;500&family=JetBrains+Mono:wght@400;500&display=swap" rel="stylesheet">
```

2. **CJK 子集**。中文 webfont 是按 unicode-range 分片的，只有真正用到的字才会下载。如果出现个别字字形不对，多半是子集没覆盖到，换字体或自托管完整 woff2。

3. **远程素材**。渲染是逐帧截图，远程图片没加载完就拍，会得到空白框。一律下载到本地。

4. **时长取整**。`data-duration` 用整数秒，总帧数 = 时长 × fps，不然首尾会差一两帧。

5. **绝对路径**。`src` 用相对工程目录的路径，不要写 `file://` 或绝对路径，换机器就废。

## 已验证的骨架

`assets/hyperframes-starter/index.html` 就是跑通过的模板：常驻背景层 + 3 个场景 + GSAP 时间轴 + 中文衬线标题 + SVG 关系图 + 进度条，12 秒 1920×1080 30fps，`lint` 0 error。直接复制改内容。
