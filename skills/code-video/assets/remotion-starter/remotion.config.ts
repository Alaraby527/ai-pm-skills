import { Config } from "@remotion/cli/config";

// JPEG 比 PNG 快很多；需要透明通道或细线条文字锐利时改回 png。
Config.setVideoImageFormat("jpeg");
Config.setJpegQuality(92);
Config.setOverwriteOutput(true);
