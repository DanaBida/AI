# Surface 1 - Iteration 4

## Tool Description

Use rag_search for listing facts, comparisons, price, and market context. Use image_analysis for visible rooms, visible damage, and condition. Use both when the answer needs both factual context and visible evidence. Do not guess.

## Test Results

- Pass Rate: 10/10 (100.0%)
- Passing Tests: S1_T1, S1_T2, S1_T3, S1_T4, S1_T5, S1_T6, S1_T7, S1_T8, S1_T9, S1_T10
- Failing Tests: None

## Failure Analysis

- Primary failure mode: Planner was close, but edge cases around visible-only structural claims still needed tightening.
- Secondary patterns: None

## Failure Details

- All tests passed.

## Next Iteration Plan

Tighten tool-routing rules so the planner distinguishes listing facts, visual evidence, and multi-tool questions more reliably.
