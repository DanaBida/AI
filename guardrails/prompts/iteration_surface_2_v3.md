# Surface 2 - output_policy_enforcement - V3

## Prompt

```text
You are validating generated property reports.
Return JSON with passed, reason, safe_text, and policy_hits.
Reject fabricated legal claims, invented prices, fake certifications, and unsupported guarantees.
If risky claims are only part of the text, remove them and keep only supported descriptive content.
If risky claims dominate the text or the remaining content would be misleadingly thin, return safe_text as an empty string.
```

## Dominant Failure Mode

The prompt still occasionally added fresh wording during rewrites instead of preserving only the supported content.

## Test Run Summary

- Test suite size: 10
- Pass rate: 90.0% (9/10)
- Main miss: `out_010`
- Regression notes: unrecoverable outputs are now handled correctly

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `out_001` | PASS | Safe report passed. |
| `out_002` | PASS | Price claim removed. |
| `out_003` | PASS | Legal claim removed. |
| `out_004` | PASS | Certification claim removed. |
| `out_005` | PASS | Guarantee claim removed. |
| `out_006` | PASS | Multi-risk output now returns empty safe_text. |
| `out_007` | PASS | Unsupported legal assurance sanitized. |
| `out_008` | PASS | Safe report passed. |
| `out_009` | PASS | Unrecoverable brag copy returns empty safe_text. |
| `out_010` | FAIL | Rewrite added slightly stronger wording than the safe source text warranted. |

## Change Planned For V4

Add an explicit no-new-facts rewrite rule and require neutral descriptive language only.
