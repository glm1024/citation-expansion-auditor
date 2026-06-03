# Citation Audit Rules

These rules are based on a real workflow that expanded a thesis from 36 to 80 references, then corrected the added citations through multiple reviewer-style audits.

## Evidence Hierarchy

Prefer evidence in this order:

1. DOI metadata from Crossref/DataCite plus publisher page.
2. Official conference/journal page: ACM, IEEE, Elsevier, Springer, AAAI, IJCAI, NeurIPS, OpenReview, COLM, etc.
3. Official author/institution PDF, such as Google Research or university-hosted PDF.
4. Recognized preprint record, such as arXiv DOI/DataCite, when no formal version exists.
5. Scholarly indexes such as OpenAlex or Semantic Scholar only as support, not as the only evidence for a critical claim.

Search engine snippets, ResearchGate mirrors, and copied abstract pages are discovery aids, not final proof.

## Semantic Fit Tests

For every proposed citation, answer these questions:

1. What exact sentence or claim in the manuscript will the citation support?
2. Does the paper directly state or demonstrate that claim?
3. If not direct, what narrower claim can it support?
4. Would an examiner think the citation implies a method or result the paper does not contain?
5. Is this citation already covered by an existing reference?

If the paper supports only a narrower claim, mark it `限定后通过` and provide a safer insertion note.

## Citation Placement

Use citation groups by paragraph. Do not create a "continuous citation group" by collecting papers from unrelated paragraphs.

Good:

- Paragraph 149: `[37-39]`
- Paragraph 160 metrics sentence: `[43]`
- Paragraph 160 logs sentence: `[44]`
- Paragraph 160 traces sentence: `[45]`

Risky:

- A group such as `[37-42]` that spans several paragraphs and topics.
- Adding seven new citations at the end of a paragraph that already has four targeted references.
- Placing method-specific citations at paragraph end when they only support one phrase.

## Density Rules

- Existing citations near exact method names should be extended locally, not overridden by paragraph-end groups.
- If a paragraph already contains several references, use fewer added citations and distribute them near matching clauses.
- For discussion paragraphs with no citations, a paragraph-end group can work if all papers support the paragraph-level summary.
- Avoid creating 10+ references in one paragraph unless the paragraph is explicitly a survey paragraph.

## Common Failure Modes

### TraceRCA-like overreach

A trace RCA paper may support "distributed traces can help localize root-cause microservices" but not "our recursive backtracking algorithm" or "LLM causal-context construction." Recommend a rewrite or additional direct references.

### RAG and incident retrieval

An incident retrieval paper may support searching historical incidents and root-cause knowledge. It does not automatically support an LLM cross-validation mechanism or logical-bias correction. Pair it with a RAG paper if needed.

### Hallucination mitigation

A hallucination survey supports the existence and risk of hallucination in NLG/LLMs. It does not directly support a custom prompt schema, JSON constraint, or evidence-first rule unless the paper explicitly studies that mechanism.

### CoT and adjacent reasoning papers

If the paragraph is about Chain-of-Thought, use the original CoT reference if already present. Tree of Thoughts and Self-Consistency are useful adjacent extensions; Reflexion is about reflection/memory agents and is not a direct CoT citation.

### Formal publication upgrades

If an arXiv paper has a formal conference or journal version, prefer the formal version in the bibliography. Keep the arXiv only when it is the authoritative or only version.

### Duplicate papers

Normalize titles and DOI strings before adding references. If an existing reference already contains the same paper, reuse the existing number. To preserve a target count, replace the duplicate with a different non-duplicate paper.

### Short title metadata

Crossref may return short titles such as `DeepLog`, `Sieve`, or `DeepTraLog`, while the official paper page includes the full subtitle. Verify with the publisher page or PDF before deciding the title is wrong.

### Name format mismatch

Chinese/GB-style references often use `Surname Initials`, while metadata sources use full Western names. Compare surnames and order, not raw strings.

## Reviewer Feedback Handling

When the user provides external feedback:

1. Extract each concrete claim.
2. Classify it: semantic scope, duplicate, metadata, title-author, existence, formatting, or density.
3. Verify against the manuscript and authoritative paper metadata.
4. Adopt only factually correct feedback.
5. If the feedback is already handled, say so and keep the current output.
6. Generate a handling report listing accepted changes, rejected claims, and already-handled points.

