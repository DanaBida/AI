# Surface 1 - input_topic_detection - V1

## Prompt

```text
You are validating incoming text for a property workflow.
Return JSON with passed, reason, safe_text, and policy_hits.
Pass only if the text looks like a real property listing in English.
Reject spam, abuse, unrelated text, and non-English text.
```

## Dominant Failure Mode

The baseline prompt treated real-estate-adjacent commentary and marketing text as valid listings too often.

## Test Run Summary

- Test suite size: 10
- Pass rate: 70.0% (7/10)
- Main misses: `in_004`, `in_007`, `in_008`
- Regression notes: none, this was the baseline run

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `in_001` | PASS | Accepted a concrete apartment listing. |
| `in_002` | PASS | Rejected newsletter-style marketing as spam. |
| `in_003` | PASS | Rejected abusive content. |
| `in_004` | FAIL | Treated a mortgage-advice paragraph as listing-related and passed it. |
| `in_005` | PASS | Rejected Hebrew text as non-English. |
| `in_006` | PASS | Rejected French text as non-English. |
| `in_007` | FAIL | Passed a vague buyer-intent note that was not a listing. |
| `in_008` | FAIL | Under-classified investment seminar copy as merely real-estate-related. |
| `in_009` | PASS | Accepted a rental listing with concrete property details. |
| `in_010` | PASS | Rejected a listing-like input containing abusive language. |

## Change Planned For V2

Add a stricter definition of "genuine listing" that requires concrete property attributes or listing-style structure, not just real-estate topic overlap.
