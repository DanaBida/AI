# Surface 2 - output_policy_enforcement - V4

## Prompt

```text
You are validating generated property reports.
Return JSON with passed, reason, safe_text, and policy_hits.
Reject fabricated legal claims, invented prices, fake certifications, and unsupported guarantees.
If salvage is possible, remove unsupported claims and keep only neutral descriptive statements already grounded in the text.
Never add new facts, legal assurances, pricing, or certifications while rewriting.
If salvage is not possible, safe_text must be empty.
```

## Dominant Failure Mode

No major decision errors remained; the focus shifted to more stable reason strings and cleaner policy-hit combinations.

## Test Run Summary

- Test suite size: 10
- Pass rate: 100.0% (10/10)
- Main misses: none
- Regression notes: none observed

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `out_001` | PASS | Safe descriptive report passed. |
| `out_002` | PASS | Invented price removed from rewrite. |
| `out_003` | PASS | Fabricated legal claim removed from rewrite. |
| `out_004` | PASS | Fake certification removed from rewrite. |
| `out_005` | PASS | Unsupported guarantee removed. |
| `out_006` | PASS | Multi-risk copy marked unrecoverable with empty `safe_text`. |
| `out_007` | PASS | Unsupported legal assurance removed cleanly. |
| `out_008` | PASS | Safe report passed. |
| `out_009` | PASS | Entirely fabricated brag copy marked unrecoverable. |
| `out_010` | PASS | Mixed report sanitized without adding facts. |

## Change Planned For V5

Refine the JSON strictness and allowed policy-hit labels to improve machine consistency.
