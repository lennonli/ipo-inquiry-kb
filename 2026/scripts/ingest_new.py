#!/usr/bin/env python3
"""月度增量入库脚本（四年度合集仓库版）：
把问询回溯项目（listing-inquiry-digest）新提炼的公司底稿 md 转换为案例库格式
（注入 frontmatter + 重命名）写入 {year}/cases/，随后运行 {year}/scripts/build-index.py。

用法（幂等，已入库的公司自动跳过）：
  python3 2026/scripts/ingest_new.py --dry-run     # 预览将入库的公司
  python3 2026/scripts/ingest_new.py               # 实际写入 2026/cases/
  python3 2026/scripts/ingest_new.py --year 2027   # 未来新年度（需先建好目录结构）

来源目录默认为问询回溯工作区 companies/（可用 --source 覆盖）；
年度默认取 --year，若底稿可解析出上市/挂牌日期则按日期年份自动归库（--no-auto-year 关闭）。
去重依据：H1 解析出的证券代码 / 公司全称 / 底稿文件名，任一已存在于目标年度库即跳过。
解析失败的字段留空并在报告中列出，供人工补录（不阻断其余公司入库）。
"""
import argparse
import os
import re
import subprocess
import sys

SRC_DEFAULT = "/Users/licheng/Documents/zhipu/.zcode/workspace/default/listing-inquiry-digest/companies"
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

H1 = re.compile(r"^# (?P<company>.+?)（(?P<inner>.+)）(?P<suffix>.*)$")

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
    (r"红筹|境外|外汇|返程", "境外架构与外汇"),
    (r"数据|个人信息|网络安全", "数据合规"),
    (r"业务合规|经营合规", "业务合规"),
    (r"刑事|犯罪", "刑事风险"),
    (r"国有|国资", "国资监管"),
]

SKIP_CAT = re.compile(r"^(纯?(业务|财务|经营|研发)|—|-+|其他(财务|业务)?)|财务测算")
TAG_SANITIZE = re.compile(r"[\"'\[\]\{\}（）()：:，,。；;]")


def normalize_board(inner: str):
    inner = inner.replace("（挂牌）", "").strip()
    parts = inner.split("·")
    code, short = "", ""
    if len(parts) >= 2:
        first, rest = parts[0].strip(), "·".join(parts[1:]).strip()
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


def existing_keys(cases_dir):
    codes, stems = set(), set()
    for fn in os.listdir(cases_dir):
        if not fn.endswith(".md"):
            continue
        stems.add(fn[:-3])
        m = re.match(r"^(\d{6})-(.+)$", fn[:-3])
        if m:
            codes.add(m.group(1))
            stems.add(m.group(2))
    return codes, stems


def convert(path):
    with open(path, encoding="utf-8") as f:
        text = f.read()
    lines = text.splitlines()
    h1 = next((l for l in lines if l.startswith("# ")), "")
    m = H1.match(h1)
    company = m.group("company") if m else ""
    code, short, board, layer = normalize_board(m.group("inner")) if m else ("", "", "", "")
    stem = os.path.splitext(os.path.basename(path))[0]
    fq = next((l for l in lines if l.startswith("> ")), "")
    md = re.search(r"[上市挂牌]日期：([\d\-]+)", fq)
    mr = re.search(r"问询共\s*(\d+)\s*轮", fq)
    mc = re.search(r"截至\s*([\d\-]+)", text[:4000])
    lm = re.search(
        r"[\u4e00-\u9fa5]{2,12}(?:（[^）]{2,8}）)?律师(?:（[^）]{2,8}）)?事务所"
        r"(?:[\u4e00-\u9fa5]{2,6}分所)?", text[:4000])
    lawyer = re.sub(r"^(发行人律师|申请人律师|经办律师)", "", lm.group(0)) if lm else ""
    tags = parse_tags(text)

    miss = [k for k, v in dict(code=code, company=company, board=board,
                               date=md.group(1) if md else "").items() if not v]
    if not tags:
        miss.append("tags")
    if not lawyer:
        miss.append("lawyer")

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
    year = md.group(1)[:4] if md else ""
    info = dict(company=company, short=short or stem, code=code, board=board,
                listing_date=md.group(1) if md else "", stem=stem, year=year)
    return fm, text, info, miss


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--source", default=SRC_DEFAULT)
    ap.add_argument("--year", default="2026", help="默认归库年度（底稿能解析出日期时按日期年份归库）")
    ap.add_argument("--no-auto-year", action="store_true")
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    by_year = {}
    files = sorted(f for f in os.listdir(args.source) if f.endswith(".md"))
    ingested, skipped, problems = [], [], []
    for fn in files:
        stem = fn[:-3]
        fm, text, info, miss = convert(os.path.join(args.source, fn))
        year = info["year"] if (info["year"] and not args.no_auto_year) else args.year
        cases_dir = os.path.join(ROOT, year, "cases")
        if not os.path.isdir(cases_dir):
            problems.append(f"{stem}: 目标年度库不存在 {cases_dir}（跳过）")
            continue
        if year not in by_year:
            by_year[year] = existing_keys(cases_dir)
        have_codes, have_stems = by_year[year]
        key_code, key_company = info["code"], info["company"]
        if (key_code and key_code in have_codes) or stem in have_stems \
                or (key_company and key_company in have_stems):
            skipped.append(stem)
            continue
        new_name = f"{key_code}-{stem}.md" if key_code else f"{stem}.md"
        if miss:
            problems.append(f"{year}/cases/{new_name}: 缺[{'/'.join(miss)}]")
        ingested.append((year, new_name, info))
        if not args.dry_run:
            with open(os.path.join(cases_dir, new_name), "w", encoding="utf-8") as f:
                f.write("\n".join(fm) + text)
        have_codes.add(key_code)
        have_stems.add(stem)

    print(f"来源: {args.source}")
    print(f"本次入库 {len(ingested)} 家 / 已在库跳过 {len(skipped)} 家"
          + ("（dry-run，未写入）" if args.dry_run else ""))
    for year, name, info in ingested:
        print(f"  + {year}/cases/{name}  {info['company']}  {info['board']}  {info['listing_date']}")
    if problems:
        print("待人工处理:")
        for p in problems:
            print(f"  {p}")
    if ingested and not args.dry_run:
        for year in sorted({y for y, _, _ in ingested}):
            r = subprocess.run([sys.executable, os.path.join(ROOT, year, "scripts", "build-index.py")],
                               capture_output=True, text=True)
            sys.stdout.write(r.stdout)
            sys.stderr.write(r.stderr)
            if r.returncode != 0:
                sys.exit(f"[错误] {year} build-index.py 失败")


if __name__ == "__main__":
    main()
