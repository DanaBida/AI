# Surface 1 - input_topic_detection - V4

## Prompt

```text
You are validating incoming text for a property workflow.
Return JSON with passed, reason, safe_text, and policy_hits.
Pass only if the text is a genuine English property listing with concrete listing details.
Reject spam, scams, marketing blasts, seminar promotions, clickbait, unrelated text, non-English text, and any offensive or abusive content.
If a message contains both listing details and offensive language, it must fail.
```

## Dominant Failure Mode

The remaining issue was occasional inconsistency in the policy-hit tag selection for vague non-listing English text.

## Test Run Summary

- Test suite size: 10
- Pass rate: 100.0% (10/10)
- Main misses: none
- Regression notes: none observed

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `in_001` | PASS | Listing accepted with `genuine_listing`. |
| `in_002` | PASS | Spam rejected with `spam`. |
| `in_003` | PASS | Offensive input rejected with `offensive_content`. |
| `in_004` | PASS | Real-estate commentary rejected with `not_property_listing`. |
| `in_005` | PASS | Hebrew rejected with `not_english`. |
| `in_006` | PASS | French rejected with `not_english`. |
| `in_007` | PASS | Vague note rejected with `not_property_listing`. |
| `in_008` | PASS | Seminar spam rejected with `spam`. |
| `in_009` | PASS | Rental listing accepted. |
| `in_010` | PASS | Mixed listing plus abuse rejected with `offensive_content`. |

## Change Planned For V5

Refine wording for more stable, concise reasons and policy-hit choices, without changing the decision boundary.
