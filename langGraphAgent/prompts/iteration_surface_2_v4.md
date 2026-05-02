# Surface 2 - Iteration 4

## Tool Description

Rewrite as a short retrieval query preserving room, city, price, comparison target, market context, and requested outcome. Avoid unsupported details.

## Test Results

- Pass Rate: 3/10 (30.0%)
- Passing Tests: S2_T6, S2_T9, S2_T10
- Failing Tests: S2_T1, S2_T2, S2_T3, S2_T4, S2_T5, S2_T7, S2_T8

## Failure Analysis

- Primary failure mode: Only minor drift remained around market-context phrasing.
- Secondary patterns: insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S2_T1: short and specific
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T2: preserve constraints
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T3: preserve constraints
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T4: preserve constraints
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T5: avoid invention
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T7: preserve constraints
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T8: avoid invention
  Missing keywords: reasoning_length
  Missing tools: None

## Next Iteration Plan

Preserve one more missing user constraint and remove any wording that encourages invented search terms.
