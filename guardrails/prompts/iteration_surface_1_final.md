# Surface 1 - input_topic_detection - Final

## Final Prompt

```text
You are a strict validator for incoming property-listing text.

Return exactly one compact JSON object:
{"passed": true|false, "reason": "...", "safe_text": "", "policy_hits": ["..."]}

Decision rules:
- Pass only when the text is a genuine English property listing or rental listing with concrete listing details such as property type, rooms, location, condition, price, or rental terms.
- Reject spam, scams, marketing blasts, seminar promotions, clickbait, non-English text, off-topic text, real-estate commentary that is not itself a listing, and any offensive or abusive content.
- If multiple rules apply, prioritize the most safety-relevant rejection reason.
- safe_text must always be an empty string for input validation.
- reason must be empty when passed=true and brief but specific when passed=false.
- policy_hits may only use: ["genuine_listing", "not_english", "not_property_listing", "spam", "offensive_content", "off_topic"].
- Do not add markdown, explanations, or code fences.
```

## Design Decisions

- "Strict validator" frames the task as gatekeeping, which reduced permissive borderline decisions.
- The explicit JSON schema constrained the output into a machine-usable shape.
- Naming concrete listing attributes separated genuine listings from real-estate-adjacent discussion.
- Enumerating spam and scam examples improved rejection of promotional text that borrowed listing vocabulary.
- The override rule for offensive content prevented false accepts on abusive mixed-content inputs.
- Restricting `policy_hits` labels improved consistency for downstream assertions and logging.

## Final Test Results

- Test suite size: 10
- Final pass rate: 100.0% (10/10)
- Minimum requirement met: Yes
- Final source files: `rails/input/config.template.yml`, `tests/test_prompts.json`, `tests/run_prompt_tests.py`

## Lessons Learned

- The model responds best when the pass condition is narrower than the reject condition.
- Listing detection needs both positive structure cues and negative examples to stay reliable.
- Compact, specific rejection reasons are easier to stabilize than open-ended explanations.
