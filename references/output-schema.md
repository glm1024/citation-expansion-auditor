# Output Schema

Use these fields for citation expansion deliverables. The default user-facing deliverable is one Markdown file, not Excel/XLSX. CSV may be used only as an internal machine-readable intermediate or when the user explicitly asks.

## Citation Suggestion Section

For each proposed citation or citation group, include these Markdown fields:

- `新增编号`: reference number, such as `[37]`.
- `建议引用形式`: grouped in-text citation form, such as `[37-39]`.
- `段落编号`: manuscript paragraph number.
- `插入方式`: `就近插入`, `段尾连续引用`, `改写后段尾引用`, or similar.
- `建议插入点`: for no-citation paragraph-level support, use `段尾连续引用，放在整段末尾`; do not phrase it as `放在“xxx”之后` even if `xxx` is the final sentence. For existing-citation paragraphs, quote the exact original sentence anchor, such as `放在“xxx”之后`.
- `原段已有引用数`: count of current references in the paragraph.
- `本处新增引用数`: count added at this location.
- `原始文本`: paragraph text from the manuscript with citation markers inserted. For no-citation paragraph-level groups, append one group at the paragraph end; for existing-citation paragraphs, mark local insertions or expanded existing references.
- `推荐插入说明`: concise actionable instruction.
- `密度处理说明`: why this does or does not overload the paragraph.
- `引用论文`: paper title.
- `格式化参考文献`: complete reference entry in the requested style.
- `相关文本摘录`: exact evidence excerpt from the paper or official abstract.
- `摘录来源`: PDF section, official abstract, Crossref/OpenAlex abstract, etc.
- `相关性说明`: what claim the paper supports.
- `复核结论`: direct pass, limited pass, replacement rationale, or warning.
- `DOI/URL`: DOI or official page.
- `发表年份`, `引用次数`, `元数据校验来源`, `摘录URL`: optional but useful.

## Grouped Insertion Strategy Section

For paragraph-level groups, include:

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

Use short exact excerpts. Keep them under 25 words unless the user explicitly needs more and copyright constraints allow it. If the exact sentence in the source is longer, excerpt the relevant clause and state the source.

Do not paraphrase evidence as if it were original text.

## Final Summary

When handing off, include:

- Number of added citations.
- Count by audit verdict.
- Any replacements or duplicates removed.
- Any claims requiring manuscript wording changes.
- Link to the Markdown handoff file when one is saved.
