# Plan: RAG Property Listing Service with Llama.cpp

## TL;DR

Build a FastAPI-based RAG service that queries a persistent ChromaDB vector store to find similar property listings, then generates insights using Llama.cpp. Pre-populate with 20+ synthetic properties (JSON format with price, bedrooms, location, condition fields). Auto-download GGUF model from Hugging Face. Deploy with Docker volumes for persistence. Conduct structured prompt engineering with 5 surfaces, 5 iterations each, documented with failure analysis in markdown logs.

---

## Steps

### **Phase 1: Project Setup & Infrastructure**

1. Create directory structure for `aiPropertyTriangeProject/ragService/`
   - `app.py` - FastAPI main server (entry point)
   - `config.py` - centralized configuration (ALL env var reads happen here)
   - `lib/` - Library abstractions (ChromaDB client, LLM handlers)
     - `lib/__init__.py` - Library module exports
     - `lib/chromadb_client.py` - ChromaDB wrapper with inject() and search() methods
   - `models/` - Pydantic models and type definitions
     - `models/property_types.py` - API request/response models
   - `controllers/` - FastAPI routers and endpoints
     - `controllers/property_controller.py` - Health and query endpoints
   - `services/` - Business logic implementations
     - `services/health_service.py` - Health check logic
     - `services/query_service.py` - RAG pipeline logic
   - `middlewares/` - Custom middleware classes
     - `middlewares/logging_middleware.py` - Request/response logging
   - `utils/` - Utility functions and helpers
   - `data/` - synthetic property listings
   - `prompts/` - prompt engineering logs (iteration_surface_1.md, etc.)
   - `tests/` - test cases for prompt validation
   - `requirements.txt` - dependencies
   - `docker-compose.yml` - service orchestration with ChromaDB volume
   - `Dockerfile` - containerized service

2. Define requirements.txt with:
   - fastapi, uvicorn (server)
   - chromadb (vector store)
   - sentence-transformers (embeddings - all-MiniLM-L6-v2)
   - llama-cpp-python (Llama.cpp wrapper)
   - pydantic (request/response models)
   - python-dotenv (env config)

3. Create environment variable template:
   - `LLAMA_MODEL_NAME` (default: "TheBloke/Mistral-7B-Instruct-v0.1-GGUF")
   - `LLAMA_MODEL_FILE` (default: "mistral-7b-instruct-v0.1.Q4_K_M.gguf")
   - `CHROMA_DB_PATH` (default: "/data/chroma_db")
   - `EMBEDDING_MODEL` (default: "all-MiniLM-L6-v2")
   - `TOP_K_LISTINGS` (default: 3)

4. **[RULE] Architecture - Libs**: Create `lib/chromadb_client.py` with `ChromaDBClient` class
   - Encapsulates ChromaDB initialization
   - Exposes `inject(documents, metadatas, ids)` method
   - Exposes `search(query_text, top_k)` method
   - Handles embedding generation internally
   - Manages collection lifecycle

5. **[RULE] Architecture - Envs**: Create centralized `config.py`
   - Load `.env` file once using `load_dotenv()`
   - Define `Config` class with all environment variables as class attributes
   - Provide type conversions (e.g., int, bool) where needed
   - All modules import Config from here; NEVER call `os.getenv()` or `load_dotenv()` elsewhere

### **Phase 2: Synthetic Data Generation**

4. Create `data/properties.json` with 20+ property listings
   - Fields per listing: id, price, bedrooms, bathrooms, rooms, location, condition, description (short text)
   - Example: `{"id": "prop_001", "price": 2500000, "bedrooms": 3, "bathrooms": 2, "rooms": 5, "location": "Haifa Downtown", "condition": "Good", "description": "..."}`
   - Locations: Israeli cities and neighborhoods (Haifa Downtown, Tel Aviv North, Jerusalem Center, etc.)

5. Create `data/load_synthetic_data.py`
   - Load JSON properties
   - Convert each to text format: "Property {id}: ₪{price}, {rooms} rooms, {bedrooms} bed, {bathrooms} bath, located in {location}, condition {condition}. {description}"
   - **[RULE] Libs**: Import `ChromaDBClient` from `lib.chromadb_client`
   - **[RULE] Envs**: Import `Config` from `config` module (NOT individual env vars)
   - Instantiate ChromaDBClient with Config values: `ChromaDBClient(Config.CHROMA_DB_PATH, Config.CHROMA_COLLECTION_NAME, Config.EMBEDDING_MODEL)`
   - Call `db_client.inject(documents, metadatas, ids)` to populate ChromaDB
   - Mark as one-time initialization script (run before deployment)

