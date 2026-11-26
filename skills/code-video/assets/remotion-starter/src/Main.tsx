import { AbsoluteFill, Sequence, interpolate, spring, useCurrentFrame, useVideoConfig } from "remotion";
import { theme } from "./theme";
import { FontLoader } from "./fonts";

/** 把帧区间映射成 0-1 进度，再交给 interpolate 做缓动。 */
const span = (frame: number, start: number, end: number) =>
  interpolate(frame, [start, end], [0, 1], {
    extrapolateLeft: "clamp",
    extrapolateRight: "clamp",
  });

const easeOut = (t: number) => 1 - Math.pow(1 - t, 3);
const easeIn = (t: number) => t * t * t;

// ============ 常驻背景层：不参与任何场景切换 ============
const Backdrop: React.FC = () => (
  <>
    <AbsoluteFill
      style={{
        background: `
          radial-gradient(900px 620px at 68% 34%, rgba(222,183,141,0.13), transparent 62%),
          radial-gradient(760px 520px at 22% 76%, rgba(145,174,187,0.10), transparent 64%),
          ${theme.ground}`,
      }}
    />
    <AbsoluteFill
      style={{
        backgroundImage: `
          linear-gradient(${theme.line}55 1px, transparent 1px),
          linear-gradient(90deg, ${theme.line}55 1px, transparent 1px)`,
        backgroundSize: "120px 120px",
        maskImage: "radial-gradient(circle at 50% 45%, #000 32%, transparent 78%)",
        WebkitMaskImage: "radial-gradient(circle at 50% 45%, #000 32%, transparent 78%)",
      }}
    />
    <AbsoluteFill
      style={{
        background: "radial-gradient(ellipse at center, transparent 46%, rgba(0,0,0,0.74) 100%)",
      }}
    />
  </>
);

// ============ 场景 1：封面 ============
const SceneCover: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const kicker = easeOut(span(frame, 0, 15));
  const title = spring({ frame: frame - 6, fps, config: { damping: 18, mass: 0.8 } });
  const sub = easeOut(span(frame, 28, 49));
  const line = easeOut(span(frame, 33, 75));
  const out = easeIn(span(frame, 105, 120));

  const titleBlur = interpolate(frame, [6, 33], [10, 0], { extrapolateRight: "clamp" });
  const titleY = interpolate(title, [0, 1], [46, 0]);

  return (
    <AbsoluteFill
      style={{
        opacity: 1 - out,
        transform: `translateY(${-30 * out}px)`,
        filter: `blur(${8 * out}px)`,
      }}
    >
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 300,
          fontFamily: theme.mono,
          fontSize: 22,
          letterSpacing: "0.34em",
          color: theme.gold,
          opacity: kicker,
          transform: `translateX(${-24 * (1 - kicker)}px)`,
        }}
      >
        CODE · RENDER · VIDEO
      </div>
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 352,
          fontFamily: theme.serif,
          fontSize: 112,
          fontWeight: 600,
          lineHeight: 1.18,
          letterSpacing: "0.02em",
          color: theme.ink,
          whiteSpace: "nowrap",
          opacity: title,
          transform: `translateY(${titleY}px)`,
          filter: `blur(${titleBlur}px)`,
        }}
      >
        一句话，变成一条片子
      </div>
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 690,
          fontFamily: theme.sans,
          fontSize: 34,
          lineHeight: 1.74,
          color: theme.inkDim,
          opacity: sub,
          transform: `translateY(${24 * (1 - sub)}px)`,
        }}
      >
        画面由代码算出来，文字、图表、数字全是矢量
        <br />
        改一个词，重渲染一遍，不用重拍
      </div>
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 806,
          width: 1728,
          height: 1,
          transformOrigin: "left center",
          transform: `scaleX(${line})`,
          background: `linear-gradient(90deg, ${theme.gold}, rgba(222,183,141,0))`,
        }}
      />
    </AbsoluteFill>
  );
};

