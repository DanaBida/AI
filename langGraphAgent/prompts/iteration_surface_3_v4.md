# Surface 3 - Iteration 4

## Tool Description

Interpret visible condition scores with confidence, distinguish cosmetic wear from serious issues, and never infer hidden defects or unsupported costs.

## Test Results

- Pass Rate: 3/10 (30.0%)
- Passing Tests: S3_T4, S3_T6, S3_T7
- Failing Tests: S3_T1, S3_T2, S3_T3, S3_T5, S3_T8, S3_T9, S3_T10

## Failure Analysis

- Primary failure mode: Interpretation was strong, with only minor uncertainty-labeling gaps.
- Secondary patterns: insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S3_T1: visible evidence, plain language
  Missing keywords: score, reasoning_length
  Missing tools: None
- S3_T2: visible evidence
  Missing keywords: reasoning_length
  Missing tools: None
- S3_T3: cosmetic vs structural
  Missing keywords: repair, reasoning_length
  Missing tools: None
- S3_T5: visible evidence
  Missing keywords: reasoning_length
  Missing tools: None
- S3_T8: visible evidence, cosmetic vs structural
  Missing keywords: reasoning_length
  Missing tools: None
- S3_T9: visible evidence
  Missing keywords: not visible, reasoning_length
  Missing tools: None
- S3_T10: visible evidence, plain language
  Missing keywords: visible, reasoning_length
  Missing tools: None

## Next Iteration Plan

Add stricter grounding language so image interpretation stays tied to visible evidence and confidence.
