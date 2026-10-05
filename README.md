# IPO与挂牌审核问询法律问题案例库（2023–2026 四年度合集）

一司一文，按年度分目录存放，共 **1,650 份**：

| 目录 | 年度 | 案例数 |
| --- | --- | --- |
| `2026/` | 2026 年度 | 264 |
| `2025/` | 2025 年度 | 430 |
| `2024/` | 2024 年度 | 386 |
| `2023/` | 2023 年度 | 570 |

每个年度目录保持统一的仓库结构：`cases/代码-简称.md` 案例正文 + `scripts/index.json` 索引 + `templates/` 模板 + `reports/` 年度总结（如有）。

案例文件结构：YAML frontmatter（company/short/code/board/layer/listing_date/inquiry_rounds/cutoff_date/lawyer/tags）→ 一、概况 → 二、法律问题总览表 → 三、重点法律问题详述（每问含**问询要点**/**回复与核查要点**/**执业提示**）。

## refi2023–refi2026/ 再融资审核问询案例库

一司一文，共 **893 份**（refi2023 390 / refi2024 107 / refi2025 186 / refi2026 210），覆盖定增、可转债、配股等。目录结构：`cases/代码-简称.md` + `scripts/index.json`（含 refi_type/pay_method/deal_amount/status/questions 等字段）+ `reports/` 年度总结。

## ma2023–ma2026/ 并购重组审核问询案例库

一司一文，共 **76 份**（ma2023 7 / ma2024 11 / ma2025 39 / ma2026 19）。目录结构：`cases/代码-简称.md` + `scripts/index.json`（含 deal_type/pay_method/deal_amount/status/registered_date 等字段）+ `reports/` 年度总结。frontmatter 字段名在各历史入库批次间存在变体（code/stock_code、company/full_name），`scripts/build-index.py` 已做同义归一，缺字段时从正文 H1「公司全称（代码·板块）」兜底回填索引。

## 接入端

- **MCP**：`legal-knowledge`（`https://mcp.licheng.uk/mcp`），kb 取值共 14 库：`ipo`（2026）/`ipo2025`/`ipo2024`/`ipo2023`、`refi2026`/`refi2025`/`refi2024`/`refi2023`、`ma2026`/`ma2025`/`ma2024`/`ma2023`、`rules`、`supplement`，服务端源码 `lennonli/legal-knowledge-mcp`
- **网站**：`https://ai.licheng.uk/kb/`（2026）、`/kb2025/`、`/kb2024/`、`/kb2023/`、`/refi2023/`–`/refi2026/`、`/ma2023/`–`/ma2026/`
- **本地检索**：`ipo-kb` skill 的 `kb_search.py`（`search`/`meta`/`full`/`read`/`list`/`update`）；根目录 `AI调用教程.md` 为面向任意 AI 智能体的接入教程

> 本仓为唯一数据源。原年度独立仓（ipo-inquiry-kb-2023/-2024/-2025）已并入本仓并归档，勿再向其提交。

## supplement/ 补充法律意见书合集

顶层 `supplement/` 目录收录交易所公开披露的**补充法律意见书 824 份**（2001–2024，按文号年份子目录），与各年度 `cases/` 问询案例库互补（问询→回复→补充法律意见书全链条）。frontmatter 含 company/code/board/round/firm/doc_no/sign_date，索引为 `supplement/scripts/index.json`。检索：`kb_search.py search --kb supplement`。图片型扫描件（实测 28 份，约 3%）正文无文本层，按元数据定位后回交易所官网原文核对（正文引用的 `*_images/` 图片文件未随本库存档）。详见 `supplement/README.md`。

## rules/ 投行法规知识库

顶层 `rules/` 目录收录投资银行/证券业务常用法律、行政法规、部门规章、规范性文件及交易所业务规则的 Markdown 汇编文本，共 **1,286 部**，按 15 个分类子目录存放（基本法规、股票发行审核、债券发行审核上市、其他证券发行、证券发行信息披露、证券发行保荐、审核与注册、询价与承销、证券上市与交易、并购重组、持续督导、新三板相关法规、常用法律法规规章及规则、证券服务机构、财务会计等相关规定）。详见 `rules/README.md`。

- 来源：第三方汇编网站「投资银行家」（`http://www.tzyhj.cn/rule.html`）。每篇 md 的 frontmatter 注明 `title` / `authority`（发布机关）/ `publish_date` / `category` / `subcategory` / `source_url`（原网页链接），全文检索与元数据索引为 `rules/scripts/index.json`（1,286 条，与 md 文件一一对应）。
- 免责声明：本目录为第三方汇编文本，仅供内部检索参考，**正式引用以官方发布为准**（国家法律法规数据库 flk.npc.gov.cn 及证监会、交易所、全国股转系统官网）；法规可能已修订或废止，引用前应核对时效性。
- 命名说明：个别法规名超长（超 macOS 255 字节文件名限制），文件名为截断名+8位哈希，法规全称以 frontmatter `title` 为准。
- 每周五 17:00 由定时任务对来源站点做增量同步（新增/更新/删除）。
