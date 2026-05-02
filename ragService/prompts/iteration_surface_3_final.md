# Surface 3 - Context injection - Final

## Final Prompt

```text
{system_prompt}

Retrieved listings:
{context}

User query:
{query}

Response requirements:
1. Summarize the closest market matches.
2. Explain the reasoning using only retrieved facts.
3. Cite property ids inline, for example [prop_001].
4. Mention uncertainty when context does not fully support a claim.

Present retrieved listings in numbered order with normalized fields for price, rooms, bedrooms, bathrooms, location, condition, and description.
```

## Design Decisions

- A stable numbered context layout makes it easier for the model to trace facts back to specific listings.
- Normalized property fields reduce ambiguity caused by inconsistent wording across retrieved documents.
- Separating system prompt, context block, and query helps the model distinguish evidence from user intent.

## Final Test Results

- Date run: 2026-04-21
- Number of test cases: 10
- Final pass rate: 100.0% (10/10)
- Minimum requirement met: Yes
- Failing test cases: None

## Lessons Learned

- Structured context formatting is more reliable than raw document dumps.
- Field normalization improves consistency in comparisons and summaries.
