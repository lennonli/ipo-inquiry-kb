#!/usr/bin/env python3
"""把 listing-inquiry-digest/companies_2025/*.md 转换为知识库 cases/（带 frontmatter）+ 报告。
元数据（code/board/listing_date）以 state/distill2025_*.json 为准；lawyer/inquiry_rounds/cutoff/tags 从正文提取。
标签归一化与 2026 版 migrate_20260825.py 同一 NORM 体系。
用法: python3 scripts/migrate_2025.py <digest_dir>
"""
import json, os, re, sys
from pathlib import Path

KB = Path(__file__).resolve().parent.parent
SRC = Path(sys.argv[1]) if len(sys.argv) > 1 else Path("/Users/licheng/Documents/zhipu/.zcode/workspace/default/listing-inquiry-digest/companies_2025")
STATE = SRC.parent / "state"
OUT = KB / "cases"
CUTOFF_DEFAULT = "2026-08-25"

H1 = re.compile(r"^# (.+?)（(.+?)）")

BOARD_MAP = [
    (r"新三板", "新三板"),
    (r"北交所", "北交所"),
    (r"创业板", "深市创业板"),
    (r"科创板", "科创板"),
    (r"沪市主板|上交所", "沪市主板"),
    (r"深市主板|深主板", "深市主板"),
]

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
    (r"红筹|境外|外汇|返程|ODI|37号文", "境外架构与外汇"),
    (r"数据|个人信息|网络安全", "数据合规"),
    (r"业务合规|经营合规", "业务合规"),
    (r"刑事|犯罪", "刑事风险"),
    (r"国有|国资", "国资监管"),
    (r"分红|股利", "分红与股利分配"),
    (r"突击入股|新增股东", "申报前新增股东"),
    (r"离职|董监高|任职", "董监高与任职"),
]
SKIP_CAT = re.compile(r"^(纯?(业务|财务|经营|研发)|—|-+|其他(财务|业务)?)|财务测算|法律类别|^其他需律师发表意见事项$")
TAG_SANITIZE = re.compile(r"[\"'\[\]\{\}（）()：:，,。；;]")


def load_meta():
    """ticker -> {code, market, listing_date}，来自 distill 批次 JSON"""
    meta = {}
    for p in sorted(STATE.glob("distill2025_*.json")):
        for c in json.load(open(p)):
            meta[c["ticker"]] = {"code": c.get("code", ""),
                                 "board_raw": c.get("market", ""),
                                 "listing_date": c.get("listing_date", "") or c.get("listed_date", "")}
    return meta


def norm_board(raw, code=""):
    for pat, board in BOARD_MAP:
        if re.search(pat, raw or ""):
            return board
    # 代码前缀兜底（distill2025_n_* 批次无 market 字段）
    if code.startswith("920"):
        return "北交所"
    if code.startswith(("873", "874", "875")):
        return "新三板"
    if code.startswith("688"):
        return "科创板"
    if code.startswith("30"):
        return "深市创业板"
    if code.startswith("60"):
        return "沪市主板"
    if code.startswith("00"):
        return "深市主板"
    return raw or ""


def parse_tags(text):
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


LAWYER_PAT = re.compile(
    r"[\u4e00-\u9fa5]{2,12}(?:（[^）]{2,8}）)?律师(?:（[^）]{2,8}）)?事务所"
    r"(?:[\u4e00-\u9fa5]{2,6}分所)?")


def fmt_yaml_list(items):
    return "[" + ", ".join(f'"{t}"' for t in items) + "]"


def main():
    OUT.mkdir(exist_ok=True)
    meta = load_meta()
    index, problems = [], []
    files = sorted(f for f in os.listdir(SRC) if f.endswith(".md"))
    for fn in files:
        stem = fn[:-3]
        text = (SRC / fn).read_text(encoding="utf-8")
        m = meta.get(stem, {})
        code = m.get("code", "")
        board = norm_board(m.get("board_raw", ""), code)
        listing_date = m.get("listing_date", "")
        h1 = next((l for l in text.splitlines() if l.startswith("# ")), "")
        hm = H1.match(h1)
        company = hm.group(1).strip() if hm else stem
        mr = re.search(r"问询共\s*(\d+)\s*轮", text[:4000])
        rounds = int(mr.group(1)) if mr else 0
        if not rounds:
            # 兜底句式："问询轮次：首轮审核问询、第二轮审核问询、审核中心意见落实函…"
            rset = set(re.findall(r"(?:首轮|第[一二三四五六1-9]轮)[^，。；]{0,6}问询", text[:4000]))
            rounds = len(rset)
        mc = re.search(r"截至\s*(\d{4}-\d{2}-\d{2})", text[:4000])
        lm = LAWYER_PAT.search(text[:4000])
        lawyer = re.sub(r"^(发行人律师|申请人律师|经办律师)", "", lm.group(0)) if lm else ""
        tags = parse_tags(text)

        miss = [k for k, v in dict(code=code, board=board, date=listing_date).items() if not v]
        if miss:
            problems.append((fn, "缺:" + "/".join(miss)))
        if not tags:
            problems.append((fn, "无法律类别标签"))
        if not lawyer:
            problems.append((fn, "缺律师"))

        out_name = f"{code}-{stem}.md" if code else f"{stem}.md"
        fm = [
            "---",
            f"company: {company}",
            f"short: {stem}",
            f'code: "{code}"',
            f"board: {board}",
            'layer: ""',
            f"listing_date: {listing_date}",
            f"inquiry_rounds: {rounds if rounds else ''}",
            f"cutoff_date: {mc.group(1) if mc else CUTOFF_DEFAULT}",
            f"lawyer: {lawyer}",
            f"tags: {fmt_yaml_list(tags)}",
            "---",
            "",
        ]
        (OUT / out_name).write_text("\n".join(fm) + text, encoding="utf-8")
        index.append({"file": out_name, "company": company, "short": stem, "code": code,
                      "board": board, "layer": "", "listing_date": listing_date,
                      "inquiry_rounds": rounds,
                      "cutoff_date": mc.group(1) if mc else CUTOFF_DEFAULT,
                      "lawyer": lawyer, "tags": tags})
    (KB / "scripts" / "index.json").write_text(
        json.dumps(sorted(index, key=lambda r: r["file"]), ensure_ascii=False, indent=1),
        encoding="utf-8")
    print(f"转换 {len(index)} 份案例 → {OUT}")
    print(f"问题 {len(problems)} 项：")
    for fn, msg in problems:
        print(f"  {fn}: {msg}")


if __name__ == "__main__":
    main()
