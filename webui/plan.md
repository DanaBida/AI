# WebUI & Local Ollama Integration — plan.md

## Summary

This project delivers a Streamlit-based WebUI for the aiPropertyTriangeProject, integrating with a local Ollama LLM (Llama 3 or Mistral) and an n8n webhook. The app provides two main tabs: a Conversational Assistant (real estate-focused chat with prompt engineering iteration) and a Listing Submission form (submits to n8n, displays structured results). All code, prompts, and configuration follow repository best practices and conventions.

## Public Interface

- **Conversational Assistant Tab**
  - User input: Chat messages
  - Output: Model responses (real estate only, off-topic politely refused)
  - System prompt: Versioned, iterated, and logged per prompt engineering rules
- **Listing Submission Tab**
  - User input: Listing description, image URLs (comma/file), agent name
  - Output: Structured report from n8n (image scores, recommendations)
- **Config**: All environment/config values via config.py (Config class)

## Phases

### Phase 1: Project Skeleton & Core Contracts

**Goal:** Establish directory structure, config, and core interfaces.

**Tasks:**

- Create webui/app.py as Streamlit entrypoint
- Add models/, controllers/, services/, utils/, tests/, prompts/ per repo standards
- Implement config.py with Config class for all env/config values
- Add requirements.txt (pinned versions)
- Update README.md with overview and architecture diagram

**Review Checklist:**

- All required directories and files exist
- Config handled only via config.py
- README and requirements.txt present

---

### Phase 2: Conversational Assistant Tab & Ollama Integration

**Goal:** Implement chat UI, Ollama client, and system prompt iteration.

**Tasks:**

- Build chat tab in app.py (Streamlit)
- Implement lib/ollama_client.py for local Ollama API
- System prompt loaded from prompts/iteration_surface_1_vX.txt
- All config (host, port, model) from config.py
- Log each prompt version and test results per prompt engineering rules

**Review Checklist:**

- Chat UI functional
- Ollama client works with local server
- System prompt versioning/logging in place
- No direct os.getenv() outside config.py

---

### Phase 3: Listing Submission Tab & n8n Integration

**Goal:** Implement listing form, n8n client, and result display.

**Tasks:**

- Build listing form tab in app.py
- Implement libs/n8n_client.py for webhook POST
- Display n8n response (image scores, recommendations) in UI
- Document request/response format in README.md

**Review Checklist:**

- Form submits to n8n and displays results
- n8n client uses config.py for URL
- README documents integration

---

### Phase 4: Prompt Engineering & Testing

**Goal:** Complete prompt engineering iterations and add tests.

**Tasks:**

- For each prompt version: write, test (10+ cases), log results in prompts/iteration_surface_1_vX.pdf
- Final prompt and justification in prompts/iteration_surface_1_final.pdf
- Add unit/integration tests for both tabs and utils

**Review Checklist:**

- Prompt logs and final prompt meet test suite/pass rate requirements
- Tests cover UI and backend logic

---

### Phase 5: Deployment & Documentation

**Goal:** Ensure deployability and complete documentation.

**Tasks:**

- Add Dockerfile, docker-compose.yml, .env.example per repo standards
- Document deployment (local, Docker, AWS EC2) in README.md
- Add health check endpoint if needed
- Document memory footprint and volume mounts

**Review Checklist:**

- All deployment files present and standards-compliant
- README covers all required sections
- App buildable and runnable per docs

---

## Assumptions & Defaults

- Streamlit is used for UI (can be swapped for Gradio if needed)
- Ollama and n8n are running and reachable from WebUI
- All configuration is centralized in config.py
- Prompt engineering follows repo’s structured log/test suite process
- No direct os.getenv() outside config.py
- All new code matches repo’s architecture and naming conventions
