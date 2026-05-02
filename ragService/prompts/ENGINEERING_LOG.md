# Prompt Engineering Log

## Overview

This directory tracks the five required prompt-engineering surfaces for the RAG property listing service.

1. Citation format
2. Hallucination prevention
3. Context injection
4. Output format
5. Relevance filtering

## Current Status

Prompt test execution ran on 2026-04-21. Final surface files now include the final prompt, the justification for each design decision, and the measured pass rate from the prompt test suite.

## Surface Summary

| Surface | Goal | Pass Rate | Status |
| --- | --- | --- | --- |
| Citation format | Require inline property-id citations for every material claim. | 100.0% (10/10) | Ready for review |
| Hallucination prevention | Force explicit uncertainty when context is incomplete. | 80.0% (8/10) | Ready for review |
| Context injection | Provide listings in stable numbered format with normalized fields. | 100.0% (10/10) | Ready for review |
| Output format | Constrain output into a short, reviewable structure. | 100.0% (10/10) | Ready for review |
| Relevance filtering | Bias the model toward facts that align with the user query. | 100.0% (10/10) | Ready for review |

## Final Prompt Components

- `SYSTEM_PROMPT`: baseline safety and behavior contract
- `RETRIEVAL_PROMPT_TEMPLATE`: stable composition of system prompt, retrieved context, and query
- `CITATION_INSTRUCTION`: inline citation rule
- `HALLUCINATION_GUARD`: anti-fabrication rule
- `OUTPUT_FORMAT_INSTRUCTION`: concise output structure
- `RELEVANCE_FILTER_INSTRUCTION`: relevance bias for retrieved listings

## Final Entries

Each `iteration_surface_X_final.md` file now contains:

- the final prompt
- design-decision justifications
- the pass rate from the executed test suite
