# Surface 1 - Iteration 2

## Tool Description

Use rag_search for listing facts and image_analysis for visible room condition.

## Test Results

- Pass Rate: 4/10 (40.0%)
- Passing Tests: S1_T1, S1_T2, S1_T4, S1_T5
- Failing Tests: S1_T3, S1_T6, S1_T7, S1_T8, S1_T9, S1_T10

## Failure Analysis

- Primary failure mode: Planner improved routing but still under-specified market-context queries.
- Secondary patterns: tool selection drift, insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S1_T3: use both
  Missing keywords: reasoning_length
  Missing tools: image_analysis
- S1_T6: use both
  Missing keywords: reasoning_length
  Missing tools: image_analysis
- S1_T7: market context
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T8: no guessing
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T9: market context
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T10: use both, no guessing
  Missing keywords: reasoning_length
  Missing tools: image_analysis

## Next Iteration Plan

Tighten tool-routing rules so the planner distinguishes listing facts, visual evidence, and multi-tool questions more reliably.
