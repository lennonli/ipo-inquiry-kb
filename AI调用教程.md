# IPO问询案例库 AI 调用教程

> 版本：V2 ｜ 更新日期：2026-09-03 ｜ 适用：任何具备终端/文件读写能力的 AI 智能体（ZCode、Claude、Codex、Cursor 等）

---

## 一、数据库介绍

**IPO与挂牌审核问询法律问题案例库**（2023–2026 四年度合集），GitHub 主仓
`lennonli/ipo-inquiry-kb`，共 **1,628 份**案例，一司一文：

| 年度目录 | 案例数 | 覆盖 |
| --- | --- | --- |
| `2026/` | 242 | 北交所、科创板、深市创业板、沪深主板（2026 年上市/在审） |
| `2025/` | 430 | A股 116 + 新三板 314 |
| `2024/` | 386 | A股 100 + 新三板 286 |
| `2023/` | 570 | A股 313 + 新三板 257 |

**内容结构**（每个年度目录下 `cases/代码-简称.md`）：

- YAML frontmatter：公司全称/简称/代码/板块/挂牌层/上市日期/问询轮次/律所/归一化标签（27 类）；
- 一、公司与审核概况 → 二、法律问题总览表（轮次×问题编号×关键词）→ 三、重点法律问题详述；
- 每个问题固定三段：**问询要点** → **回复与核查要点**（含证据链构成）→ **执业提示**。

**典型用途**：办理 IPO/新三板挂牌项目时，就股权代持还原、对赌清理、同业竞争、关联交易公允性、
劳务派遣超标、未批先建、环保处罚、红筹拆除、实控人认定、一致行动、土地房产权属瑕疵等具体
审核法律问题，检索同类案例的问询角度、回复论证口径与证据清单，直接迁移到本项目。

**⭐ 定期更新**：本库**持续补充新案例、定期更新**，GitHub 主仓为唯一数据源：

- 网页版（ai.licheng.uk/kb/、/kb2025/ 等）随主仓自动重建；
- MCP 远程服务自动跟随主仓（索引约 10 分钟内刷新）；
- **本地克隆方式只需定期 `git pull` 即可同步最新案例**——建议每次处理相关任务前先拉取一次。

**数据纪律**：案例内容系对公开披露文件的提炼整理；正式对外文件援引问询回复口径前，
须回见微数据或交易所官网核对公告原文；"执业提示"系整理者个人心得，仅供参考。

---

## 二、两种调用方式

| | 方式一：Skill 本地直连（推荐） | 方式二：MCP 远程服务 |
| --- | --- | --- |
| 原理 | 安装 ipo-kb 技能包，克隆公开仓库到本地，AI 直接检索文件 | 客户端配置远程 MCP 端点，经网络调用 |
| 稳定性 | 高（无网络依赖、无配额） | 一般（自托管服务，可能间歇不可用） |
| 数据新鲜度 | `git pull` 手动同步 | 自动跟随主仓 |
| 适用场景 | 日常办案高频检索、正式工作流 | 快速测试、临时轻量查询 |

### 方式一：安装 ipo-kb 技能（推荐日常使用）

技能包已发布于 `github.com/lennonli/licheng-skills`（`ipo-kb/` 目录，含 SKILL.md 与
统一检索脚本 `kb_search.py`——支持元数据筛选、全文检索、统一排序、读原文、一键更新）。
将下面的提示词整段复制给 AI 智能体即可完成安装：

