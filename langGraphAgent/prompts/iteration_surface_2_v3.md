# Surface 2 - Iteration 3

## Tool Description

Turn the request into a concise retrieval query that preserves property type, room, city, price, and comparison intent without adding new facts.

## Test Results

- Pass Rate: 0/10 (0.0%)
- Passing Tests: None
- Failing Tests: S2_T1, S2_T2, S2_T3, S2_T4, S2_T5, S2_T6, S2_T7, S2_T8, S2_T9, S2_T10

## Failure Analysis

- Primary failure mode: Search queries became more faithful, but outcome-oriented requests still lost user intent.
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
- S2_T6: requested outcome
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T7: preserve constraints
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T8: avoid invention
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T9: market context
  Missing keywords: reasoning_length
  Missing tools: None
- S2_T10: requested outcome
  Missing keywords: reasoning_length
  Missing tools: None

## Next Iteration Plan

Preserve one more missing user constraint and remove any wording that encourages invented search terms.
