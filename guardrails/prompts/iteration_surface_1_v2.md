# Surface 1 - input_topic_detection - V2

## Prompt

```text
You are validating incoming text for a property workflow.
Return JSON with passed, reason, safe_text, and policy_hits.
Pass only if the text is a genuine English property listing with concrete listing details such as property type, rooms, location, condition, price, or rental terms.
Reject spam, abuse, unrelated text, non-English text, and real-estate discussion that is not itself a listing.
```

## Dominant Failure Mode

The biggest remaining issue was that borderline listing-like spam still slipped through when it contained location or pricing language.

## Test Run Summary

- Test suite size: 10
- Pass rate: 80.0% (8/10)
- Main misses: `in_002`, `in_008`
- Regression notes: `in_004` and `in_007` were fixed without harming genuine-listing recall

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `in_001` | PASS | Accepted a structured sale listing. |
| `in_002` | FAIL | Promotional newsletter wording still looked listing-like. |
| `in_003` | PASS | Rejected offensive text. |
| `in_004` | PASS | Rejected mortgage commentary as not a listing. |
| `in_005` | PASS | Rejected Hebrew text. |
| `in_006` | PASS | Rejected French text. |
| `in_007` | PASS | Rejected vague buyer-intent message. |
| `in_008` | FAIL | "Guaranteed returns" seminar copy still triggered false acceptance. |
| `in_009` | PASS | Accepted a valid rental listing. |
| `in_010` | PASS | Rejected abuse mixed into listing text. |

## Change Planned For V3

Add explicit spam and scam examples, especially for investment promises, clickbait, seminars, and broadcast-style marketing.
