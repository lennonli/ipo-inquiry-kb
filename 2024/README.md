# IPO与挂牌审核问询法律问题案例库 · 2024年度

2024年1月1日—12月31日完成 **A股上市 100 家**（科创板15/沪主板17/深主板7/创业板38/北交所23）与 **新三板挂牌 286 家**的审核问询法律问题回溯库，共 **386 份案例**、详述法律问题 1,747 个。一司一文，基于审核期间公开披露的问询回复、法律意见书提炼，沉淀"问询要点—回复与核查要点—执业提示"。

> 内容均来自公开披露文件；`执业提示` 为个人业务心得。同步展示于 `https://ai.licheng.uk/kb2024/`。2025 年度库见 [ipo-inquiry-kb-2025](https://github.com/lennonli/ipo-inquiry-kb-2025)（`https://ai.licheng.uk/kb2025/`），2026 年度库见 [ipo-inquiry-kb](https://github.com/lennonli/ipo-inquiry-kb)（`https://ai.licheng.uk/kb/`）。

## 快速使用

```bash
# 本地检索（任何 AI / 终端均可）
grep -l "股权代持" cases/*.md          # 按标签/关键词找案例
python3 scripts/build-index.py          # 重建索引 scripts/index.json
python3 -c "import json;[print(x['file'],x['tags'])for x in json.load(open('scripts/index.json'))if'股权代持'in x['tags']]"
```

- **年度总结**：`reports/2024年度总结.md`（共性统计 TOP、监管趋势、分公司索引）
- **AI 智能体**：本仓库为纯 Markdown，ZCode / Claude Code / Codex 本地 clone 后直接检索；配套 skill `ipo-kb`

## 目录结构

```
cases/           案例正文，一司一文，文件名"代码-简称.md"
reports/         2024年度总结报告（与网站 /kb2024/2024年度总结 页面同步）
templates/       case-template.md 新案例模板
scripts/
  index.json          全库索引（build-index.py 生成，勿手改）
  build-index.py      从 frontmatter 重建索引
  migrate_2024.py     首次存量迁移脚本（386份，源自 listing-inquiry-digest/companies_2024，已归档）
```

## frontmatter 字段规范

- `company` 公司全称 / `short` 简称（=文件名简称部分）/ `code` 六位代码（双引号包裹）
- `board` 六值：科创板｜沪市主板｜深市主板｜深市创业板｜北交所｜新三板（本年度新三板 layer 未区分，留空）
- `listing_date` 上市/挂牌日 / `inquiry_rounds` 问询轮次（含落实函机制的在概况段描述）/ `cutoff_date` 提炼截止日
- `lawyer` 发行人/申请人律师（原文未载明留空，**不得推测填充**；本年度空 17 份）
- `tags` 归一化标签，与 2026/2025 库同一 NORM 体系（见 `scripts/migrate_2024.py`）

## 数据质量基线（严禁"修复"成编造）

- 约 13 家低于 6KB 的无文件/扫描版简版待核验；相关内容已在案例中保留"待核验"标注，未作推测填充（当前迁移文件大小复核为 15 家）。
- 律所提取率 344/386；轮次解析 334/386（其余为无问询文本或表述特殊，原文未载明处留空）。

## 数据来源

上海/深圳/北京证券交易所官网及全国股转系统官网公开披露文件（抓取与提炼管线见 `listing-inquiry-digest`，数据目录为 `companies_2024/`，元数据为 `state/distill2024_*.json`）。
