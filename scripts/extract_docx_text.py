#!/usr/bin/env python3
"""Extract numbered paragraphs and reference-list text from a DOCX file.

This script intentionally uses only the Python standard library. It reads
word/document.xml directly, which is enough for audit workflows that need stable
paragraph numbers and bibliography text.
"""

from __future__ import annotations

import argparse
import json
import re
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


NS = {"w": "http://schemas.openxmlformats.org/wordprocessingml/2006/main"}


def paragraph_text(p: ET.Element) -> str:
    parts: list[str] = []
    for node in p.iter():
        if node.tag == f"{{{NS['w']}}}t" and node.text:
            parts.append(node.text)
        elif node.tag == f"{{{NS['w']}}}tab":
            parts.append("\t")
        elif node.tag == f"{{{NS['w']}}}br":
            parts.append("\n")
    return re.sub(r"[ \t]+", " ", "".join(parts)).strip()


def extract_docx(path: Path) -> list[dict]:
    with zipfile.ZipFile(path) as zf:
        xml = zf.read("word/document.xml")
    root = ET.fromstring(xml)
    paragraphs = []
    for idx, p in enumerate(root.findall(".//w:body/w:p", NS), start=1):
        text = paragraph_text(p)
        paragraphs.append({"idx": idx, "text": text})
    return paragraphs


def find_refs_start(paragraphs: list[dict]) -> int | None:
    for p in paragraphs:
        text = re.sub(r"\s+", "", p["text"]).lower()
        if text in {"参考文献", "references", "bibliography"}:
            return p["idx"]
    for p in paragraphs:
        if re.match(r"^\s*\[\d+\]", p["text"]):
            return p["idx"]
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("--out-dir", type=Path, default=Path("extracted"))
    args = ap.parse_args()

    args.out_dir.mkdir(parents=True, exist_ok=True)
    paragraphs = extract_docx(args.docx)
    refs_start = find_refs_start(paragraphs)
    references = [p for p in paragraphs if refs_start and p["idx"] >= refs_start]

    payload = {
        "docx": str(args.docx),
        "paragraph_count": len(paragraphs),
        "refs_start": refs_start,
        "paragraphs": paragraphs,
        "references": references,
    }
    (args.out_dir / "extracted.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
    with (args.out_dir / "paragraphs.txt").open("w", encoding="utf-8") as f:
        for p in paragraphs:
            f.write(f"{p['idx']:04d} {p['text']}\n")
    with (args.out_dir / "references.txt").open("w", encoding="utf-8") as f:
        for p in references:
            f.write(f"{p['idx']:04d} {p['text']}\n")
    print(args.out_dir / "extracted.json")


if __name__ == "__main__":
    main()

