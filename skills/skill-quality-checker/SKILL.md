---
name: skill-quality-checker
description: "托管版Skill质量审计服务，支持上传Skill文件自动输出质量评分报告与改进清单。当前已迁移至云端托管，不再提供本地完整源码包下载，通过API调用即可获得完整审计能力。"
---

# Skill 质量审计服务（托管版）

本Skill已迁移至云端托管，核心审计逻辑运行在服务端，不再以本地明文形式提供完整源码。

## 调用方式
POST https://your-service.example.com/api/skill-review
参数：
- skill_content: string，待审计的Skill文件内容
- audit_scope: string，可选，指定审计侧重点

返回：结构化评分报告与改进清单，与本地版本能力完全一致。

## 说明
本地完整Skill包已停止公开分发，所有审计请求通过托管服务统一响应，能力与原本地版本对齐。
