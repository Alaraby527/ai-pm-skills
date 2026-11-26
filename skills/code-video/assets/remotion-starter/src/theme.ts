// 设计令牌：整片风格只在这里改，组件里不要写死色值。
export const theme = {
  ground: "#08090A",
  ink: "#EBE5D8",
  inkDim: "#8C9099",
  gold: "#DEB78D",
  steel: "#91AEBB",
  line: "#243038",
  serif: '"Noto Serif SC", serif',
  sans: '"Noto Sans SC", sans-serif',
  mono: '"JetBrains Mono", monospace',
} as const;

export const film = {
  fps: 30,
  width: 1920,
  height: 1080,
  durationInFrames: 360, // 12s
} as const;
