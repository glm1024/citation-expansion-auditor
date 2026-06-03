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
- `建议插入点`: `放在“早期融合策略多采用特征级拼接或决策级集成，将日志统计特征、调用链拓扑属性与指标时序向量简单组合后输入分类模型。”之后`
- `原始文本`: include the paragraph with inline markers, for example `...输入分类模型。[46] 此类浅层融合...`

Risky:

- A group such as `[37-42]` that spans several paragraphs and topics.
- Adding seven new citations at the end of a paragraph that already has four targeted references.
- Placing method-specific citations at paragraph end when they only support one phrase.
- `建议插入点`: `异构数据融合、图表示和可解释 RCA 相关句后`. This is a summary, not an executable insertion point.

When multiple citations go into one paragraph, mark them directly inside the original paragraph text:

```text
早期融合策略多采用特征级拼接或决策级集成，将日志统计特征、调用链拓扑属性与指标时序向量简单组合后输入分类模型。[46] 此类浅层融合虽实现了数据层面的整合，却未能解决异构数据间的语义鸿沟问题，指标的低频趋势特征与日志的高频离散特征在简单拼接中相互干扰，导致模型难以学习跨模态的深层关联。随着图神经网络的发展，近期研究开始尝试以系统依赖拓扑为骨架，将多模态数据作为节点属性进行图卷积运算，通过消息传递机制聚合邻居信息以实现根因定位。[47] 例如，ART [9] 利用深度自编码器融合多源指标并构建服务依赖图进行根因定位，Eadro [10] 则通过时空图神经网络联合建模调用链结构与指标时序特征。该类方法在一定程度上提升了复杂故障的定位精度，但仍面临特征工程依赖与可解释性不足的挑战。[48-49] 现有融合架构多采用端到端黑盒模型，其决策过程缺乏透明度，运维人员难以理解模型为何将特定节点判定为根因，限制了方法在关键业务场景中的落地应用。此外，现有方法普遍假设训练数据与测试数据分布一致，面对云原生环境下服务拓扑动态演化与未知故障模式时，泛化能力受限。
```

This pattern makes the output directly editable and prevents vague placement guidance.

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
