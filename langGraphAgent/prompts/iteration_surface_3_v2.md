# Surface 3 - Iteration 2

## Tool Description

Interpret visible condition from images and explain the score simply.

## Test Results

- Pass Rate: 0/10 (0.0%)
- Passing Tests: None
- Failing Tests: S3_T1, S3_T2, S3_T3, S3_T4, S3_T5, S3_T6, S3_T7, S3_T8, S3_T9, S3_T10

## Failure Analysis

- Primary failure mode: Plain-language explanations improved, but hidden-defect claims were still too loose.
- Secondary patterns: insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S3_T1: visible evidence, plain language
  Missing keywords: score, reasoning_length
  Missing tools: None
- S3_T2: visible evidence, no hidden defects
  Missing keywords: reasoning_length
  Missing tools: None
- S3_T3: cosmetic vs structural
  Missing keywords: repair, reasoning_length
  Missing tools: None
- S3_T4: no hidden defects
  Missing keywords: listing, reasoning_length
  Missing tools: None
- S3_T5: visible evidence
  Missing keywords: reasoning_length
  Missing tools: None
- S3_T6: no hidden defects
  Missing keywords: reasoning_length
  Missing tools: None
- S3_T7: confidence
  Missing keywords: uncertain, reasoning_length
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
