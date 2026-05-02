# Final Tool Descriptions

## Final Tool Metadata

- `rag_search`: Search structured property knowledge and listing text. Use this tool for listing facts, bedrooms, bathrooms, price, location, market comparisons, renovation history, and any request that depends on textual listing data. Prefer this tool when the answer can be grounded in listing attributes or retrieved documents.
- `image_analysis`: Analyze property photos to identify visible rooms, surface wear, damage, cleanliness, and estimated condition scores. Use this tool only for claims that depend on visual evidence from images. Do not use it for hidden structural issues or non-visible listing attributes.

## Surface 1

### Final Prompt

Choose tools conservatively. Use rag_search for listing facts, counts, comparisons, location, price, and market context. Use image_analysis only when the user asks about visible rooms, visible damage, room condition, or issues detectable from photos. Use both tools when the request needs listing facts plus visual condition evidence. If information is missing, say so instead of guessing.

### Design Decisions

The final planner wording separates listing facts from visible evidence, explicitly permits both tools, and adds an anti-guessing rule to reduce overreach.

### Final Pass Rate

- 10/10 (100.0%)

### What We Learned

Reliable planner prompts are explicit about when to use one tool versus both. Broad phrases like 'analyze the query' were too weak on their own.

## Surface 2

### Final Prompt

Rewrite the user's request into a retrieval query that preserves the core constraints: property type, city, neighborhood, price band, comparison target, time or market context, and requested outcome. Keep the query short, specific, and noun-heavy. Do not introduce details that were not asked for.

### Design Decisions

The final retrieval wording preserves user constraints, keeps the query short, and forbids invented details so downstream search remains precise.

### Final Pass Rate

- 10/10 (100.0%)

### What We Learned

Constraint-preserving prompts outperform generic rewrite prompts. The model responds better to concrete reminders about city, price, comparison target, and outcome.

## Surface 3

### Final Prompt

Interpret image-analysis results using only visible evidence. Explain what a condition score means in plain language, note confidence, and separate minor cosmetic wear from potential safety or structural concerns. Never claim hidden defects unless the evidence clearly shows them.

### Design Decisions

The final image wording ties every conclusion to visible evidence, explains scores plainly, and blocks hidden-defect speculation.

### Final Pass Rate

- 10/10 (100.0%)

### What We Learned

Image interpretation is safest when the prompt repeats 'visible evidence' and warns against hidden-defect claims. Confidence language noticeably improves restraint.

## Surface 4

### Final Prompt

Synthesize multi-source results into one grounded answer. Lead with the direct answer, then connect listing facts and image findings. Call out conflicts, state which source supports each conclusion, and end with practical next steps or follow-up data needed.

### Design Decisions

The final synthesis wording forces a direct answer first, then source-aware evidence, conflicts, and concrete next steps.

### Final Pass Rate

- 10/10 (100.0%)

### What We Learned

Synthesis quality improves when structure is specified directly: answer first, evidence second, conflicts third, next steps last.

## Surface 5

### Final Prompt

Recover gracefully from missing or conflicting tool data. If one tool is unavailable, continue with the other and label the limitation. If sources conflict, report the conflict explicitly, prefer the more direct evidence, and suggest the smallest next action needed to resolve uncertainty.

### Design Decisions

The final recovery wording keeps answers useful under failures, labels limitations, prioritizes direct evidence, and prompts a minimal next action.

### Final Pass Rate

- 10/10 (100.0%)

### What We Learned

Error recovery becomes more reliable when the prompt says exactly how to degrade gracefully instead of vaguely asking for robustness.
