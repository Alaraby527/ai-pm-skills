# 官方招聘门户 / ATS 操作规律

> 目录：1) 只走官方门户 · 2) 飞书 ATS · 3) Moka · 4) 北森 zhiye · 5) 表单填写（React 受控，含在线简历微调）· 6) PDF 上传与解析 · 7) 坐标与点击 · 8) 验证/登录交接 · 9) 标签页与异步

## 1) 只走官方门户

- 投递入口仅限公司官方招聘门户/官方 ATS：飞书 ATS、Moka、北森（zhiye）、官网自研系统。
- BOSS、邮箱直投、智联、猎聘、前程、小红书私信、第三方简历聚合站、高校就业平台：**只作线索记录**，不作为投递通道（用户明确同意恢复前不投）。
- 进入门户后**先登录、先查「投递记录/应聘记录」与投递纪律**（如「3 个月内限投 N 个职位」），再找岗。

## 2) 飞书 ATS（域名形如 `<tenant>.jobs.feishu.cn/<t>`）

| 页面 | 路径 |
|---|---|
| 职位列表 | `/<t>/position/list` |
| 登录 | `/<t>/login` |
| 应聘记录/进度（→N 备注、状态） | `/<t>/position/application` |
| 职位详情 | `/<t>/position/<id>/detail` |
| 投递表单 | `/<t>/resume/<id>/apply` |
| 投递成功 | `/<t>/resume/applied` |

- 上传 PDF → 等约 3s → 点「解析并覆盖/自动填充」→ 校验字段 → 补全 → 滚到底点「提交简历」。
- 应聘记录页异步：刷新后等 5–8s 再读；窄宽（如 464）下个别租户记录页不渲染，换宽度或路径。

## 3) Moka（域名 `app.mokahr.com/campus-recruitment/<slug>/<id>` 或 `campus_apply`）

| 页面 | hash |
|---|---|
| 职位列表 | `#/jobs`（可带 `?keyword=`） |
| 投递记录 | `#/candidateHome/applications` |
| 投递表单 | `#/job/<uuid>/apply` |
| 已投后编辑 | `#/apply/edit/<id>` |

- **租户 URL 必须带完整数字 ID**，截断少写几位会 404（数字 ID 以门户实际地址为准）。
- 列表卡片含：岗位名、发布/更新时间、部门、全职/实习、地点、职责摘要；找全非技术岗后再评分。
- 提交可能触发滑块拼图，交接用户完成。

## 4) 北森 zhiye（域名 `<tenant>.zhiye.com`，移动版 `m.zhiye.com`）

| 页面 | 路径 |
|---|---|
| 职位列表 | `/campus/jobs?KeyWords=` |
| 职位详情 | `/campus/detail?jobAdId=<uuid>` |
| 投递表单 | `/form?fromPage=job&jobAdId=<uuid>&userId=<id>` |
| 投递记录 | 个人中心 / 我的投递（如 `/personal/deliveryRecord`） |

- 移动版常用 `adid` 参数与 `#/apply-create/<step>?adid=`；流程同 PC，分步保存。

## 5) 表单填写（React 受控组件）

React 受控 input/textarea 不能只赋值，须用原生 setter 再派发事件：

```js
function setVal(el, val){
  const proto = el.tagName==='TEXTAREA' ? HTMLTextAreaElement.prototype : HTMLInputElement.prototype;
  Object.getOwnPropertyDescriptor(proto,'value').set.call(el, val);
  el.dispatchEvent(new Event('input',{bubbles:true}));
  el.dispatchEvent(new Event('change',{bubbles:true}));
}
```

- 原生 select：设 `value` 后 dispatch change；自定义下拉：点开 → 点选对应 option。
- 日期/单选/多选优先点选真实控件；填完用 snapshot 回读确认是否被框架接受。
- 文本字段统一标点口径（如书名号统一为【】），不改事实、不编数据。

### 在线简历微调（只改在线简历；闭环第 7 步）

- **必须先调用简历 skill `resume-jd-align`**（同仓库 `skills/resume-jd-align`，本地别名 ai-pm-resume-writing），按其 JD 关键词提取与简历对齐方法执行。
- **只改门户「在线简历」的结构化文本**；附件 PDF 统一用通用版、不按公司定制、不改动。
- 先按 ATS 读完整 JD，提取**硬技能 / 业务场景 / 软素质**三类关键词。
- 关键词**自然融入对应经历的「证据 bullet」**（职责 / 方案 / 成果的具体描述行），与事实贴合、不堆砌；事实、数据、成果零改动，经历顺序与独立项目不删减。
- **禁止**把关键词写进「个人评价 / 自我评价」；**禁止**改长或改名【】四字小标题（保持恰好四个汉字）。
- **★点「保 存」前**：把「改了哪几条、各自融入了哪些 JD 关键词」展示给用户，取得**第 2 次确认（保存确认）**后才保存。

## 6) PDF 上传与解析

- 上传前向用户确认文件名/版本（通用版 vs 管培生等变体）。
- 上传 → 等待自动解析（约 3s）→ 选择「解析并覆盖/自动填充」→ 逐字段校验（实习地点、期望城市、项目等常需补）→ 提交。
- 用户明确「只写在线简历、不传附件」时，不传附件，不算漏传。

## 7) 坐标与点击

- `click_xy`/`drag`/`scroll` 坐标按 **DOM 视口 1100×920** 归一化（0–1000）；落盘截图常为 464×685，**不可直接用于换算**。
- 由 `getBoundingClientRect()` 换算：`nx=x/1100*1000`、`ny=y/920*1000`。
- 部分提交按钮 JS `.click()` 无效：改用归一化坐标，或把元素平移进可点区域再点。
- 排查 DOM 用 `snapshot()`/`read_all()`；`bu.js()` 偶尔返回 `{}`，换 snapshot 或结构化读取。

## 8) 验证 / 登录交接

- 登录、扫码、短信/OTP、人机、滑块拼图：调 `interaction.request_action`（browserControl）交接用户，不代填密码/验证码（用户主动给出时可填）。
- 保持停在验证页再交接；用户完成后重新 snapshot，用新 refs 继续，不复用旧 refs。
- 提交属高后果动作：交接用户确认或由用户本人完成。

## 9) 标签页与异步

- 点击新开 Tab：`list_tabs()` 按 URL/标题匹配 → `switch_tab()`（会附着并前置该 Tab）；会话错位用 `resync()`。
- 列表/记录页多为前端渲染与懒加载：滚动加载、`wait_for_load`、必要时等待后再读；停招岗会显示「已停止招聘/不存在」，跳过。
