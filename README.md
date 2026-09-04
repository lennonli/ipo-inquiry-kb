# IPO与挂牌审核问询法律问题案例库（2023–2026 四年度合集）

一司一文，按年度分目录存放，共 **1,628 份**：

| 目录 | 年度 | 案例数 |
| --- | --- | --- |
| `2026/` | 2026 年度 | 242 |
| `2025/` | 2025 年度 | 430 |
| `2024/` | 2024 年度 | 386 |
| `2023/` | 2023 年度 | 570 |

每个年度目录保持统一的仓库结构：`cases/代码-简称.md` 案例正文 + `scripts/index.json` 索引 + `templates/` 模板（2026）+ `reports/` 年度总结（如有）。

案例文件结构：YAML frontmatter（company/short/code/board/layer/listing_date/inquiry_rounds/cutoff_date/lawyer/tags）→ 一、概况 → 二、法律问题总览表 → 三、重点法律问题详述（每问含**问询要点**/**回复与核查要点**/**执业提示**）。

## 接入端

- **MCP**：`legal-knowledge`（`https://mcp.licheng.uk/mcp`），kb 取值 `ipo`（2026）/`ipo2025`/`ipo2024`/`ipo2023`/`rules`，服务端源码 `lennonli/legal-knowledge-mcp`
- **网站**：`https://ai.licheng.uk/kb/`（2026）、`/kb2025/`、`/kb2024/`、`/kb2023/`
- **本地检索**：`ipo-kb` skill 的 `kb_search.py`（`search`/`meta`/`full`/`read`/`list`/`update`）

> 本仓为唯一数据源。原年度独立仓（ipo-inquiry-kb-2023/-2024/-2025）已并入本仓并归档，勿再向其提交。

## rules/ 投行法规知识库

顶层 `rules/` 目录收录投资银行/证券业务常用法律、行政法规、部门规章、规范性文件及交易所业务规则的 Markdown 汇编文本，共 **1,055 部**，按 15 个分类子目录存放（基本法规、股票发行审核、债券发行审核上市、其他证券发行、证券发行信息披露、证券发行保荐、审核与注册、询价与承销、证券上市与交易、并购重组、持续督导、新三板相关法规、常用法律法规规章及规则、证券服务机构、财务会计等相关规定）。

- 来源：第三方汇编网站「投资银行家」（`http://www.tzyhj.cn/rule.html`）。每篇 md 的 frontmatter 注明 `title` / `authority`（发布机关）/ `publish_date` / `category` / `subcategory` / `source_url`（原网页链接），全文检索与元数据索引为 `rules/scripts/index.json`（1,055 条，与 md 文件一一对应）。
- 免责声明：本目录为第三方汇编文本，仅供内部检索参考，**正式引用以官方发布为准**（国家法律法规数据库 flk.npc.gov.cn 及证监会、交易所、全国股转系统官网）；法规可能已修订或废止，引用前应核对时效性。
- 命名说明：个别法规名超长（超 macOS 255 字节文件名限制），文件名为截断名+8位哈希，法规全称以 frontmatter `title` 为准。
- 每周五 17:00 由定时任务对来源站点做增量同步（新增/更新/删除）。
