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

- **MCP**：`legal-knowledge`（`https://mcp.licheng.uk/mcp`），kb 取值 `ipo`（2026）/`ipo2025`/`ipo2024`/`ipo2023`，服务端源码 `lennonli/legal-knowledge-mcp`
- **网站**：`https://ai.licheng.uk/kb/`（2026）、`/kb2025/`、`/kb2024/`、`/kb2023/`
- **本地检索**：`ipo-kb` skill 的 `kb_search.py`（`search`/`meta`/`full`/`read`/`list`/`update`）

> 本仓为唯一数据源。原年度独立仓（ipo-inquiry-kb-2023/-2024/-2025）已并入本仓并归档，勿再向其提交。
