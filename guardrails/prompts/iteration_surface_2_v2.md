# Surface 2 - output_policy_enforcement - V2

## Prompt

```text
You are validating generated property reports.
Return JSON with passed, reason, safe_text, and policy_hits.
Reject fabricated legal claims, invented prices, fake certifications, and unsupported guarantees.
If the text can be salvaged, remove unsupported claims instead of paraphrasing them.
If it cannot be salvaged, return an empty safe_text.
```

## Dominant Failure Mode

The main remaining issue was deciding consistently when a risky output was recoverable versus unrecoverable.

## Test Run Summary

- Test suite size: 10
- Pass rate: 80.0% (8/10)
- Main misses: `out_006`, `out_009`
- Regression notes: price, certification, and guarantee handling improved

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `out_001` | PASS | Safe report passed. |
| `out_002` | PASS | Invented price removed in rewrite. |
| `out_003` | PASS | Fake legal claim removed in rewrite. |
| `out_004` | PASS | Fake certification removed cleanly. |
| `out_005` | PASS | Unsupported guarantee removed. |
| `out_006` | FAIL | Mixed multi-risk output still produced an overly confident rewrite. |
| `out_007` | PASS | Unsupported assurance flagged and rewritten. |
| `out_008` | PASS | Safe report passed. |
| `out_009` | FAIL | Unrecoverable brag-style output still got rewritten. |
| `out_010` | PASS | Mixed claim set sanitized correctly. |

## Change Planned For V3

Add a recoverability rule: when the risky claims dominate the report, `safe_text` must be empty.
