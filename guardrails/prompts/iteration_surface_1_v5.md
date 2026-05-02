# Surface 1 - input_topic_detection - V5

## Prompt

```text
You are a strict validator for incoming property-listing text.
Return exactly one compact JSON object with passed, reason, safe_text, and policy_hits.
Pass only when the text is a genuine English property listing or rental listing with concrete listing details.
Reject spam, scams, marketing blasts, seminar promotions, clickbait, non-English text, off-topic text, and any offensive or abusive content.
If any rejection rule applies, passed must be false and safe_text must be an empty string.
Use only the allowed policy-hit labels.
```

## Dominant Failure Mode

No major functional failure remained; this iteration focused on response consistency and concise failure reasons.

## Test Run Summary

- Test suite size: 10
- Pass rate: 100.0% (10/10)
- Main misses: none
- Regression notes: none observed

## Output Notes

| Test ID | Result | Output Summary |
| --- | --- | --- |
| `in_001` | PASS | Accepted valid listing. |
| `in_002` | PASS | Rejected spam cleanly. |
| `in_003` | PASS | Rejected abuse cleanly. |
| `in_004` | PASS | Rejected non-listing real-estate commentary. |
| `in_005` | PASS | Rejected Hebrew. |
| `in_006` | PASS | Rejected French. |
| `in_007` | PASS | Rejected vague non-listing message. |
| `in_008` | PASS | Rejected investment seminar spam. |
| `in_009` | PASS | Accepted rental listing. |
| `in_010` | PASS | Rejected abusive mixed-content input. |

## Lessons

- Listing acceptance becomes more stable when the prompt names concrete listing attributes explicitly.
- Abuse and spam need override language; otherwise the model overweights listing-like details.
- JSON-only output and enumerated policy tags reduce repair work downstream.
