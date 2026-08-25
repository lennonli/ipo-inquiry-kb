#!/usr/bin/env python3
"""存量案例迁移脚本（2026-08-25）：
从 /Users/licheng/Downloads/companies 读取 242 份 md（只读），
注入 YAML frontmatter、重命名为"代码-简称.md"、写入 cases/。
解析失败的字段留空并在报告中列出，供人工补录。
"""
import json
import os
import re
import shutil
import sys

SRC = "/Users/licheng/Downloads/companies"
DST = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "cases")

# H1 变体：
#   # 公司（920079·北交所）审核问询法律问题回溯      —— 标准：代码·板块
#   # 公司（乔路铭·北交所）…                        —— 简称·板块（无代码）
#   # 公司（北交所·审核问询）…                      —— 板块·审核问询（在审）
#   # 公司（875086·新三板基础层（挂牌））…           —— 嵌套括号
H1 = re.compile(r"^# (?P<company>.+?)（(?P<inner>.+)）(?P<suffix>.*)$")

BOARD_MAP = [
    (r"新三板", "新三板"),
    (r"北交所", "北交所"),
    (r"创业板", "深市创业板"),
    (r"科创板", "科创板"),
    (r"沪市主板|上交所", "沪市主板"),
    (r"深市主板|深主板", "深市主板"),
]

# 法律类别归一化（保守映射：首个命中生效；未命中原样保留）
NORM = [
    (r"代持", "股权代持"),
    (r"对赌|特殊权利|特殊投资条款|一票否决|领售|反稀释|优先清算|^B\+?轮?$|^B$", "对赌与特殊权利条款"),
    (r"一致行动|控制权稳定", "控制权稳定性"),
    (r"实控人|实际控制人|控股股东", "实控人认定"),
    (r"同业竞争", "同业竞争"),
    (r"独立性|五独立", "独立性"),
    (r"关联", "关联交易与关联方"),
    (r"劳动|社保|公积金|劳务", "劳动与社会保障"),
    (r"环保|环境", "环保合规"),
    (r"诉讼|仲裁", "诉讼仲裁"),
    (r"土地|房产|不动产|租赁", "土地房产与租赁"),
    (r"资质|许可|牌照|认证", "资质许可"),
    (r"历史沿革|股权变动|增资|股改|出资", "历史沿革与股权变动"),
    (r"股权激励|员工持股", "股权激励"),
    (r"信息披露", "信息披露"),
    (r"公司治理|治理|内控", "公司治理与内控"),
    (r"募投|募集资金", "募集资金运用"),
    (r"税收|税务", "税务合规"),
    (r"行政处罚|处罚|违法", "行政处罚"),
    (r"知识产权|专利|商标|著作", "知识产权"),
    (r"承诺", "承诺事项"),
    (r"重大合同", "重大合同"),
    (r"红筹|境外|外汇|返程", "境外架构与外汇"),
    (r"数据|个人信息|网络安全", "数据合规"),
    (r"业务合规|经营合规", "业务合规"),
    (r"刑事|犯罪", "刑事风险"),
    (r"国有|国资", "国资监管"),
]

SKIP_CAT = re.compile(r"^(纯?(业务|财务|经营|研发)|—|-+|其他(财务|业务)?)|财务测算")

# YAML 行内数组安全字符清洗（引号/括号/逗号等会破坏解析）
TAG_SANITIZE = re.compile(r"[\"'\[\]\{\}（）()：:，,。；;]")


# 原文未载明但已人工核验补录的律师（仅此一例，其余空值保持空）
HARDCODE_LAWYER = {"七一股份.md": "北京中伦文德（杭州）事务所"}


def normalize_board(inner: str):
    """inner = 括号内内容，如 '920079·北交所' / '875086·新三板基础层（挂牌）'"""
    inner = inner.replace("（挂牌）", "").strip()
    parts = inner.split("·")
    code, short = "", ""
    if len(parts) >= 2:
        first, rest = parts[0].strip(), "·".join(parts[1:]).strip()
        # 公司名自带括号（如"伏达半导体（合肥）股份有限公司"）时代码位于 first 段末尾
        cm = re.search(r"([0-9]{6}|[0-9]{4})\s*$", first)
        if re.fullmatch(r"[0-9A-Za-z]{4,8}", first):
            code = first
            board_raw = rest
        elif cm:
            code = cm.group(1)
            board_raw = rest
        else:
            board_raw = rest if any(re.search(p, rest) for p, _ in BOARD_MAP) else first
            if any(re.search(p, board_raw) for p, _ in BOARD_MAP):
                short = first
    else:
        board_raw = parts[0]
    board = next((b for p, b in BOARD_MAP if re.search(p, board_raw)), board_raw)
    layer = ""
    if board == "新三板":
        if "基础层" in board_raw:
            layer = "基础层"
        elif "创新层" in board_raw:
            layer = "创新层"
    return code, short, board, layer


