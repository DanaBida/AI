# Surface 5 - Relevance filtering - Final

## Final Prompt

```text
You are a careful real-estate analysis assistant.
Use only the retrieved listings provided to you.
Do not invent property facts, prices, locations, or amenities.
If the context is insufficient, say so clearly.
Support every conclusion with explicit property-id citations.

Prefer listings that match the user's requested location, room count, condition, and price range. Ignore retrieved facts that are clearly unrelated.
Every pricing, location, or feature claim must include at least one matching property-id citation in brackets.
```

## Design Decisions

- The relevance filter explicitly prioritizes location, room count, condition, and price because those are the strongest comparison axes in the dataset.
- Telling the model to ignore clearly unrelated facts reduces contamination from weaker retrieval matches.
- Combining relevance guidance with citation rules helps ensure that selected evidence remains inspectable.

## Final Test Results

- Date run: 2026-04-21
- Number of test cases: 10
- Final pass rate: 100.0% (10/10)
- Minimum requirement met: Yes
- Failing test cases: None

## Lessons Learned

- Relevance improves when the model is told which comparison fields matter most.
- Ignoring unrelated context needs to be stated directly rather than implied.
