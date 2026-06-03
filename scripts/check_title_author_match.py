#!/usr/bin/env python3
"""Check proposed citation title and author metadata against DOI sources.

Input: CSV with columns such as:
- 新增编号 / 编号 / id / ref
- 引用论文 / 论文题名 / title
- 格式化参考文献 / reference / citation
- DOI/URL / doi / url

The script uses Crossref first, then DataCite. Rows without DOI metadata are
marked for manual review instead of being treated as failures. It writes a
Markdown report by default; use --write-csv for a machine-readable intermediate
report.
"""

from __future__ import annotations

import argparse
import csv
import difflib
import html
import json
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path


def pick(row: dict, names: list[str]) -> str:
    for name in names:
        if row.get(name):
            return row[name].strip()
    lower = {k.lower(): v for k, v in row.items()}
    for name in names:
        if lower.get(name.lower()):
            return lower[name.lower()].strip()
    return ""


def doi_from(*values: str) -> str:
    for value in values:
        value = (value or "").strip()
        value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
        match = re.search(r"\b10\.\d{4,9}/[-._;()/:A-Z0-9]+\b", value, flags=re.I)
        if match:
            return match.group(0).rstrip(".,;)")
    return ""


def request_json(url: str) -> tuple[int, dict | None]:
    req = urllib.request.Request(url, headers={"User-Agent": "citation-expansion-auditor"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace"))
    except urllib.error.HTTPError as exc:
        return exc.code, None
    except Exception:
        return 0, None


def normalize_title(title: str) -> str:
    title = html.unescape(title or "")
    title = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return re.sub(r"\s+", " ", title).strip()


def title_score(current: str, authority: str) -> float:
    c = normalize_title(current)
    a = normalize_title(authority)
    if not c or not a:
        return 0.0
    if c == a or c in a or a in c:
        return 1.0
    return difflib.SequenceMatcher(None, c, a).ratio()


def surname(value: str) -> str:
    value = re.sub(r"[^A-Za-z\- ]+", " ", value or "").strip()
    if not value:
        return ""
    parts = value.split()
    if len(parts) == 1:
        return parts[0].lower()
    # GB/T-like entries often use "Surname Initials"; metadata often has
    # "Given Family". Prefer the first token for citation-list snippets.
    return parts[0].lower()


def parse_current_authors(row: dict) -> list[str]:
    explicit = pick(row, ["作者", "authors", "author"])
    reference = pick(row, ["格式化参考文献", "参考文献", "reference", "citation"])
    raw = explicit or reference
    if not raw:
        return []
    raw = re.sub(r"^\s*\[\d+\]\s*", "", raw)
    if explicit:
        head = raw
    else:
        head = raw.split(".", 1)[0]
    head = re.split(r"\bet al\.?", head, flags=re.I)[0]
    parts = [p.strip() for p in re.split(r"\s*,\s*|\s+and\s+", head) if p.strip()]
    return [s for s in (surname(p) for p in parts) if s]


def crossref_metadata(doi: str) -> dict:
    status, data = request_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
    if status == 200 and data and data.get("message"):
        msg = data["message"]
        authors = []
        for item in msg.get("author") or []:
            family = item.get("family") or ""
            if family:
                authors.append(surname(family))
        return {
            "source": "Crossref",
            "title": (msg.get("title") or [""])[0],
            "authors": authors,
            "publisher": msg.get("publisher") or "",
            "status": status,
        }
    return {}


def datacite_metadata(doi: str) -> dict:
    status, data = request_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""))
    if status == 200 and data and data.get("data"):
        attrs = data["data"].get("attributes") or {}
        titles = attrs.get("titles") or []
        creators = attrs.get("creators") or []
        authors = []
        for item in creators:
            family = item.get("familyName") or ""
            if not family and item.get("name"):
                family = item["name"].split(",", 1)[0]
            if family:
                authors.append(surname(family))
        return {
            "source": "DataCite",
            "title": (titles[0] or {}).get("title") if titles else "",
            "authors": authors,
            "publisher": attrs.get("publisher") or "",
            "status": status,
        }
    return {}


