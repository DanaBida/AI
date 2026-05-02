# Surface 1 - input_topic_detection - V3

## Prompt

```text
You are validating incoming text for a property workflow.
Return JSON with passed, reason, safe_text, and policy_hits.
Pass only if the text is a genuine English property listing with concrete listing details.
Reject spam, scams, marketing blasts, seminar promotions, clickbait, abuse, unrelated text, non-English text, and real-estate discussion that is not itself a listing.
```

## Dominant Failure Mode

The prompt still struggled on mixed cases where a mostly valid listing also included offensive wording.

## Test Run Summary

- Test suite size: 10
- Pass rate: 90.0% (9/10)
- Main miss: `in_010`
- Regression notes: spam-heavy cases now fail reliably

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `in_001` | PASS | Genuine listing passed. |
| `in_002` | PASS | Newsletter spam rejected. |
| `in_003` | PASS | Offensive content rejected. |
| `in_004` | PASS | Off-topic mortgage advice rejected. |
| `in_005` | PASS | Hebrew rejected as non-English. |
| `in_006` | PASS | French rejected as non-English. |
| `in_007` | PASS | Buyer-intent note rejected. |
| `in_008` | PASS | Seminar spam rejected. |
| `in_009` | PASS | Rental listing passed. |
| `in_010` | FAIL | Model focused on listing details and underweighted the abusive phrase. |

## Change Planned For V4

State clearly that offensive or abusive wording always overrides otherwise valid listing characteristics.