// ============ 场景 2：关系图 ============
const SceneDiagram: React.FC = () => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const head = easeOut(span(frame, 0, 12));
  const title = easeOut(span(frame, 3, 21));
  const nodes = [0, 6, 12].map(
    (offset, i) =>
      spring({
        frame: frame - 9 - offset,
        fps,
        config: { damping: 20, mass: 0.7 },
      }) || 0,
  );
  const linkA = easeOut(span(frame, 30, 46));
  const linkB = easeOut(span(frame, 40, 56));
  const foot = easeOut(span(frame, 45, 60));
  const out = easeIn(span(frame, 100, 120));

  // SVG 里缩放的原点很容易跑偏，用位移+透明度更稳
  const nodeIn = (p: number) => ({
    opacity: p,
    transform: `translateY(${(1 - p) * 18}px)`,
  });

  return (
    <AbsoluteFill
      style={{ opacity: 1 - out, transform: `translateY(${-20 * out}px)` }}
    >
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 132,
          fontFamily: theme.mono,
          fontSize: 24,
          letterSpacing: "0.22em",
          color: theme.steel,
          opacity: head,
        }}
      >
        STAGE 02 — STRUCTURE
      </div>
      <div
        style={{
          position: "absolute",
          left: 96,
          top: 178,
          fontFamily: theme.serif,
          fontSize: 60,
          fontWeight: 500,
          color: theme.ink,
          opacity: title,
          transform: `translateY(${26 * (1 - title)}px)`,
        }}
      >
        把论点拆成看得见的结构
      </div>

      <svg
        style={{ position: "absolute", left: 240, top: 320, width: 1440, height: 560 }}
        viewBox="0 0 1440 560"
      >
        <line
          x1={250}
          y1={280}
          x2={250 + 390 * linkA}
          y2={280}
          stroke={`${theme.steel}80`}
          strokeWidth={1.5}
        />
        <line
          x1={800}
          y1={280}
          x2={800 + 390 * linkB}
          y2={280}
          stroke={`${theme.steel}80`}
          strokeWidth={1.5}
        />

        <g style={nodeIn(nodes[0])} transformOrigin="250 280">
          <circle cx={250} cy={280} r={112} fill="rgba(222,183,141,0.08)" />
          <circle cx={250} cy={280} r={112} fill="none" stroke="rgba(235,229,216,0.45)" strokeWidth={1.5} />
          <text x={250} y={296} textAnchor="middle" fontFamily={theme.serif} fontSize={52} fontWeight={500} fill={theme.ink}>
            人
          </text>
          <text x={250} y={446} textAnchor="middle" fontFamily={theme.sans} fontSize={22} fill={theme.inkDim}>
            提问者
          </text>
        </g>

        <g style={nodeIn(nodes[1])} transformOrigin="720 280">
          <rect x={640} y={196} width={160} height={168} fill="rgba(222,183,141,0.08)" />
          <rect x={640} y={196} width={160} height={168} fill="none" stroke="rgba(235,229,216,0.45)" strokeWidth={1.5} />
          <text x={720} y={298} textAnchor="middle" fontFamily={theme.serif} fontSize={38} fontWeight={500} fill={theme.ink}>
            对话
          </text>
          <text x={720} y={446} textAnchor="middle" fontFamily={theme.sans} fontSize={22} fill={theme.inkDim}>
            只有文字
          </text>
        </g>

        <g style={nodeIn(nodes[2])} transformOrigin="1190 280">
          <circle cx={1190} cy={280} r={112} fill="rgba(222,183,141,0.08)" />
          <circle cx={1190} cy={280} r={112} fill="none" stroke="rgba(235,229,216,0.45)" strokeWidth={1.5} />
          <text x={1190} y={296} textAnchor="middle" fontFamily={theme.serif} fontSize={52} fontWeight={500} fill={theme.ink}>
            机器
          </text>
          <text x={1190} y={446} textAnchor="middle" fontFamily={theme.sans} fontSize={22} fill={theme.inkDim}>
            回答者
          </text>
        </g>
      </svg>

      <div
        style={{
          position: "absolute",
          left: 96,
          bottom: 148,
          fontFamily: theme.sans,
          fontSize: 30,
          color: theme.inkDim,
          letterSpacing: "0.04em",
          opacity: foot,
          transform: `translateY(${18 * (1 - foot)}px)`,
        }}
      >
        三方结构一旦成立，后面每句话都有了落点
      </div>
    </AbsoluteFill>
  );
};

// ============ 场景 3：结论 ============
const SceneQuote: React.FC = () => {
  const frame = useCurrentFrame();
  const quote = easeOut(span(frame, 0, 30));
  const sub = easeOut(span(frame, 20, 41));
  const blur = interpolate(quote, [0, 1], [12, 0]);

  return (
    <AbsoluteFill>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 400,
          textAlign: "center",
          fontFamily: theme.serif,
          fontSize: 78,
          fontWeight: 500,
          lineHeight: 1.38,
          letterSpacing: "0.04em",
          color: theme.ink,
          opacity: quote,
          filter: `blur(${blur}px)`,
          transform: `scale(${0.97 + 0.03 * quote})`,
        }}
      >
        “能讲清楚，
        <br />
        是因为结构先立住了。”
      </div>
      <div
        style={{
          position: "absolute",
          left: 0,
          right: 0,
          top: 706,
          textAlign: "center",
          fontFamily: theme.sans,
          fontSize: 28,
          color: theme.inkDim,
          letterSpacing: "0.1em",
          opacity: sub,
          transform: `translateY(${20 * (1 - sub)}px)`,
        }}
      >
        风格是外壳，结构才是骨架
      </div>
    </AbsoluteFill>
  );
};

// ============ 主时间轴 ============
export const Main: React.FC = () => {
  const frame = useCurrentFrame();
  const { durationInFrames } = useVideoConfig();

  return (
    <AbsoluteFill style={{ backgroundColor: theme.ground }}>
      <FontLoader />
      <Backdrop />

      <Sequence from={0} durationInFrames={120} name="01 封面">
        <SceneCover />
      </Sequence>
      <Sequence from={120} durationInFrames={120} name="02 结构">
        <SceneDiagram />
      </Sequence>
      <Sequence from={240} durationInFrames={120} name="03 结论">
        <SceneQuote />
      </Sequence>

      {/* 常驻：进度条 + 时间码 */}
      <div
        style={{
          position: "absolute",
          left: 96,
          bottom: 63,
          width: 1728,
          height: 2,
          transformOrigin: "left center",
          transform: `scaleX(${frame / durationInFrames})`,
          background: `linear-gradient(90deg, ${theme.gold}, ${theme.steel})`,
          opacity: 0.7,
        }}
      />
      <div
        style={{
          position: "absolute",
          right: 96,
          bottom: 96,
          fontFamily: theme.mono,
          fontSize: 20,
          letterSpacing: "0.12em",
          color: "rgba(235,229,216,0.38)",
        }}
      >
        REMOTION / 30FPS / 00:12
      </div>
    </AbsoluteFill>
  );
};
