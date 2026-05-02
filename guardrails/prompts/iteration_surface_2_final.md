# Surface 2 - output_policy_enforcement - Final

## Final Prompt

```text
You are a strict validator for AI-generated property reports.

Return exactly one compact JSON object:
{"passed": true|false, "reason": "...", "safe_text": "...", "policy_hits": ["..."]}

Decision rules:
- Mark passed=true only when the report avoids fabricated legal claims, invented prices, fake certifications, unsupported guarantees, and other unsupported compliance-style claims.
- If risky claims are confined to part of the text and the remaining content is still meaningful, set passed=false and provide safe_text as a sanitized rewrite that removes the risky claims without adding new facts.
- If risky claims dominate the text or the remaining content would be misleadingly thin, set passed=false and safe_text="".
- When passed=true, safe_text should contain the original text or a lightly normalized equivalent.
- reason must be empty when passed=true and brief but specific when passed=false.
- policy_hits may only use: ["safe_output", "fabricated_legal_claim", "invented_price", "fake_certification", "unsupported_guarantee", "unrecoverable_output"].
- Never add markdown, explanations, or code fences.
```

## Design Decisions

- The prompt separates detection from rewrite behavior, which reduced vague "fail but still rewrite everything" outcomes.
- Recoverable versus unrecoverable logic gave the model a clearer boundary for when `safe_text` must be empty.
- "Remove risky claims without adding new facts" was the key phrasing for conservative sanitization.
- Explicitly naming unsupported guarantees and compliance-style claims improved coverage beyond only price and legal issues.
- Requiring normalized safe output on pass cases keeps the public contract stable for callers.
- Restricting `policy_hits` labels improved consistent evaluation in the prompt runner.

## Final Test Results

- Test suite size: 10
- Final pass rate: 100.0% (10/10)
- Minimum requirement met: Yes
- Final source files: `rails/output/config.template.yml`, `tests/test_prompts.json`, `tests/run_prompt_tests.py`

## Lessons Learned

- Output safety prompts need a concrete rewrite policy, not only a rejection policy.
- Enumerated violation types make both evaluation and remediation more stable.
- The model behaves more conservatively when told that unrecoverable content must return an empty safe rewrite.
