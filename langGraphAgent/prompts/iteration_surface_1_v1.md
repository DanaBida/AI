# Surface 1 - Iteration 1

## Tool Description

Use rag_search for facts and image_analysis for photos.

## Test Results

- Pass Rate: 0/10 (0.0%)
- Passing Tests: None
- Failing Tests: S1_T1, S1_T2, S1_T3, S1_T4, S1_T5, S1_T6, S1_T7, S1_T8, S1_T9, S1_T10

## Failure Analysis

- Primary failure mode: Planner prompt was too vague, so it missed when both tools were required.
- Secondary patterns: tool selection drift, insufficient reasoning detail, keyword coverage gaps

## Failure Details

- S1_T1: visual condition
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T2: listing facts
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T3: use both, visual condition
  Missing keywords: reasoning_length
  Missing tools: image_analysis
- S1_T4: listing facts
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T5: visual condition
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T6: use both, listing facts
  Missing keywords: reasoning_length
  Missing tools: image_analysis
- S1_T7: market context
  Missing keywords: reasoning_length
  Missing tools: None
- S1_T8: visual condition, no guessing
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