### **Phase 3: Core Service Implementation**

6. Create `config.py`
   - **[RULE] Envs**: Centralize ALL environment variable reads in this file
   - Load `.env` file once using `load_dotenv()` at module import time
   - Define `Config` class with all env vars as class attributes
   - Provide type conversions (int, bool, etc.) for numeric/boolean values
   - No other module should call `os.getenv()` or `load_dotenv()`
   - Include comments explaining each variable's purpose

7. Create `lib/chromadb_client.py` - ChromaDB wrapper
   - **[RULE] Libs**: `ChromaDBClient` class that wraps ChromaDB operations
   - Constructor: `__init__(db_path, collection_name, embedding_model_name)`
   - Initialize embedding model and ChromaDB client internally
   - Method: `inject(documents, metadatas, ids)` - embed and insert documents
   - Method: `search(query_text, top_k)` - embed query and return similar results
   - Method: `get_count()` - return total documents in collection
   - Comprehensive logging for all operations

8. Create Pydantic models in `models/property_types.py`
   - `ListingResult` - Retrieved property listing result
   - `QueryRequest` - Request model for /query endpoint
   - `QueryResponse` - Response model for /query endpoint
   - `HealthResponse` - Response model for /health endpoint

9. Create `controllers/property_controller.py` with FastAPI router
   - `GET /health` endpoint - delegates to HealthService
   - `POST /query` endpoint - delegates to QueryService
   - Import models from `models/` directory

10. Create `services/health_service.py`
    - `HealthService.check_health()` - Health check business logic
    - Return structured health status data

11. Create `services/query_service.py`
    - `QueryService.query_properties()` - RAG pipeline implementation
    - **[RULE] Libs**: Use `ChromaDBClient` from `lib.chromadb_client` (call `search()` method)
    - Extract listing description from request
    - Call `db_client.search(description, top_k=Config.TOP_K_LISTINGS)` to retrieve similar properties
    - Format retrieved context into prompt template
    - Call Llama.cpp to generate insight
    - Return structured response data

12. Create `middlewares/logging_middleware.py`
    - `LoggingMiddleware` - Request/response logging
    - Log all incoming requests and outgoing responses
    - Include timing and status information

13. Create `utils/retrieval.py`:
    - Function `format_context(retrieved_listings)` → formatted string for LLM prompt

14. Create `utils/llama_handler.py`:
    - Function `initialize_llama_model(model_name, model_file)` → model instance
    - Function `download_model_if_needed(model_name, model_file, output_path)` → path to GGUF file
    - Function `generate_insight(model, context, query, prompt_template)` → insight string
    - Error handling: fallback if model download fails

### **Phase 4: Prompt Engineering (5 Surfaces × 5 Iterations)**

11. Define 5 prompt engineering surfaces to iterate on:
    - **Surface 1**: Citation format - How to instruct model to cite source listings
    - **Surface 2**: Hallucination prevention - How to prevent fabricating details
    - **Surface 3**: Context injection - How to structure retrieved documents in prompt
    - **Surface 4**: Output format - How to specify desired insight structure
    - **Surface 5**: Relevance filtering - How to instruct model to only use relevant context

12. Create test suite (minimum 10 test cases per surface):
    - Test cases: `tests/test_prompts.json` with format:
      ```json
      {
        "test_id": "cite_001",
        "query": "...",
        "retrieved_docs": [...],
        "expected_behaviors": ["cites_property_id", "no_fabrication"],
        "assertion_keywords": ["Property", "from the", "listing"]
      }
      ```
    - Manual test runner: `tests/run_prompt_tests.py` to execute and log results

13. Iteration 1 - Baseline (each surface):
    - Write naive first-attempt prompt without overthinking
    - Run on test suite, record outputs and pass rate
    - Document in `prompts/iteration_surface_X_v1.pdf` (or .docx if preferred)

