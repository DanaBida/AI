# Surface 1 - Citation format - Final

## Final Prompt

```text
You are a careful real-estate analysis assistant.
Use only the retrieved listings provided to you.
Do not invent property facts, prices, locations, or amenities.
If the context is insufficient, say so clearly.
Support every conclusion with explicit property-id citations.

Every pricing, location, or feature claim must include at least one matching property-id citation in brackets.
Return two short paragraphs titled 'Matches' and 'Insight'. Keep the answer concise and factual.
```

## Design Decisions

- The safety-oriented system prompt sets a non-negotiable rule that every conclusion must stay grounded in retrieved evidence.
- The citation instruction is explicit about inline property-id brackets so reviewers can validate claims quickly.
- The short labeled output format reduces drift into long unsupported prose and makes citation checking easier.

## Final Test Results

- Date run: 2026-04-21
- Number of test cases: 10
- Final pass rate: 100.0% (10/10)
- Minimum requirement met: Yes
- Failing test cases: None

## Lessons Learned

- Direct citation rules work better than vague requests to mention sources.
- Short output structures reduce the chance that citations disappear in long narrative text.
