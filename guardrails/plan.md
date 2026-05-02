# Guardrails Service Plan

## Summary

Build `aiPropertyTriangeProject/guardrails` as a FastAPI service with two NeMo Guardrails-backed endpoints:

- `POST /check/input` validates incoming listing text and accepts only genuine English property listings.
- `POST /check/output` validates AI-generated property reports for fabricated legal claims, invented prices, and fake certifications, and returns a sanitized rewrite when recovery is safe.

The service should follow: clean architecture folders, centralized `config.py`, Docker + Compose for EC2 readiness, pinned `requirements.txt`, comprehensive `README.md`, and prompt-engineering artifacts tracked in-repo.

## Public Interfaces

Request model for both endpoints:

```json
{ "text": "<text to check>" }
```

Response model for both endpoints:

```json
{ "pass": true/false, "reason": "<if fail>", "safe_text": "<if output>" }
```

Behavior contract:

- `/check/input`
  - `pass=true`: text looks like a genuine English property listing in scope.
  - `pass=false`: reject spam, offensive content, off-topic submissions, or wrong-language submissions; `reason` explains the failure; `safe_text` stays empty.
- `/check/output`
  - `pass=true`: report is safe to return; `safe_text` can mirror the original or normalized output text.
  - `pass=false`: `reason` explains the violated policy; `safe_text` contains a sanitized rewrite when the issue is recoverable, otherwise empty.

## Phase 1: Project Skeleton And Core Contracts

Goal: create the service structure and lock the API/data contracts.

- Create the service skeleton in `aiPropertyTriangeProject/guardrails` using the existing house style:
  - `models/`, `controllers/`, `services/`, `middlewares/`, `utils/`, `lib/`, `tests/`, `prompts/`, `rails/`
  - `app.py`, `config.py`, `requirements.txt`, `.env.example`, `Dockerfile`, `docker-compose.yml`, `README.md`, `plan.md`
- Add Pydantic types for check request/response plus a small internal result type that separates `passed`, `reason`, `safe_text`, and `policy_hits`.
- Implement thin controllers for `POST /check/input`, `POST /check/output`, and `GET /health`.
- Centralize all env handling in `config.py`, including app host/port, log level, NeMo model/provider settings, prompt artifact paths, and optional strictness toggles for input/output checks.

Review checklist:

- Folder structure matches project standards.
- Request/response schema is stable and documented.
- `config.py` is the only place reading environment variables.

## Phase 2: Guardrails Runtime And Policy Flows

Goal: wire NeMo Guardrails into the service with clear separation of concerns.

- Add a single-purpose wrapper in `lib/` for NeMo Guardrails runtime setup so Colang/YAML loading, LLM configuration, and rail execution stay out of controllers/services.
- Add a static `GuardrailsService` that routes requests to the correct NeMo rail set and maps raw rail outcomes into the public JSON contract.
- Create separate rail configs for:
  - Input validation: genuine English property listing detection, spam rejection, offensive-content rejection, off-topic rejection.
  - Output validation: unsupported legal-claim detection, invented price detection, fabricated certification detection, sanitized rewrite path.
- Keep topic detection and policy enforcement as explicit prompts inside the rail configuration, not buried in Python code.

Review checklist:

- Controllers remain thin.
- Python code does not embed the actual policy prompts.
- Input and output rail paths are independently testable.

## Phase 3: Prompt Engineering Assets

Goal: make the prompt work measurable, repeatable, and reviewable.

Treat the two prompt surfaces as:

1. `input_topic_detection`
2. `output_policy_enforcement`

For each surface:

- Create at least 10 test cases with:
  - `test_id`
  - input text
  - retrieved/policy context used by the prompt runner
  - measurable expected behaviors
  - assertion keywords or patterns
- Run 5 prompt iterations minimum:
  - `v1`: baseline prompt
  - `v2` and `v3`: each targets one dominant failure mode
  - `v4` and `v5`: refinement based on remaining misses/regressions
- Record pass rate, failure mode, changes made, and regression notes for every run.
- Target at least `80%` pass rate per surface by the final version.
- Store working artifacts in markdown first under `prompts/`, following the repo pattern already used by `ragService`; include a final packaging step to export iteration logs to PDF or DOCX if required for submission.

Recommended prompt-artifact set:

- `prompts/ENGINEERING_LOG.md`
- `prompts/iteration_surface_1_v1.md` ... `v5.md`
- `prompts/iteration_surface_1_final.md`
- `prompts/iteration_surface_2_v1.md` ... `v5.md`
- `prompts/iteration_surface_2_final.md`
- `tests/test_prompts.json`
- `tests/run_prompt_tests.py`

Review checklist:

- Each surface has 10 or more test cases.
- Each iteration documents one main failure mode and what changed.
- Final pass rate per surface is at least `80%`.

## Phase 4: Testing And Quality Validation

Goal: verify service behavior and prompt behavior before deployment.

- Unit tests for request/response models and config parsing.
- Controller tests for `/check/input`, `/check/output`, and `/health`.
- Service tests for:
  - valid English listing passes
  - non-listing English text fails
  - spam/marketing text fails
  - offensive text fails
  - wrong-language input fails
  - safe report passes
  - fabricated price fails
  - fake legal claim fails
  - fake certification fails
  - sanitized rewrite is returned only when appropriate
- Prompt-test runner coverage with at least 10 cases per surface and pass-rate reporting.
- Smoke checks for Docker startup and health endpoint.

Review checklist:

- API behavior is covered at model, service, and controller level.
- Prompt tests produce a measurable pass-rate summary.
- Health endpoint verifies runtime readiness.

## Phase 5: Deployment And Documentation

Goal: make the service easy to run locally and ready for EC2 deployment review.

- Add a lightweight logging middleware and structured service logging to stdout/stderr for EC2/CloudWatch friendliness.
- Add deployment files with explicit Python base image, non-root runtime user, health check, `env_file: - .env`, documented port mapping, restart policy, and volume mounts for rail/prompt artifacts if needed.
- Write a full `README.md` mirroring the other services: overview, Mermaid architecture, local setup, Docker setup, API examples, configuration, development commands, and EC2 deployment notes.

Review checklist:

- Container build is explicit and reproducible.
- Runtime logs are suitable for Docker and CloudWatch.
- README covers architecture, setup, API, configuration, development, and deployment.

## Assumptions And Defaults

- Default accepted listing language is English only.
- `/check/output` should attempt a sanitized rewrite on failure when the content can be safely salvaged.
- Prompt iteration artifacts will be maintained in markdown in-repo first, with PDF/DOCX export treated as a packaging step rather than the source of truth.
- No shared cross-service library is required initially; `guardrails` is a standalone FastAPI service that can later be called by `ragService` or another orchestrator.
- Health endpoint should confirm API liveness and successful rail/runtime initialization, not external model quality.