def author_match(current: list[str], authority: list[str]) -> tuple[bool, str]:
    if not current or not authority:
        return False, "Missing current or authority author metadata."
    if current[0] == authority[0]:
        return True, "First-author surname matches."
    overlap = len(set(current[:3]) & set(authority[:3]))
    if overlap >= min(2, len(current), len(authority)):
        return True, "Top-three surname overlap is sufficient."
    return False, "First-author surname and top-author overlap do not match."


def verify(row: dict) -> dict:
    ref = pick(row, ["新增编号", "编号", "id", "ref"])
    title = pick(row, ["引用论文", "论文题名", "title"])
    reference = pick(row, ["格式化参考文献", "参考文献", "reference", "citation"])
    doi_url = pick(row, ["DOI/URL", "doi", "url", "URL"])
    doi = doi_from(doi_url, reference)
    current_authors = parse_current_authors(row)

    metadata = crossref_metadata(doi) if doi else {}
    if doi and not metadata:
        metadata = datacite_metadata(doi)
    if doi:
        time.sleep(0.1)

    if not metadata:
        conclusion = "需人工复核"
        note = "No Crossref/DataCite metadata was found for the DOI."
        return {
            "编号": ref,
            "论文题名": title,
            "当前DOI": doi,
            "题名作者结论": conclusion,
            "当前作者姓氏": "; ".join(current_authors),
            "权威题名": "",
            "权威作者姓氏": "",
            "元数据来源": "",
            "相似度": "",
            "说明": note,
        }

    score = title_score(title, metadata["title"])
    t_ok = score >= 0.9
    a_ok, author_note = author_match(current_authors, metadata["authors"])
    if t_ok and a_ok:
        conclusion = "匹配"
        note = "Title and author metadata match the authority source."
    elif not t_ok and a_ok:
        conclusion = "题名需人工复核"
        note = "Authors match, but the authority title differs or is abbreviated."
    elif t_ok and not a_ok:
        conclusion = "作者需人工复核"
        note = author_note
    else:
        conclusion = "需人工复核"
        note = "Both title and author metadata need manual review."

    return {
        "编号": ref,
        "论文题名": title,
        "当前DOI": doi,
        "题名作者结论": conclusion,
        "当前作者姓氏": "; ".join(current_authors),
        "权威题名": metadata["title"],
        "权威作者姓氏": "; ".join(metadata["authors"]),
        "元数据来源": metadata["source"],
        "相似度": f"{score:.3f}",
        "说明": note,
    }


def write_reports(rows: list[dict], out_prefix: Path, write_csv: bool = False) -> None:
    out_prefix.parent.mkdir(parents=True, exist_ok=True)
    md_path = out_prefix.with_suffix(".md")
    if write_csv:
        csv_path = out_prefix.with_suffix(".csv")
        with csv_path.open("w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)
        print(csv_path)

    counts: dict[str, int] = {}
    for row in rows:
        counts[row["题名作者结论"]] = counts.get(row["题名作者结论"], 0) + 1
    md = ["# Title-Author Metadata Audit", "", "## Summary"]
    md.extend(f"- {k}: {v}" for k, v in sorted(counts.items()))
    md.append("")
    md.append("## Details")
    for row in rows:
        md.extend([
            f"### {row['编号']} {row['论文题名']}",
            f"- Result: {row['题名作者结论']}",
            f"- Authority title: {row['权威题名']}",
            f"- Current surnames: {row['当前作者姓氏']}",
            f"- Authority surnames: {row['权威作者姓氏']}",
            f"- Source: {row['元数据来源']}",
            f"- Note: {row['说明']}",
            "",
        ])
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(md_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--out-prefix", type=Path, default=Path("title_author_audit"))
    ap.add_argument("--write-csv", action="store_true", help="also write a CSV report for machine-readable QA")
    args = ap.parse_args()
    with args.input_csv.open(encoding="utf-8-sig", newline="") as f:
        rows = [verify(row) for row in csv.DictReader(f)]
    if not rows:
        raise SystemExit("input CSV has no rows")
    write_reports(rows, args.out_prefix, args.write_csv)


if __name__ == "__main__":
    main()
