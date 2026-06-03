# Citation Expansion Auditor

A Codex skill for expanding and auditing academic citations in existing manuscripts.

It is designed for workflows where a user needs to:

- increase a bibliography to a target count;
- find upstream or related papers from existing references;
- place new citations by paragraph and claim;
- verify that added papers are real;
- check title-author metadata and duplicate references;
- respond to external reviewer feedback about citation quality.

The skill is intentionally conservative. It treats every citation as a claim-level evidence decision, not just a topic match.

## Contents

- `SKILL.md`: main skill instructions.
- `references/audit-rules.md`: verification rules and common failure modes.
- `references/output-schema.md`: recommended CSV/XLSX/Markdown output fields.
- `scripts/extract_docx_text.py`: extract stable paragraph numbers and reference-list text from DOCX.
- `scripts/check_paper_existence.py`: verify DOI/URL existence evidence.
- `scripts/check_title_author_match.py`: compare proposed title/authors against Crossref/DataCite metadata.
- `scripts/validate_citation_proposal.py`: catch duplicate DOI/title, missing metadata, long excerpts, and citation-group issues.
- `evals/evals.json`: example evaluation prompts.

## Quick Validation

```bash
python3 -m py_compile scripts/*.py
npx skills add /path/to/citation-expansion-auditor -l
```
