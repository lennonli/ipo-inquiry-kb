#!/usr/bin/env python3
"""从 cases/*.md 的 frontmatter 重建 scripts/index.json。
新增/修订案例后运行：python3 scripts/build-index.py
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CASES = os.path.join(ROOT, "cases")

FM_FIELDS = ["company", "short", "code", "board", "layer", "listing_date",
             "inquiry_rounds", "cutoff_date", "lawyer", "tags",
             "deal_type", "pay_method", "deal_amount", "status",
             "registered_date", "fin_adv"]

# 各批次入库的 frontmatter 字段名不统一，做同义归一
FM_ALIASES = {"stock_code": "code", "full_name": "company"}


def parse_frontmatter(text):
    if not text.startswith("---"):
        return None
    end = text.find("\n---", 3)
    if end < 0:
        return None
    fm = {}
    for line in text[4:end].splitlines():
        m = re.match(r"(\w+):\s*(.*)", line)
        if not m:
            continue
        k, v = m.groups()
        v = v.strip().strip('"')
        if k == "tags":
            fm[k] = [t.strip().strip('"').strip() for t in v.strip("[]").split(",") if t.strip()]
        elif k == "inquiry_rounds":
            fm[k] = int(v) if v.isdigit() else 0
        elif k == "deal_amount":
            normalized = v.replace(",", "")
            try:
                number = float(normalized)
                fm[k] = int(number) if number.is_integer() else number
            except ValueError:
                fm[k] = v
        else:
            fm[k] = v
    return fm


def h1_info(text):
    """从正文 H1『# 公司全称（代码·板块）…』兜底提取 company/code/board（frontmatter 缺字段时用）。"""
    m = re.search(r"^# (.+?)（(\d{6})(?:·([^）]+))?）", text, re.M)
    if not m:
        return {}
    info = {"company": m.group(1).strip(), "code": m.group(2)}
    if m.group(3):
        info["board"] = m.group(3).strip()
    return info


def fill_identity(row, fn, fm, text):
    """仅当字段为空时回填 company/short/code/board，绝不覆盖 frontmatter 已有值。"""
    h1 = h1_info(text)
    m_fn = re.match(r"(\d{6})-(.+)\.md$", fn)
    if not row.get("company"):
        row["company"] = fm.get("company") or fm.get("full_name") or h1.get("company", "")
    if not row.get("short"):
        row["short"] = fm.get("short") or (m_fn.group(2) if m_fn else "")
    if not row.get("code"):
        row["code"] = fm.get("code") or fm.get("stock_code") or (m_fn.group(1) if m_fn else "") or h1.get("code", "")
    if not row.get("board"):
        row["board"] = fm.get("board") or h1.get("board", "")
    return row


def main():
    index = []
    for fn in sorted(os.listdir(CASES)):
        if not fn.endswith(".md"):
            continue
        text = open(os.path.join(CASES, fn), encoding="utf-8").read()
        fm = parse_frontmatter(text)
        if not fm:
            print(f"[警告] {fn} 无 frontmatter，跳过", file=sys.stderr)
            continue
        row = {"file": fn}
        row.update({k: fm.get(k, "" if k != "tags" else []) for k in FM_FIELDS})
        row = fill_identity(row, fn, fm, text)
        index.append(row)
    out = os.path.join(ROOT, "scripts", "index.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"索引重建完成: {len(index)} 条 → {out}")


if __name__ == "__main__":
    sys.exit(main())
