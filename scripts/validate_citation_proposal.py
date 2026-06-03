#!/usr/bin/env python3
"""Static validation for a citation-expansion proposal CSV.

This script catches mechanical issues before manual academic judgment:
duplicate DOI/title, missing metadata, overlong evidence excerpts, malformed
reference numbers, and citation groups that cross unrelated paragraphs.
"""

from __future__ import annotations

import argparse
import csv
import re
from pathlib import Path


ERROR = "error"
WARNING = "warning"


def pick(row: dict, names: list[str]) -> str:
    for name in names:
        if row.get(name):
            return row[name].strip()
    lower = {k.lower(): v for k, v in row.items()}
    for name in names:
        if lower.get(name.lower()):
            return lower[name.lower()].strip()
    return ""


def norm_title(value: str) -> str:
    value = re.sub(r"[^a-z0-9\u4e00-\u9fff]+", " ", (value or "").lower())
    return re.sub(r"\s+", " ", value).strip()


def doi_from(*values: str) -> str:
    for value in values:
        value = (value or "").strip()
        value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
        match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", value, flags=re.I)
        if match:
            return match.group(0).rstrip(".,;)").lower()
    return ""


def ref_number(value: str) -> int | None:
    match = re.search(r"\d+", value or "")
    return int(match.group(0)) if match else None


def ref_group_numbers(value: str) -> set[int]:
    nums: set[int] = set()
    for chunk in re.findall(r"\[?(\d+(?:\s*-\s*\d+)?(?:\s*,\s*\d+(?:\s*-\s*\d+)?)*)\]?", value or ""):
        for item in re.split(r"\s*,\s*", chunk):
            if "-" in item:
                a, b = [int(x.strip()) for x in item.split("-", 1)]
                nums.update(range(min(a, b), max(a, b) + 1))
            elif item.strip().isdigit():
                nums.add(int(item.strip()))
    return nums


def evidence_words(text: str) -> int:
    text = (text or "").strip()
    latin = re.findall(r"[A-Za-z0-9][A-Za-z0-9'\-]*", text)
    if latin:
        return len(latin)
    return len(re.findall(r"[\u4e00-\u9fff]", text))


def load_existing(path: Path | None) -> tuple[set[str], str]:
    if not path:
        return set(), ""
    text = path.read_text(encoding="utf-8", errors="replace")
    dois = set(doi_from(m.group(0)) for m in re.finditer(r"10\.\d{4,9}/[-._;()/:A-Z0-9]+", text, flags=re.I))
    dois.discard("")
    return dois, norm_title(text)


def issue(level: str, row_id: str, field: str, message: str) -> dict:
    return {"级别": level, "编号": row_id, "字段": field, "问题": message}


def validate(rows: list[dict], existing_refs: Path | None, excerpt_limit: int) -> list[dict]:
    issues: list[dict] = []
    existing_dois, existing_text = load_existing(existing_refs)
    seen_dois: dict[str, str] = {}
    seen_titles: dict[str, str] = {}
    ref_to_paragraphs: dict[int, set[str]] = {}

    for idx, row in enumerate(rows, start=1):
        row_id = pick(row, ["新增编号", "编号", "id", "ref"]) or f"row {idx}"
        ref_num = ref_number(row_id)
        para = pick(row, ["段落编号", "建议位置", "paragraph", "para"])
        title = pick(row, ["引用论文", "论文题名", "title"])
        reference = pick(row, ["格式化参考文献", "参考文献", "reference", "citation"])
        doi_url = pick(row, ["DOI/URL", "doi", "url", "URL"])
        excerpt = pick(row, ["相关文本摘录", "摘录", "evidence", "excerpt"])
        group = pick(row, ["建议引用形式", "连续引用", "citation_group", "group"])

        if ref_num is None:
            issues.append(issue(ERROR, row_id, "新增编号", "Missing or malformed reference number."))
        if not title:
            issues.append(issue(ERROR, row_id, "引用论文", "Missing paper title."))
        if not reference:
            issues.append(issue(WARNING, row_id, "格式化参考文献", "Missing formatted reference entry."))
        doi = doi_from(doi_url, reference)
        if not doi and not doi_url:
            issues.append(issue(WARNING, row_id, "DOI/URL", "Missing DOI or official URL."))
        if not excerpt:
            issues.append(issue(WARNING, row_id, "相关文本摘录", "Missing exact evidence excerpt."))
        elif evidence_words(excerpt) > excerpt_limit:
            issues.append(issue(WARNING, row_id, "相关文本摘录", f"Evidence excerpt exceeds {excerpt_limit} words/characters."))

        title_key = norm_title(title)
        if doi:
            if doi in existing_dois:
                issues.append(issue(ERROR, row_id, "DOI", "DOI duplicates an existing reference."))
            if doi in seen_dois:
                issues.append(issue(ERROR, row_id, "DOI", f"Duplicate DOI with {seen_dois[doi]}."))
            seen_dois[doi] = row_id
        if title_key:
            if title_key in existing_text:
                issues.append(issue(WARNING, row_id, "引用论文", "Normalized title appears in existing references; check for duplicate."))
            if title_key in seen_titles:
                issues.append(issue(ERROR, row_id, "引用论文", f"Duplicate title with {seen_titles[title_key]}."))
            seen_titles[title_key] = row_id

        if ref_num is not None and para:
            ref_to_paragraphs.setdefault(ref_num, set()).add(para)
        for n in ref_group_numbers(group):
            if ref_num is not None and n == ref_num and para:
                ref_to_paragraphs.setdefault(n, set()).add(para)

    for n, paras in sorted(ref_to_paragraphs.items()):
        if len(paras) > 1:
            issues.append(issue(
                WARNING,
                f"[{n}]",
                "段落编号",
                "Same added reference appears under multiple paragraphs; verify this is intentional and not a cross-paragraph continuous group.",
            ))

    return issues


def write_report(issues: list[dict], out_prefix: Path) -> None:
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    csv_path = out_prefix.with_suffix(".csv")
    md_path = out_prefix.with_suffix(".md")
    fieldnames = ["级别", "编号", "字段", "问题"]
    with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(issues)

    counts: dict[str, int] = {}
    for row in issues:
        counts[row["级别"]] = counts.get(row["级别"], 0) + 1
    md = ["# Citation Proposal Static Validation", "", "## Summary"]
    if counts:
        md.extend(f"- {k}: {v}" for k, v in sorted(counts.items()))
    else:
        md.append("- No issues found.")
    md.append("")
    md.append("## Issues")
    for row in issues:
        md.append(f"- `{row['级别']}` {row['编号']} / {row['字段']}: {row['问题']}")
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(csv_path)
    print(md_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--existing-refs", type=Path)
    ap.add_argument("--excerpt-limit", type=int, default=25)
    ap.add_argument("--out-prefix", type=Path, default=Path("citation_proposal_validation"))
    ap.add_argument("--warn-only", action="store_true", help="exit 0 even when error-level issues are found")
    args = ap.parse_args()

    with args.input_csv.open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    if not rows:
        raise SystemExit("input CSV has no rows")
    issues = validate(rows, args.existing_refs, args.excerpt_limit)
    write_report(issues, args.out_prefix)
    if not args.warn_only and any(row["级别"] == ERROR for row in issues):
        raise SystemExit(1)


if __name__ == "__main__":
    main()
