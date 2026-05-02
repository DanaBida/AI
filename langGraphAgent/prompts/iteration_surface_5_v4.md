# Surface 5 - Iteration 4

## Tool Description

Handle missing or conflicting data by naming the unavailable tool, preferring direct evidence, preserving user intent, and suggesting a next step.

## Test Results

- Pass Rate: 3/10 (30.0%)
- Passing Tests: S5_T3, S5_T6, S5_T8
- Failing Tests: S5_T1, S5_T2, S5_T4, S5_T5, S5_T7, S5_T9, S5_T10

## Failure Analysis

- Primary failure mode: Recovery behavior was solid, with only minor ambiguity around evidence prioritization.
- Secondary patterns: insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S5_T1: label limitation
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T2: continue with partial data
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T4: continue with partial data
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T5: label limitation
  Missing keywords: reasoning_length
  Missing tools: None
- S5_T7: continue with partial data
  Missing keywords: partial, reasoning_length
  Missing tools: None
- S5_T9: label limitation
  Missing keywords: limited, reasoning_length
  Missing tools: None
- S5_T10: suggest next action
  Missing keywords: reasoning_length
  Missing tools: None

## Next Iteration Plan

Improve graceful degradation so the answer remains useful under partial or conflicting evidence.
