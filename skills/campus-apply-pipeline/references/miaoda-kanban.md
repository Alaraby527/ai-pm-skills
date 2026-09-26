# 妙搭「秋招工作台」看板双写

> 目录：1) 定位与通道 · 2) 数据表与枚举 · 3) 进「已投递」条件 · 4) createdBy 数据隔离（重点）· 5) 备注口径 · 6) 双写流程与提示词

## 1) 定位与通道

- URL / app_id / 看板名称：统一见 `config/personal.md`，本文件不硬编码。
- 所有读写走 `app_builder_agent`：编辑传 app_id + user_prompt，**不传 arch_type**；同一应用必须**串行**编辑（一次只在途一个改动），改完回读再做下一个。

## 2) 数据表与枚举

- 数据表 `application`；看板接口 `GET /api/applications/kanban`，后端按 `createdBy=当前登录用户` 过滤、按 `status` 分列。
- `status`（与主表 M 对应）：

| 看板列 | status |
|---|---|
| 待投递 | `pending` |
| 已投递 | `applied` |
| 笔试/测评 | `written_test` |
| 面试 | `interview` |
| Offer | `offer` |
| 已挂 | `failed` |
| 已结束/截止 | `ended` |

- `jobType`：校招=`campus_recruitment`、实习=`internship`。
- 其它常用字段：`company`、`position`、`location`、`notes`、`createdBy`。

## 3) 进「已投递」条件

必须同时满足：`status="applied"`、`company` 非空、`position` 非空、`createdBy=当前登录用户`。任一缺失卡片不会出现在用户看板的「已投递」列。

- 投递成功后再双写，不要在投递前先建 applied 卡。
- 校招岗 jobType=campus_recruitment；**实习岗同样要同步**（如智谱实习），jobType=internship，不要因为看板叫「秋招工作台」就漏记实习。

## 4) createdBy 数据隔离（重点，最易踩坑）

- 接口写入可能落到内置测试/验收账号（非本人账号）；看板按创建人隔离，**用户在自己账号下看不到测试账号建的卡**。
- 因此在给 app_builder_agent 的指令中必须明确：
  1. **以用户本人登录会话创建**记录（createdBy=当前用户），不要用测试/验收账号；
  2. 创建后**调用看板接口回读核对**，确认该卡出现在当前用户的对应列，并回报该列卡片总数（应较之前 +1）。
- 若发现卡落到测试账号：以用户本人会话重建正确卡，并删除测试账号下的重复卡，再请用户确认「能看到」。
- 最终以**用户本人看板实见**为准，不能只凭写入返回成功就判定完成。

## 5) 备注口径

- `notes` 只放该公司**投递进度/投递记录页**链接（用于查状态），**不放岗位投递(job)链接**。
- 一张卡对应一家公司的一个岗位；同公司多岗分别建卡。

## 6) 双写流程与提示词

1. 官方门户投递成功、主表回填后，再双写看板。
2. 调 app_builder_agent（传 app_id），user_prompt 要点（替换实际值）：

```text
在「秋招工作台」的 application 表新增 1 条投递记录，并以我本人登录会话创建（createdBy=当前用户，勿用测试/验收账号）：
- company：<公司全称>
- position：<岗位名>
- status：applied
- jobType：campus_recruitment（实习则用 internship）
- location：<工作地点，未知可留空>
- notes：<该公司投递进度/记录页链接，仅放进度链接>
创建后调用 GET /api/applications/kanban 回读，确认该卡出现在我本人账号的「已投递」列，并回报该列卡片总数（应比之前多 1）。
```

3. 拿到回读结果后，请用户确认看板可见；可见即双写完成，再进入下一家。
4. 后续状态推进（笔试/面试/offer/已挂）同样串行更新对应卡的 status，并回读核对。
