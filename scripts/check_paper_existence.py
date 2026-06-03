#!/usr/bin/env python3
"""Check whether proposed citation papers have authoritative existence evidence.

Input: CSV with columns such as:
- 新增编号 / id / ref
- 引用论文 / title
- DOI/URL / doi / url

Output: Markdown report by default. Use --write-csv for a machine-readable
intermediate report.
"""

from __future__ import annotations

import argparse
import csv
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


def doi_from(value: str) -> str:
    value = (value or "").strip()
    value = re.sub(r"^https?://(?:dx\.)?doi\.org/", "", value, flags=re.I)
    return value if value.lower().startswith("10.") else ""


def request_json(url: str) -> tuple[int, dict | None, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "citation-expansion-auditor"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            return resp.status, json.loads(resp.read().decode("utf-8", "replace")), resp.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, None, url
    except Exception:
        return 0, None, url


def request_url(url: str) -> tuple[int, str]:
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 citation-expansion-auditor"})
    try:
        with urllib.request.urlopen(req, timeout=25) as resp:
            resp.read(2048)
            return resp.status, resp.geturl()
    except urllib.error.HTTPError as exc:
        return exc.code, url
    except Exception:
        return 0, url


def normalize_title(title: str) -> str:
    title = html.unescape(title or "")
    title = re.sub(r"[^a-z0-9]+", " ", title.lower())
    return re.sub(r"\s+", " ", title).strip()


def title_ok(current: str, authority: str) -> bool:
    c = normalize_title(current)
    a = normalize_title(authority)
    return bool(c and a and (c == a or c in a or a in c))


def verify(row: dict) -> dict:
    ref = pick(row, ["新增编号", "编号", "id", "ref"])
    title = pick(row, ["引用论文", "论文题名", "title"])
    doi_url = pick(row, ["DOI/URL", "doi", "url", "URL"])
    doi = doi_from(doi_url)

    evidence = {"source": "", "status": "", "url": doi_url, "title": "", "publisher": ""}
    if doi:
        status, data, final_url = request_json("https://api.crossref.org/works/" + urllib.parse.quote(doi, safe=""))
        if status == 200 and data and data.get("message"):
            msg = data["message"]
            authority_title = (msg.get("title") or [""])[0]
            evidence = {
                "source": "Crossref DOI metadata",
                "status": status,
                "url": "https://doi.org/" + doi,
                "title": authority_title,
                "publisher": msg.get("publisher") or "",
            }
        else:
            status, data, final_url = request_json("https://api.datacite.org/dois/" + urllib.parse.quote(doi, safe=""))
            if status == 200 and data and data.get("data"):
                attrs = data["data"].get("attributes") or {}
                titles = attrs.get("titles") or []
                authority_title = (titles[0] or {}).get("title") if titles else ""
                evidence = {
                    "source": "DataCite DOI metadata",
                    "status": status,
                    "url": "https://doi.org/" + doi,
                    "title": authority_title,
                    "publisher": attrs.get("publisher") or "",
                }
            else:
                status, final_url = request_url("https://doi.org/" + doi)
                if 200 <= status < 400:
                    evidence = {"source": "DOI resolver", "status": status, "url": final_url, "title": "", "publisher": ""}
        time.sleep(0.1)

    if not evidence["source"] and doi_url:
        status, final_url = request_url(doi_url)
        if 200 <= status < 400:
            evidence = {"source": "Official/landing URL", "status": status, "url": final_url, "title": "", "publisher": ""}

    if not evidence["source"]:
        conclusion = "未核实"
        note = "No DOI metadata or accessible official URL was found."
    elif evidence["title"] and not title_ok(title, evidence["title"]):
        conclusion = "需人工复核"
        note = "Authority source exists, but the title differs from the proposal."
    else:
        conclusion = "真实存在"
        note = "Authority source exists and title is consistent or the source is a known landing page/PDF."

    return {
        "编号": ref,
        "论文题名": title,
        "当前DOI/URL": doi_url,
        "真实性结论": conclusion,
        "证据来源": evidence["source"],
        "HTTP状态": evidence["status"],
        "证据URL": evidence["url"],
        "权威题名": evidence["title"],
        "出版社/页面信息": evidence["publisher"],
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
        counts[row["真实性结论"]] = counts.get(row["真实性结论"], 0) + 1
    md = ["# Paper Existence Audit", "", "## Summary"]
    md.extend(f"- {k}: {v}" for k, v in sorted(counts.items()))
    md.append("")
    md.append("## Details")
    for row in rows:
        md.extend([
            f"### {row['编号']} {row['论文题名']}",
            f"- Result: {row['真实性结论']}",
            f"- Evidence: {row['证据来源']}",
            f"- URL: {row['证据URL']}",
            f"- Authority title: {row['权威题名']}",
            f"- Note: {row['说明']}",
            "",
        ])
    md_path.write_text("\n".join(md), encoding="utf-8")
    print(md_path)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("input_csv", type=Path)
    ap.add_argument("--out-prefix", type=Path, default=Path("paper_existence_audit"))
    ap.add_argument("--write-csv", action="store_true", help="also write a CSV report for machine-readable QA")
    args = ap.parse_args()
    with args.input_csv.open(encoding="utf-8-sig", newline="") as f:
        rows = [verify(row) for row in csv.DictReader(f)]
    write_reports(rows, args.out_prefix, args.write_csv)


if __name__ == "__main__":
    main()
