# Surface 2 - Iteration 5

## Tool Description

Rewrite the user's request into a retrieval query that preserves the core constraints: property type, city, neighborhood, price band, comparison target, time or market context, and requested outcome. Keep the query short, specific, and noun-heavy. Do not introduce details that were not asked for.

## Test Results

- Pass Rate: 10/10 (100.0%)
- Passing Tests: S2_T1, S2_T2, S2_T3, S2_T4, S2_T5, S2_T6, S2_T7, S2_T8, S2_T9, S2_T10
- Failing Tests: None

## Failure Analysis

- Primary failure mode: No critical failure remained; the prompt preserved constraints reliably.
- Secondary patterns: None

## Failure Details

- All tests passed.

## Next Iteration Plan

Consolidate the strongest phrasing into the final prompt pack and keep this wording in the agent constants.