14. Iterations 2-3 - Targeted fixes:
    - Identify top failure mode from v1
    - Modify prompt to address specific failure
    - Run test suite, assess fix vs. regressions
    - Document in `prompts/iteration_surface_X_v2.pdf` and `_v3.pdf` (or .docx if preferred)
    - Analyze: Did this fix improve pass rate? Did it break anything?

15. Iterations 4-5 - Refinement:
    - Continue targeting failure modes
    - By v5, document model behavior patterns and phrasings that work
    - Document in `prompts/iteration_surface_X_v4.pdf` and `_v5.pdf` (or .docx if preferred)
    - Final entry: Justify design decisions, report final pass rate

16. Consolidate final prompts:
    - Choose best v5 prompt for each surface
    - Create `prompts/final_prompts.py` module with:
      - `SYSTEM_PROMPT` - base instruction
      - `RETRIEVAL_PROMPT_TEMPLATE` - context injection template
      - `CITATION_INSTRUCTION` - citation formatting rules
      - `HALLUCINATION_GUARD` - instructions to prevent fabrication
    - Store version metadata: which iteration won, pass rate, date

### **Phase 5: FastAPI Server & Deployment**

17. Create `app.py` main application:
    - FastAPI app initialization
    - Import and include property router from `controllers/property_controller.py`
    - Add logging middleware from `middlewares/logging_middleware.py`
    - Load config on startup
    - Error handling: graceful failures with descriptive messages
    - Logging: structured logs for requests, retrieval, LLM calls

18. Create `docker-compose.yml`:
    - Service 1: FastAPI app (port 8000)
    - Service 2: ChromaDB server container OR embedded (depends on approach)
    - Volume: `/data/chroma_db` mounted on host → persistent vector store
    - Environment variables passed via `.env` file
    - Use env_file directive: env_file: - .env
    - Build from `Dockerfile`

19. Create `Dockerfile`:
    - Base image: `python:3.11-slim`
    - Install system dependencies (if Llama.cpp needs compilation)
    - Copy requirements, install via pip
    - Copy source code
    - Run initialization script to load synthetic data (or conditional check)
    - Expose port 8000
    - CMD: `uvicorn app:app --host 0.0.0.0 --port 8000`

20. Create `.env.example`:
    - Template with all configurable variables
    - Document defaults and accepted values

### **Phase 6: Verification**

21. Verification steps:
    - **Unit tests**: `tests/test_embedding.py`, `tests/test_chromadb.py`, `tests/test_llama.py`
    - **Integration test**: `tests/test_e2e.py` - full `/query` flow
    - **Prompt validation**: Run `tests/run_prompt_tests.py` to confirm all surfaces pass minimum 8/10 tests
    - **Manual test**: Call `/query` with sample description, inspect similar_listings + insight quality
    - **Docker test**: Build image, run container, test `/health` and `/query` endpoints

### **Phase 7: Documentation**

22. Create `README.md`:
    - Overview, stack description
    - Architecture diagram annotating specific design decisions
    - Setup instructions (local + Docker)
    - API documentation (endpoint, request/response examples)
    - Prompt engineering summary (link to iteration logs)
    - Performance notes (latency, throughput)

23. Create prompt engineering summary document `prompts/ENGINEERING_LOG.md`:
    - Overview of 5 surfaces and why they matter
    - Link to each surface's iteration files
    - Final prompt decisions and pass rates
    - Lessons learned about Llama.cpp prompt sensitivity

---

## Relevant Files

- `aiPropertyTriangeProject/ragService/app.py` — FastAPI app entry point, router/middleware configuration
- `aiPropertyTriangeProject/ragService/config.py` — Model initialization, ChromaDB client, env config
- `aiPropertyTriangeProject/ragService/models/property_types.py` — Pydantic models for API requests/responses
- `aiPropertyTriangeProject/ragService/controllers/property_controller.py` — FastAPI router with health and query endpoints
- `aiPropertyTriangeProject/ragService/services/health_service.py` — Health check business logic
- `aiPropertyTriangeProject/ragService/services/query_service.py` — RAG pipeline business logic
- `aiPropertyTriangeProject/ragService/middlewares/logging_middleware.py` — Request/response logging middleware
- `aiPropertyTriangeProject/ragService/utils/retrieval.py` — ChromaDB querying, embedding, context formatting
- `aiPropertyTriangeProject/ragService/utils/llama_handler.py` — Llama.cpp initialization, model download, inference
- `aiPropertyTriangeProject/ragService/prompts/final_prompts.py` — Final prompt templates (winner of iterations)
- `aiPropertyTriangeProject/ragService/data/properties.json` — 20+ synthetic property listings (JSON)
- `aiPropertyTriangeProject/ragService/data/load_synthetic_data.py` — ChromaDB initialization from JSON
- `aiPropertyTriangeProject/ragService/tests/run_prompt_tests.py` — Prompt validation runner
- `aiPropertyTriangeProject/ragService/docker-compose.yml` — Service orchestration with persistent volume

