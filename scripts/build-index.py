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
             "inquiry_rounds", "cutoff_date", "lawyer", "tags"]


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
            fm[k] = [t.strip() for t in v.strip("[]").split(",") if t.strip()]
        elif k == "inquiry_rounds":
            fm[k] = int(v) if v.isdigit() else 0
        else:
            fm[k] = v
    return fm


def main():
    index = []
    for fn in sorted(os.listdir(CASES)):
        if not fn.endswith(".md"):
            continue
        fm = parse_frontmatter(open(os.path.join(CASES, fn), encoding="utf-8").read())
        if not fm:
            print(f"[警告] {fn} 无 frontmatter，跳过", file=sys.stderr)
            continue
        row = {"file": fn}
        row.update({k: fm.get(k, "" if k != "tags" else []) for k in FM_FIELDS})
        index.append(row)
    out = os.path.join(ROOT, "scripts", "index.json")
    with open(out, "w", encoding="utf-8") as f:
        json.dump(index, f, ensure_ascii=False, indent=1)
    print(f"索引重建完成: {len(index)} 条 → {out}")


if __name__ == "__main__":
    sys.exit(main())
