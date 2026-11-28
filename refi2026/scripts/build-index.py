#!/usr/bin/env python3
"""重建 refi2026/scripts/index.json（库内无现成 builder，按既往口径手写）。

口径（以 2026-11-27 批的 3 条新行 + 21 条已维护行核实）：
- 行顺序：既有 250 行原位不动，新行按代码排序追加在末尾（与 11-27 批一致）。
- 字段顺序：dir, code, short, company, board, title, refi_type, refi_type_raw,
  pay_method, deal_amount, status, status_short, registered_date, listing_date,
  lawyer, lawyer_raw, file, tags, size, questions。
- title 取正文 H1（去掉 "# "）；dir 取文件名 stem；short 无 frontmatter 时取文件名简称；
  listing_date 缺省为 ""。
- size = 文件字节数（int），questions = 正文中 "### " 标题数；仅新行计算这两项，
  既有行一律不动（229 条 legacy 行的 size/questions 为 ""，21 条维护行的 questions
  语义未完全坐实，均保持原样）。
- 既有行默认原封不动；只有调用方用环境变量 REFI_UPDATE_FILES 点名的文件，
  才刷新其 status / registered_date / size（status 仅当新值非空、且旧值不是其
  前缀时才替换，以保住索引里的富化长 status）。
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))  # refi2026/
CASES = os.path.join(ROOT, "cases")
INDEX = os.path.join(ROOT, "scripts", "index.json")

KEYS = ["dir", "code", "short", "company", "board", "title", "refi_type",
        "refi_type_raw", "pay_method", "deal_amount", "status", "status_short",
        "registered_date", "listing_date", "lawyer", "lawyer_raw", "file",
        "tags", "size", "questions"]


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
        else:
            fm[k] = v
    return fm


def build_row(fn, text):
    fm = parse_frontmatter(text)
    if fm is None:
        print(f"[警告] {fn} 无 frontmatter，跳过", file=sys.stderr)
        return None
    stem = fn[:-3]
    m = re.match(r"(\d{6})-(.+)$", stem)
    h1 = re.search(r"^# (.+)$", text, re.M)
    row = {
        "dir": stem,
        "code": fm.get("code", "") or (m.group(1) if m else ""),
        "short": fm.get("short", "") or (m.group(2) if m else ""),
        "company": fm.get("company", ""),
        "board": fm.get("board", ""),
        "title": h1.group(1).strip() if h1 else "",
        "refi_type": fm.get("refi_type", ""),
        "refi_type_raw": fm.get("refi_type_raw", ""),
        "pay_method": fm.get("pay_method", ""),
        "deal_amount": fm.get("deal_amount", ""),
        "status": fm.get("status", ""),
        "status_short": fm.get("status_short", ""),
        "registered_date": fm.get("registered_date", ""),
        "listing_date": fm.get("listing_date", ""),
        "lawyer": fm.get("lawyer", ""),
        "lawyer_raw": fm.get("lawyer_raw", ""),
        "file": fn,
        "tags": fm.get("tags", []),
        "size": os.path.getsize(os.path.join(CASES, fn)),
        "questions": len(re.findall(r"^### ", text, re.M)),
    }
    return {k: row[k] for k in KEYS}


def main():
    old = json.load(open(INDEX, encoding="utf-8"))
    files = sorted(f for f in os.listdir(CASES) if f.endswith(".md"))
    # 本周被改动的文件（只刷新这些行的 status / registered_date / size）：
    # 由调用方用环境变量 REFI_UPDATE_FILES 以空格分隔传入，未传入则只追加新行、
    # 不动任何既有行。禁止按 frontmatter 全量刷新——索引里有不少 frontmatter
    # 没有的富化值（如 refi_type_raw、listing_date、长 status），会被洗掉。
    update_files = set(os.environ.get("REFI_UPDATE_FILES", "").split())
    out = []
    # 既有行严格按旧索引顺序输出（11-27 批的 3 行在末尾是既往顺序，不得重排）。
    for old_row in old:
        fn = old_row["file"]
        text = open(os.path.join(CASES, fn), encoding="utf-8").read()
        row = dict(old_row)
        if fn in update_files:
            fresh = build_row(fn, text)
            for k in ("status", "registered_date"):
                nv = fresh[k]
                ov = row.get(k, "")
                if nv and nv != ov and not (isinstance(ov, str) and ov.startswith(nv)):
                    row[k] = nv
            if isinstance(row.get("size"), int) and row["size"] != fresh["size"]:
                row["size"] = fresh["size"]
        out.append({k: row[k] for k in KEYS})
    new_rows = []
    old_files = {r["file"] for r in old}
    for fn in files:
        if fn not in old_files:
            text = open(os.path.join(CASES, fn), encoding="utf-8").read()
            r = build_row(fn, text)
            if r:
                new_rows.append(r)
    new_rows.sort(key=lambda r: r["code"])
    out.extend(new_rows)
    orphans = [r["file"] for r in old if r["file"] not in files]
    if orphans:
        print(f"[警告] 索引中有 {len(orphans)} 条文件已不在盘上：{orphans}", file=sys.stderr)
    with open(INDEX, "w", encoding="utf-8") as f:
        json.dump(out, f, ensure_ascii=False, indent=1)
    print(f"refi 索引重建完成: {len(out)} 条（既有 {len(old)} + 新增 {len(new_rows)}）→ {INDEX}")
    if orphans:
        print(f"注意：{len(orphans)} 条孤儿行已随重建剔除")


if __name__ == "__main__":
    sys.exit(main())