**Template reference files from workspace**:

- [lesson3/rag_web/app.py](http://_vscodecontentref_/0) — FastAPI-style endpoint patterns (adapt Flask to FastAPI)
- [homeworkGeminiAPI/chatbot/service.py](http://_vscodecontentref_/1) — Business logic separation pattern
- [homeworkGeminiAPI/utils/rag.py](http://_vscodecontentref_/2) — FAISS-based retrieval (adapt to ChromaDB API)

---

## Verification

1. **Prompt engineering**: All 5 surfaces × 5 iterations complete with documented failure analysis; final prompts achieve ≥80% pass rate on test suites (8/10 minimum per surface)
2. **Vector store**: ChromaDB initialized with 20+ properties, queries return top-3 relevant listings with proper metadata
3. **API endpoint**: `/query` accepts property description, returns `similar_listings` array + `insight` string with proper citations
4. **Model download**: Llama.cpp GGUF auto-downloaded from HF on first run, model inference produces coherent text
5. **Docker**: `docker-compose up` builds and runs service; `/health` returns OK; `/query` works; ChromaDB persists across container restarts
6. **No hallucination**: Insight text only references retrieved listings, no fabricated property details

---

## Decisions

- **Framework**: FastAPI (not Flask) — aligns with user requirements despite workspace pattern using Flask
- **Code Architecture**: Clean Architecture with separation of concerns
  - `models/` - Pydantic type definitions and data models
  - `controllers/` - FastAPI routers and endpoint definitions
  - `services/` - Business logic implementations
  - `middlewares/` - Cross-cutting concerns (logging, auth, etc.)
- **Vector Store**: ChromaDB with Docker volume persistence — enables reproducible deployments and prevents data loss
- **Llama.cpp auto-download**: HuggingFace source — simplifies deployment, no pre-built model needed
- **Synthetic data format**: Simple JSON (price, bedrooms, location, condition) — lightweight, easy to generate 20+ variations, sufficient for testing RAG quality
- **Prompt engineering scope**: 5 surfaces × 5 iterations minimum with structured markdown logs — rigorous iteration tracking to demonstrate prompt sensitivity and improvements
- **Embedding model**: HuggingFace `sentence-transformers` (all-MiniLM-L6-v2) — matches workspace pattern, proven for retrieval tasks
- **Top-K retrieval**: k=3 listings — balance between context richness and prompt token limits

**Excluded**:

- Fine-tuning Llama model (use off-the-shelf GGUF)
- Advanced retrieval techniques (BM25, hybrid search) — simple semantic similarity sufficient
- Production monitoring/observability (basic logging only)
- Authentication/rate limiting (focus on RAG core)

---

## Further Considerations

1. **Llama.cpp model selection**: Current plan uses Mistral-7B-Instruct. Consider alternatives:
   - **Option A** (Recommended): Mistral-7B — good balance of speed/quality, 7B params manageable on consumer hardware
   - **Option B**: Llama-2-7B-Chat — proven, slightly larger, may be slower
   - **Option C**: TinyLlama-1.1B — ultra-fast inference, lower quality output
   - Decision: Use Mistral-7B as primary, make model configurable via env var

2. **Hardware requirements for documentation**: Llama.cpp models require ~4-8 GB RAM depending on quantization. Should README specify minimum hardware?
   - Recommendation: Document in README, add startup warning if RAM < 4GB

3. **Prompt engineering methodology**: Should test suite be automated (pytest) or manual (human review of outputs)?
   - Recommendation: Hybrid — automated keyword/regex checks for obvious failures + manual review of quality for final pass/fail judgment
