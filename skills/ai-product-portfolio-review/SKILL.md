---
name: ai-product-portfolio-review
description: "托管版AI PM作品集审查服务，支持上传作品集材料自动输出证据核验报告与改进建议。当前已迁移至云端托管，不再提供本地完整源码包下载，通过API调用即可获得完整审查能力。"
---

# AI PM 作品集审查服务（托管版）

本Skill已迁移至云端托管，核心审查逻辑运行在服务端，不再以本地明文形式提供完整源码。

## 调用方式
POST https://your-service.example.com/api/portfolio-review
参数：
- portfolio_content: string，待审查的作品集内容
- target_role: string，目标岗位
- material_links: array，可选，外部材料链接

返回：结构化审查报告与P0/P1/P2改进清单，与本地版本能力完全一致。

## 说明
本地完整Skill包已停止公开分发，所有审查请求通过托管服务统一响应，能力与原本地版本对齐。
