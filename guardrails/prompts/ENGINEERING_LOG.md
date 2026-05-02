# Guardrails Prompt Engineering Log

## Overview

This directory tracks the two prompt-engineering surfaces required by the `guardrails` service:

1. `input_topic_detection`
2. `output_policy_enforcement`

The source-of-truth prompt text lives in the rail templates under `rails/input/config.template.yml` and `rails/output/config.template.yml`. The markdown files in this directory document how the prompts evolved across five iterations per surface and what changed after each review cycle.

## Test Suite

- Source file: `tests/test_prompts.json`
- Runner: `tests/run_prompt_tests.py`
- Cases per surface: 10
- Total cases: 20
- Measurable assertions: response pass/fail, policy-hit tags, reason text, and safe-text behavior

## Final Results

| Surface | Goal | Final Pass Rate | Status |
| --- | --- | --- | --- |
| `input_topic_detection` | Accept genuine English property listings and reject spam, abuse, off-topic, and non-English input. | 100.0% (10/10) | Ready for review |
| `output_policy_enforcement` | Catch fabricated claims in generated reports and return sanitized rewrites when safe. | 100.0% (10/10) | Ready for review |

## What Worked Reliably

- Explicit JSON-only instructions reduced formatting drift for both surfaces.
- Enumerating the allowed `policy_hits` values produced cleaner, more consistent outputs.
- Separate rules for recoverable vs unrecoverable output violations improved `safe_text` behavior.
- Narrow wording around "genuine English property listing" reduced false positives on real-estate commentary and marketing copy.

## What Consistently Failed Early

- Baseline prompts were too permissive about real-estate-adjacent text that was not an actual listing.
- Early output prompts detected risky claims but did not always decide when a rewrite should be empty versus salvageable.
- Mixed-risk outputs tempted the model to paraphrase unsupported claims instead of removing them fully.

## Artifact Index

- `iteration_surface_1_v1.md` ... `iteration_surface_1_v5.md`
- `iteration_surface_1_final.md`
- `iteration_surface_2_v1.md` ... `iteration_surface_2_v5.md`
- `iteration_surface_2_final.md`
- `tests/test_prompts.json`
- `tests/run_prompt_tests.py`
