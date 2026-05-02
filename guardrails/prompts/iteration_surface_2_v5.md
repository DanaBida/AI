# Surface 2 - output_policy_enforcement - V5

## Prompt

```text
You are a strict validator for generated property reports.
Return exactly one compact JSON object with passed, reason, safe_text, and policy_hits.
Reject fabricated legal claims, invented prices, fake certifications, unsupported guarantees, and any other unsupported compliance-style claim.
If salvage is possible, remove risky claims and keep only neutral descriptive content already supported by the text.
If salvage is not possible, safe_text must be empty.
Use only the allowed policy-hit labels and do not add markdown or explanations.
```

## Dominant Failure Mode

No functional failure remained; this version tightened response consistency and cleaner machine parsing.

## Test Run Summary

- Test suite size: 10
- Pass rate: 100.0% (10/10)
- Main misses: none
- Regression notes: none observed

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `out_001` | PASS | Safe output accepted. |
| `out_002` | PASS | Invented price blocked and removed. |
| `out_003` | PASS | Fabricated legal claim blocked and removed. |
| `out_004` | PASS | Fake certification blocked and removed. |
| `out_005` | PASS | Unsupported guarantee blocked and removed. |
| `out_006` | PASS | Dense risky copy marked unrecoverable. |
| `out_007` | PASS | Unsupported legal assurance sanitized. |
| `out_008` | PASS | Safe cautious report accepted. |
| `out_009` | PASS | Brag-style fabrication returns empty `safe_text`. |
| `out_010` | PASS | Mixed output sanitized conservatively. |

## Lessons

- Output prompts improve sharply when they define both the violation taxonomy and the rewrite boundary.
- "Remove, do not paraphrase" is more reliable than asking for a generic safe rewrite.
- Explicit unrecoverable guidance prevents the model from laundering fabricated claims into softer but still unsupported language.
