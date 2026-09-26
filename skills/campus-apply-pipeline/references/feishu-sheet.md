# 飞书主表操作规律（表名见 config/personal.md）

> 目录：1) 定位与列结构 · 2) 枚举与下拉 · 3) 读写纪律 · 4) 回填口径 · 5) P 键排序置顶法 · 6) 大输出落盘 · 7) 交付

## 1) 定位与列结构

- URL / token / sheet_id / 表名：统一见 `config/personal.md`，本文件不硬编码。
- 列：

| A | B | C | D | E | F | G | H | I | J | K | L | M | N | O | P |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 日期 | 星期 | 时段 | 序号 | 公司名称 | 具体岗位 | 类型 | 优先级方向 | 公司梯队 | 工作地点 | 匹配经历要点 | 投递链接 | 投递状态 | 备注 | 结果阶段 | 排序辅助(临时) |

- P 列只用于排序，**用完必须清空**，不留任何值。
- 日期格式「M月D日」无前导零；时段一天 6 档（见 `config/personal.md`），双选会用「全天」。

## 2) 枚举与下拉

- G 类型：校招 / 实习 / 线下双选会 / 复盘。
- M 投递状态（**必须是下拉选项**，不能手敲自由文本）：待投递、已投递、笔试中、面试中、已offer、已挂、已截止、待进行、已沟通。
- O 结果阶段仅三值：简历挂 / 笔试挂 / 面试挂。
- M 列数据验证范围默认 M1:M500；数据行将超过 500 时，先用 `+dropdown-update` 扩大验证范围再写。
- 历史「已拒」已全局改为「已挂」；状态词以枚举为准。

## 3) 读写纪律

- 主表实时协同：**每次写入前重新 `+csv-get` 取最新数据与行号**，排序会改变物理行号，禁用旧行号，按公司名/岗位重新定位。
- 定位 sheet 用 `--sheet-id <sheet_id，见 config>`（避免猜名）；`--range` 用 A1 矩形。
- 写后必须回读核对（`+csv-get`），返回 `ok` 只表示请求成功。
- 最小改动：未点名的行/列/结构不动；不擅自新增「进度详情」等列。

## 4) 回填口径

- **优先复用已有线索行**（同公司同岗的待投递行）覆盖更新，不轻易新增；确无对应行才新增。
- 新增行序号 D = 当前 max(D)+1；复用线索行时保留原 D。
- 一次回填字段：A/B/C 日期星期时段、E 公司、F 岗位、G 类型、H 方向、I 梯队、J 地点、K 匹配要点、L 投递链接、M 状态、N 备注（=该公司投递进度/记录页链接）；有结果再填 O。
- N 备注与看板 notes **只放投递进度/记录查询链接，不放岗位投递(job)链接**。

## 5) P 键排序置顶法（已投递行沉到活跃块、整体置顶）

分组键（升序）：活跃 1,000,000 → 待投递 3,000,000 → 复盘 5,000,000 → 线下双选会 7,000,000 → 空行 9,000,000；同组用「键 + 物理行号」保证稳定，新投递行落到活跃块底部。

判定（按行，键 = 组常量 + 物理行号 n）：A–O 全空=空行(9M+n)；G=复盘=(5M+n)；G=线下双选会=(7M+n)；M∈{已投递,笔试中,面试中,已offer,已挂,已截止,已沟通}=(1M+n)；其余（待投递）=(3M+n)。组内按 n 升序，新投递行（n 最大）落到活跃块底部。

标准步骤（`<last>`=最新末行，写入前先 csv-get 确认）：

```bash
URL="<主表 URL，见 config/personal.md>"; SID="<sheet_id，见 config>"

# 1) 拉快照（含 P 列、带行号），落盘
lark-cli sheets +csv-get --url "$URL" --sheet-id "$SID" --range "A1:P<last>" --output-path ./snapshot.json

# 2) 生成 P 键单列文件（可选 --applied <物理行> 强制把某行算已投递）
python3 scripts/gen_pkeys.py ./snapshot.json -o ./pkeys.csv

# 3) 写入 P 列（数据从第 2 行开始）
lark-cli sheets +csv-put --url "$URL" --sheet-id "$SID" --start-cell "P2" --csv @pkeys.csv

# 4) 全宽按 P 升序排序（不含表头，range 覆盖完整记录宽度）
lark-cli sheets +range-sort --url "$URL" --sheet-id "$SID" --range "A2:P<last>" \
  --sort-keys '[{"column":"P","ascending":true}]'

# 5) 清空 P 列（high-risk，需 --yes；先 --dry-run 核对范围）
lark-cli sheets +cells-clear --url "$URL" --sheet-id "$SID" --range "P2:P<last>" --yes

# 6) 回读核对
lark-cli sheets +csv-get --url "$URL" --sheet-id "$SID" --range "A1:P<last>"
```

- 排序 range 必须覆盖完整记录宽度（A 到 P），排序列只在 `--sort-keys` 指定 P；`--has-header` 默认 false（数据从第 2 行起、表头第 1 行不在 range 内）。
- 排序后行号变化，后续定位重新 csv-get。

## 6) 大输出落盘

- `+csv-get` 结果核心字段：`annotated_csv`（每行带 `[row=N] ` 前缀，N=真实行号）、`col_indices`（表头第 j 列对应的列字母）、`row_indices`、`current_region`。
- 行号从 `[row=N]` 读，列字母从 `col_indices` 读，**不要手数逗号/心算行号**。
- 大表用 `--output-path` 落盘（stdout 回执看 `complete` / `truncated` / `unread_sheets`）；`complete:false` 表示只有半截，需续读。
- 也可按行窗口分批（`A1:P300`、`A301:P600`…）；`has_more` 表示未完。
- 15 位以上长数字 csv-get 会显示成科学计数，需精确值改用 `+cells-get`。

## 7) 交付

- 本轮对主表有写入/排序，回填并回读核对后，通过 `present_files` 重新交付最新主表（不沿用上一轮卡片）。
- 交付说明简述：本次回填/置顶了哪家、状态、验证方式与覆盖范围。
