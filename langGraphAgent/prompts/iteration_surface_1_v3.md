# Surface 1 - Iteration 3

## Tool Description

Use rag_search for listing facts, comparisons, and price. Use image_analysis for visible room condition or damage. Use both when renovation or value improvement needs facts plus visual evidence.

## Test Results

- Pass Rate: 6/10 (60.0%)
- Passing Tests: S1_T1, S1_T2, S1_T3, S1_T4, S1_T5, S1_T6
- Failing Tests: S1_T7, S1_T8, S1_T9, S1_T10

## Failure Analysis

- Primary failure mode: Planner used both tools more often but still needed a stronger anti-guessing rule.
- Secondary patterns: tool selection drift, insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S1_T7: market context
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T8: no guessing
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T9: market context
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T10: no guessing
  Missing keywords: reasoning_length
  Missing tools: image_analysis

## Next Iteration Plan

Tighten tool-routing rules so the planner distinguishes listing facts, visual evidence, and multi-tool questions more reliably.