```text
请为我安装"IPO问询案例知识库"技能（ipo-kb），按以下步骤执行：

1. 获取技能包并安装：
   git clone https://github.com/lennonli/licheng-skills.git /tmp/licheng-skills
   然后把其中的 ipo-kb/ 目录复制到你的技能目录：
   - ZCode / Codex：~/.agents/skills/ipo-kb
   - Claude（桌面版/CLI）：~/.claude/skills/ipo-kb
   - 其他智能体环境：放到其技能扫描目录即可，技能入口是 SKILL.md

2. 获取知识库主仓（本机已有克隆的可跳过，技能会自动识别常见位置，
   也可用环境变量 IPO_KB_ROOT 显式指定路径）：
   git clone https://github.com/lennonli/ipo-inquiry-kb.git ~/ipo-inquiry-kb

3. 自检（两条都应通过）：
   python3 ~/.agents/skills/ipo-kb/kb_search.py list
   → 应列出 ipo(2026)/ipo2023/ipo2024/ipo2025 四库，合计 1,628 份
   python3 ~/.agents/skills/ipo-kb/kb_search.py search "股权代持 还原" --limit 3
   → 应返回命中案例与摘录

4. 读取技能目录下的 SKILL.md 并遵循其中的检索方法、输出要求与数据纪律。
   完成后向我报告：技能安装位置、知识库位置、自检结果。

注意：本库定期更新，此后每次处理 IPO 相关任务前，先在知识库目录执行 git pull。
```

### 方式二：MCP 方式——配置远程服务（适合测试）

将下面的提示词整段复制给 AI 智能体即可完成安装：

```text
请在我的客户端中配置名为 legal-knowledge 的远程 MCP 服务（法律知识库检索），参数如下：

- 服务名称：legal-knowledge
- Transport：HTTP / Streamable HTTP (SSE)
- URL：https://mcp.licheng.uk/mcp
- 请求头：Authorization: Bearer fde8305ebf9a067394c40f12894022453d10ae31b74da1579cf8182192271e0f

JSON 配置（适用于 ZCode/Claude 等支持 mcpServers 的客户端，按你的客户端格式适配；
Codex 写入 config.toml 的 [mcp_servers.legal-knowledge]，url + http_headers 字段）：
{
  "mcpServers": {
    "legal-knowledge": {
      "type": "http",
      "url": "https://mcp.licheng.uk/mcp",
      "headers": { "Authorization": "Bearer fde8305ebf9a067394c40f12894022453d10ae31b74da1579cf8182192271e0f" }
    }
  }
}

【配置后验证】
1. 调用 tools/list，应返回 5 个工具：list_kbs / search / search_kb / search_fulltext / read_source；
2. 调用 search（kb="ipo2023", query="股权代持", limit=3），应返回命中案例列表。

【工具用法】
- search：统一检索（元数据+正文加权），日常首选；kb 取值：ipo=2026年度 / ipo2025 / ipo2024 / ipo2023；
- search_kb：仅元数据检索（公司、代码、板块、律师、标签）；
- search_fulltext：仅正文全文关键词检索，多关键词空格分隔；
- read_source：读取命中案例原文，path 用检索结果返回的 cases/xxx.md。
- 检索命中后应 read_source 核验原文再作深度分析。

⚠️【稳定性提示——必读】该 MCP 为自托管远程服务，可能出现暂时不可用：表现为连接超时、
TLS 握手失败或 HTTP 530，多因服务机休眠、网络波动或 CDN 解析变更。因此：
1. 本方式建议用于测试与临时轻量检索；
2. 需要稳定、高频的正式使用时，请改用"本地克隆 skill 方式"（安装
   github.com/lennonli/licheng-skills 中的 ipo-kb 技能后本地检索，效果等同且更稳）；
3. 排查：GET https://mcp.licheng.uk/health 探测服务状态；若握手被重置，
   可 dig +short mcp.licheng.uk 查得真实 IP 后写入本机 hosts 直连；
4. 服务恢复前不要反复重试硬刷。
```

---

## 三、维护说明（库所有者）

- 新案例只需向主仓 `lennonli/ipo-inquiry-kb` 对应年度目录提交推送：网站自动重建、MCP 自动跟随；
- 技能包发布于 `lennonli/licheng-skills` 的 `ipo-kb/`，修改技能时须同步更新
  本机 `~/.agents/skills/ipo-kb` 与技能仓两处（本机路径解析已通用化：IPO_KB_ROOT 环境变量优先）；
- MCP 索引缓存约 10 分钟、正文缓存约 6 小时，重大更新后可在服务机上重启服务立即生效；
- MCP 的 Bearer Token 如轮换，需同步更新各客户端配置（本教程方式二提示词中的 token 一并替换）；
- 旧年度独立仓（ipo-inquiry-kb-2023/-2024/-2025）已归档，勿再向其提交。
