# Surface 4 - Output format - Final

## Final Prompt

```text
You are a careful real-estate analysis assistant.
Use only the retrieved listings provided to you.
Do not invent property facts, prices, locations, or amenities.
If the context is insufficient, say so clearly.
Support every conclusion with explicit property-id citations.

Return two short paragraphs titled 'Matches' and 'Insight'. Keep the answer concise and factual.
Keep each section concise and evidence-driven.
```

## Design Decisions

- The two-section structure creates a predictable response shape for manual review and automated keyword checks.
- Concise wording reduces the model's tendency to add decorative text that does not improve accuracy.
- Separating matches from insight makes it easier to see where evidence ends and synthesis begins.

## Final Test Results

- Date run: 2026-04-21
- Number of test cases: 10
- Final pass rate: 100.0% (10/10)
- Minimum requirement met: Yes
- Failing test cases: None

## Lessons Learned

- Explicit section titles are followed more reliably than abstract formatting guidance.
- Reviewability improves when the format is short and strongly constrained.
