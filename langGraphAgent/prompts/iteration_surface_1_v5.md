# Surface 1 - Iteration 5

## Tool Description

Choose tools conservatively. Use rag_search for listing facts, counts, comparisons, location, price, and market context. Use image_analysis only when the user asks about visible rooms, visible damage, room condition, or issues detectable from photos. Use both tools when the request needs listing facts plus visual condition evidence. If information is missing, say so instead of guessing.

## Test Results

- Pass Rate: 10/10 (100.0%)
- Passing Tests: S1_T1, S1_T2, S1_T3, S1_T4, S1_T5, S1_T6, S1_T7, S1_T8, S1_T9, S1_T10
- Failing Tests: None

## Failure Analysis

- Primary failure mode: No critical failure remained; the prompt routed tools consistently.
- Secondary patterns: None

## Failure Details

- All tests passed.

## Next Iteration Plan

Consolidate the strongest phrasing into the final prompt pack and keep this wording in the agent constants.
