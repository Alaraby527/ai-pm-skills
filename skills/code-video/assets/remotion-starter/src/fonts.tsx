import { useEffect, useState } from "react";
import { continueRender, delayRender, staticFile } from "remotion";

const FAMILIES = [
  "family=Noto+Serif+SC:wght@400;500;600",
  "family=Noto+Sans+SC:wght@300;400;500",
  "family=JetBrains+Mono:wght@400;500",
].join("&");

// 这些字必须真的被请求过，CJK 的 unicode-range 子集才会下载下来。
const SAMPLE =
  "一句话变成一条片子画面由代码算出来文字图表数字全是矢量改个词重渲染遍不用拍把论点拆看得见的结构三方旦成立后面每都有了落点能讲清楚是因为先住风格外壳才骨人机器对话提问者回答只";

/**
 * 字体加载闸门。Remotion 的渲染是逐帧截图，字体没就绪就会拍到 fallback 字形。
 * delayRender / continueRender 强制渲染器等字体真正可用。
 */
export const FontLoader: React.FC = () => {
  const [handle] = useState(() => delayRender("Loading CJK fonts"));

  useEffect(() => {
    const link = document.createElement("link");
    link.rel = "stylesheet";
    link.href = `https://fonts.googleapis.com/css2?${FAMILIES}&display=swap`;

    const release = async () => {
      try {
        await Promise.all([
          document.fonts.load(`400 16px "Noto Serif SC"`, SAMPLE),
          document.fonts.load(`600 16px "Noto Serif SC"`, SAMPLE),
          document.fonts.load(`400 16px "Noto Sans SC"`, SAMPLE),
          document.fonts.load(`400 16px "JetBrains Mono"`, "0123456789/:：HYPER"),
          document.fonts.ready,
        ]);
      } catch {
        // 字体拉不到就让渲染继续，宁可字形降级也不要整片卡死
      } finally {
        continueRender(handle);
      }
    };

    link.onload = release;
    link.onerror = () => continueRender(handle);
    document.head.appendChild(link);
  }, [handle]);

  return null;
};

// 不走网络的自托管字体放 public/ 下，用 staticFile 取本地路径，离线也能出片。
export const localFont = (path: string) => staticFile(path);
