# Output Schema

Use these fields for citation expansion deliverables. The default user-facing deliverable is one Markdown file, not Excel/XLSX. CSV may be used only as an internal machine-readable intermediate or when the user explicitly asks.

## Citation Suggestion Section

For each proposed citation or citation group, include these Markdown fields:

- `新增编号`: reference number, such as `[37]`.
- `原始文本`: paragraph text from the manuscript with citation markers inserted. For no-citation paragraph-level groups, append one group at the paragraph end; for existing-citation paragraphs, mark local insertions or expanded existing references.
- `引用论文`: complete formatted reference entry in the requested style.
- `相关文本摘录`: exact complete sentence from the paper, official abstract, or authoritative index abstract. Do not output a sentence fragment such as text ending in `and`, `with`, or `for`.
- `摘录来源`: PDF section, official abstract, Crossref/OpenAlex abstract, etc.
- `引用理由`: why this paper can be used as a citation for this manuscript paragraph, including any limitation.
- `摘录可信理由`: why the quoted source sentence is relevant and credible evidence for the paragraph claim.
- `复核结论`: direct pass, limited pass, replacement rationale, or warning in reader-friendly language.
- `DOI/URL`: DOI or official page.
- `发表年份`, `引用次数`, `元数据校验来源`, `摘录URL`: optional but useful.

Do not include per-item internal process fields such as `建议位置`, `推荐插入说明`, `密度处理说明`, or `相关性说明` in the clean Markdown handoff when `原始文本` already marks the citation location. Those fields may be used in internal CSV/audit drafts only.

## Grouped Insertion Strategy Section

This section is optional. Use it only when the user wants density review or planning context. Keep it separate from per-paper detail entries.

- `建议引用形式`
- `段落编号`
- `插入方式`
- `建议插入点`: use paragraph-end grouping for no-citation paragraph-level groups (`放在整段末尾`); quote exact original sentence anchors only for existing-citation local insertions or rewrite exceptions.
- `主题`
- `原段已有引用数`
- `本处新增引用数`
- `处理建议`
- `该组论文`

## Audit Reports

Create Markdown sections when useful:

1. `逐篇核验报告`: semantic fit and action.
2. `题名作者核验报告`: title-author match against Crossref/official pages.
3. `真实性核验报告`: paper existence and evidence URL.
4. `外部评审意见处理说明`: accepted/rejected/already-handled reviewer feedback.

For audit verdicts, use:

- `通过`
- `限定后通过`
- `已替换后通过`
- `不建议新增`
- `需人工复核`

## Evidence Excerpts

Use short exact excerpts. Prefer a complete sentence. Keep it under 25 words unless the user explicitly needs more and copyright constraints allow it. If the most relevant sentence is too long, choose a shorter complete sentence from the same source and use `摘录可信理由` to explain the semantic match.

Do not paraphrase evidence as if it were original text.

## Final Summary

When handing off, include:

- Number of added citations.
- Count by audit verdict.
- Any replacements or duplicates removed.
- Any claims requiring manuscript wording changes.
- Link to the Markdown handoff file when one is saved.
