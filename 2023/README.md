# IPO与挂牌审核问询法律问题案例库 · 2023年度

2023年1月1日—12月31日完成 **A股上市 313 家**（科创板67/北交所77/深市创业板110/沪市主板36/深市主板23）与 **新三板挂牌 257 家**，共 **570 份案例**，详述法律问题 **3,915 个**。其中约545家为主要可读案例（A股313家 + 新三板有 TXT 的232家），另有约25家新三板绿色通道等简版/待核验记录，一司一文，沉淀“问询要点—回复与核查要点—执业提示”。

> 内容均来自公开披露文件及项目底稿提炼；`执业提示` 为个人业务心得。同步展示于 `https://ai.licheng.uk/kb2023/`。2024、2025及当前年度库分别见 `https://ai.licheng.uk/kb2024/`、`https://ai.licheng.uk/kb2025/`、`https://ai.licheng.uk/kb/`。

## 快速使用

```bash
# 本地检索（任何 AI / 终端均可）
grep -l "股权代持" cases/*.md          # 按标签/关键词找案例
python3 scripts/build-index.py          # 重建索引 scripts/index.json
python3 -c "import json;[print(x['file'],x['tags'])for x in json.load(open('scripts/index.json'))if'股权代持'in x['tags']]"
```

- **年度总结**：`reports/2023年度总结.md`（共性统计 TOP、监管趋势、分公司索引）
- **AI 智能体**：本仓库为纯 Markdown，ZCode / Claude Code / Codex 本地 clone 后直接检索；配套 skill `ipo-kb`

## 目录结构

```
cases/           案例正文，一司一文，文件名“代码-简称.md”；无代码时使用“简称.md”
reports/         2023年度总结报告（与网站 /kb2023/2023年度总结 页面同步）
templates/       case-template.md 新案例模板
scripts/
  index.json          全库索引（build-index.py 生成，勿手改）
  build-index.py      从 frontmatter 重建索引
  migrate_2023.py     首次存量迁移脚本（570份，源自 listing-inquiry-digest/companies_2023）
```

## frontmatter 字段规范

- `company` 公司全称 / `short` 简称（=文件名简称部分）/ `code` 六位代码（双引号包裹）
- `board` 六值：科创板｜沪市主板｜深市主板｜深市创业板｜北交所｜新三板（本年度新三板 `layer` 未区分，留空）
- `listing_date` 上市/挂牌日 / `inquiry_rounds` 问询轮次（含落实函机制的在概况段描述）/ `cutoff_date` 提炼截止日
- `lawyer` 发行人/申请人律师（原文未载明留空，**不得推测填充**）
- `tags` 归一化法律问题标签，与既有年度库采用同一 NORM 体系（见 `scripts/migrate_2023.py`）

## 数据质量基线（严禁“修复”成编造）

- 约25家新三板绿色通道、简易程序或两大通道均未检索到可提取问询文件的公司，保留为“概况+待核验”简版；不把无文件推定为无风险。
- 核准制沪深主板约52家等无文件/简版公司已在库内标注待核验；其余扫描版、文本缺失或页码无法确认的内容亦按原文标注【待核验】，不得补写律师、轮次或法律类别。
- 当前迁移统计：律师名称提取 422/570，未提取 148 份；法律类别标签 476/570，未提取 94 份；未提取项均保留为空。
- 正式援引问询回复、法律意见书或监管口径前，应回交易所、全国股转系统或原始披露文件核对原文。

## 数据来源

上海证券交易所、深圳证券交易所、北京证券交易所及全国股转系统公开披露文件；年度元数据来自 `listing-inquiry-digest/state/companies_2023.json` 与 `state/neeq_listed_2023.json`，抓取与提炼管线见内部项目 `listing-inquiry-digest`。
