---
name: citation-expansion-auditor
description: Use when expanding academic references for an existing manuscript and auditing added citations. This skill is for tasks like increasing a thesis/paper bibliography to a target count, finding upstream/related papers from current references, placing new citations by paragraph, checking reference formatting consistency, and verifying that every added paper really exists, has matching title/authors, is not duplicated, and semantically supports the exact manuscript claim. Use this whenever the user asks to add references, expand citations, audit citation correctness, verify DOI/title/authors, check whether references are fabricated, or respond to reviewer/friend feedback about citation quality.
---

# Citation Expansion Auditor

This skill expands and audits academic citations for an existing manuscript. The core job is not "find many papers"; it is to produce citations the user can safely verify and insert by hand.

## Core Workflow

1. Ingest the manuscript and current bibliography.
   - Extract paragraph numbers, paragraph text, existing in-text citation counts, and the reference list.
   - Preserve the original manuscript unless the user explicitly asks for edits.
   - Keep paragraph numbering stable in all outputs.

2. Clarify the target.
   - Target reference count or range, such as adding 44 references to reach 80.
   - Citation style required by the thesis/journal.
   - Whether "continuous citations" means grouped within one paragraph. Default: yes. A group like `[37-39]` should belong to one paragraph, not span unrelated paragraphs.

3. Find candidate papers.
   - Start from the manuscript topic and current references.
   - Prefer upstream papers cited by current references, survey bibliographies, and canonical method papers.
   - Also use scholarly databases and official publication pages.
   - Track DOI/URL, venue, year, authors, and evidence source for every candidate.

4. Place citations by claim, not by theme alone.
   - Map each candidate to the exact paragraph and sentence-level claim it supports.
   - If the original paragraph has no citations and the added papers are paragraph-level background or survey support, use one paragraph-end continuous group such as `[37-39]`. Do not split it into multiple local markers.
   - For no-citation paragraph-level groups, write `建议位置` / `建议插入点` as "place at the end of the whole paragraph." Do not write "after the `xxx` sentence" even when `xxx` is the final sentence; reserve quoted sentence anchors for existing-citation paragraphs or rewrite exceptions.
   - If the original paragraph already has citations, quote the exact original sentence used as the insertion anchor. Do not describe the anchor with a summary such as "after the heterogeneous-data sentence" unless those exact words appear in the manuscript.
   - In the `原始文本` field, provide a marked version of the original paragraph. For no-citation paragraph-level groups, append the group at the paragraph end; for existing-citation paragraphs, insert or extend markers at the proposed locations.
   - If a paragraph already has several targeted citations, insert new citations near the relevant sentence instead of dumping them at the paragraph end.
   - If a no-citation paragraph contains later claims the papers do not support, either mark the paragraph-end group as `限定后通过` with a limitation note, or recommend a sentence rewrite when paragraph-end placement would be misleading.

5. Verify each citation before handoff.
   - Existence: DOI metadata, official publication page, official PDF, OpenReview/NeurIPS/ACM/IEEE/Elsevier/Springer page, or a recognized preprint record.
   - Title-author match: current reference title and first authors must match an authority source.
   - Non-duplication: compare against existing references and the added list by DOI and normalized title.
   - Semantic fit: the evidence must support the exact manuscript claim. If it only supports a narrower claim, say so.
   - Formatting: use the requested style consistently and prefer formal proceedings/journal versions over arXiv when available.

6. Deliver user-facing files.
   - Produce one Markdown handoff file by default. Do not create Excel/XLSX deliverables unless the user explicitly asks.
   - Include a detailed citation suggestion section for manual manuscript editing. The `原始文本` field should already contain the proposed citation marker, so do not repeat internal fields such as insertion-position notes, recommendation notes, or density notes in each item unless the user explicitly asks for an audit trace.
   - Include a grouped insertion strategy section only when it helps the user review density. Keep it separate from per-paper details, or omit it when the user asks for a clean handoff file.
   - Include audit sections as needed: semantic fit, title-author match, existence, duplicate detection, and reviewer-feedback handling.
   - Use exact evidence excerpts. Prefer one complete sentence from the paper, official abstract, or authoritative index abstract; do not truncate mid-sentence. If the most relevant sentence is too long, choose a shorter complete sentence from the same source and explain the closer semantic match in Chinese.
   - For every paper, split semantic explanation into two reader-facing fields: why this paper can cite the manuscript paragraph, and why the quoted paper sentence is the most relevant/credible evidence.
   - Do not invent paper text.

## Quality Gates

Read [audit-rules.md](references/audit-rules.md) before finalizing added references. It contains the verification criteria and common failure modes from real thesis citation work.

Use [output-schema.md](references/output-schema.md) when creating Markdown deliverables.

Use scripts when the input shape matches:

| Need | Script |
| --- | --- |
| Extract paragraphs and references from `.docx` | `scripts/extract_docx_text.py` |
| Check added references exist | `scripts/check_paper_existence.py` |
| Check title-author match | `scripts/check_title_author_match.py` |
| Validate citation proposal CSV for duplicates, ranges, and excerpt length | `scripts/validate_citation_proposal.py` |

The scripts read CSV when convenient, but their default report output is Markdown. Use `--write-csv` only for machine-readable intermediate QA.

## Judgment Rules

- Treat reviewer/friend feedback as hypotheses. Check it against the manuscript and paper evidence before adopting it.
- A paper being real is not enough; it must support the marked claim.
- A paper supporting a broad topic is not enough; it must not be cited as evidence for a narrower method detail it does not contain.
- When evidence is narrower than the manuscript sentence, either recommend a sentence rewrite or move the citation to a narrower insertion point.
- When an existing reference already covers the paper, reuse the existing reference number instead of adding a duplicate. If the user still needs the target count, replace the duplicate with a different non-duplicate paper.
- Prefer formal publication metadata over preprint metadata when both refer to the same work.
- If a title is commonly shortened in Crossref, verify against the official paper page or PDF before marking it wrong.
- Chinese GB/T-like reference lists often write names as `Surname Initials`; compare surnames carefully against Western full-name metadata.

## Output Tone

Be conservative and explicit. For each questionable item, say one of:

- `通过`: the paper directly supports the target claim.
- `限定后通过`: the paper is valid but supports only a narrower claim.
- `已替换后通过`: the original candidate was replaced due to mismatch, duplication, weak evidence, or better formal metadata.
- `不建议新增`: reuse an existing reference or remove it from the added set.
- `需人工复核`: authoritative evidence was insufficient or contradictory.

When the user will manually edit the manuscript, provide original paragraph text with inline citation markers, the formatted reference entry, one exact complete-sentence evidence excerpt, evidence source, `引用理由`, `摘录可信理由`, and a clear review conclusion/limitation note.
