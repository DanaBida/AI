# Surface 5 - Iteration 1

## Tool Description

Handle errors and missing data.

## Test Results

- Pass Rate: 0/10 (0.0%)
- Passing Tests: None
- Failing Tests: S5_T1, S5_T2, S5_T3, S5_T4, S5_T5, S5_T6, S5_T7, S5_T8, S5_T9, S5_T10

## Failure Analysis

- Primary failure mode: Error handling prompt acknowledged failures but did not preserve user intent under partial data.
- Secondary patterns: insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S5_T1: label limitation
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T2: continue with partial data
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T3: report conflict
  Missing keywords: repair, reasoning_length
  Missing tools: None
- S5_T4: continue with partial data
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T5: label limitation
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T6: prefer direct evidence
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T7: continue with partial data
  Missing keywords: partial, reasoning_length
  Missing tools: None
- S5_T8: prefer direct evidence
  Missing keywords: cannot confirm, reasoning_length
  Missing tools: None
- S5_T9: label limitation
  Missing keywords: limited, reasoning_length
  Missing tools: None
- S5_T10: suggest next action
  Missing keywords: reasoning_length
  Missing tools: None

## Next Iteration Plan

Improve graceful degradation so the answer remains useful under partial or conflicting evidence.