def parse_tags(text: str):
    tags = set()
    in_overview = False
    for line in text.splitlines():
        if line.startswith("## 二、"):
            in_overview = True
            continue
        if in_overview and line.startswith("## "):
            break
        if not (in_overview and line.startswith("|")):
            continue
        if re.match(r"^\|[\s\-|:]+\|$", line):
            continue
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) < 4 or cells[0] == "轮次":
            continue
        for raw in re.split(r"[/、，,；;]", cells[3]):
            raw = TAG_SANITIZE.sub("", raw).strip()
            if not raw or SKIP_CAT.search(raw):
                continue
            tag = next((t for p, t in NORM if re.search(p, raw)), raw)
            tags.add(tag)
    return sorted(tags)


def fmt_yaml_list(items):
    return "[" + ", ".join(f'"{t}"' for t in items) + "]"


def main():
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".md"))
    index, problems = [], []
    for fn in files:
        with open(os.path.join(SRC, fn), encoding="utf-8") as f:
            text = f.read()
        lines = text.splitlines()
        h1 = next((l for l in lines if l.startswith("# ")), "")
        m = H1.match(h1)
        company = m.group("company") if m else ""
        code, short, board, layer = normalize_board(m.group("inner")) if m else ("", "", "", "")
        stem = os.path.splitext(fn)[0]
        fq = next((l for l in lines if l.startswith("> ")), "")
        md = re.search(r"[上市挂牌]日期：([\d\-]+)", fq)
        mr = re.search(r"问询共\s*(\d+)\s*轮", fq)
        mc = re.search(r"截至\s*([\d\-]+)", text[:4000])
        # 兼容"锦天城（深圳）律师事务所""国浩律师（上海）事务所""金杜律师事务所上海分所"等写法
        lm = re.search(
            r"[\u4e00-\u9fa5]{2,12}(?:（[^）]{2,8}）)?律师(?:（[^）]{2,8}）)?事务所"
            r"(?:[\u4e00-\u9fa5]{2,6}分所)?", text[:4000])
        lawyer = re.sub(r"^(发行人律师|申请人律师|经办律师)", "",
                        lm.group(0)) if lm else ""
        lawyer = HARDCODE_LAWYER.get(fn, lawyer)
        tags = parse_tags(text)

        miss = [k for k, v in dict(code=code, company=company, board=board,
                                   date=md.group(1) if md else "").items() if not v]
        if miss:
            problems.append((fn, "缺:" + "/".join(miss)))
        if not tags:
            problems.append((fn, "无法律类别标签"))
        if not lawyer:
            problems.append((fn, "缺律师"))

        fm = [
            "---",
            f"company: {company}",
            f"short: {short or stem}",
            f'code: "{code}"' if code else 'code: ""',
            f"board: {board}",
            f'layer: "{layer}"',
            f"listing_date: {md.group(1) if md else ''}",
            f"inquiry_rounds: {mr.group(1) if mr else ''}",
            f"cutoff_date: {mc.group(1) if mc else ''}",
            f"lawyer: {lawyer}",
            f"tags: {fmt_yaml_list(tags)}",
            "---",
            "",
        ]
        new_name = f"{code}-{stem}.md" if code else f"{stem}.md"
        with open(os.path.join(DST, new_name), "w", encoding="utf-8") as f:
            f.write("\n".join(fm) + text)
        index.append(dict(file=new_name, company=company, short=short or stem, code=code,
                          board=board, layer=layer,
                          listing_date=md.group(1) if md else "",
                          inquiry_rounds=int(mr.group(1)) if mr else 0,
                          cutoff_date=mc.group(1) if mc else "",
                          lawyer=lawyer, tags=tags))
    with open(os.path.join(os.path.dirname(DST), "scripts", "index.json"), "w",
              encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"迁移完成: {len(index)} 份 → {DST}")
    print(f"待人工补录 {len(problems)} 项:")
    for fn, p in problems:
        print(f"  {fn}: {p}")


if __name__ == "__main__":
    sys.exit(main())
