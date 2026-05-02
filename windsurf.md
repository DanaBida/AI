# Instructions for aiPropertyTriageProject

## 1. Prompt Engineering Rules

### Log Format (per surface)

Each prompt engineering task must be documented with a structured log file. Follow this format for each of the 5 surfaces:

#### Version 1 — Baseline

- Write your first attempt at the prompt without overthinking it
- Run it on your complete test suite (minimum 10 test cases per surface)
- Record all outputs, pass rate, and failure patterns
- Document in: `prompts/iteration_surface_X_v1.pdf` (or .docx if preferred)

#### Versions 2 and 3 — Targeted Iterations

- Analyze v1 results and identify the **single most critical failure mode**
- Describe the failure in one sentence
- Modify prompt to directly address that specific failure
- Rerun complete test suite and record new outputs
- Assess: Did this fix improve pass rate? Did regressions appear?
- Document in: `prompts/iteration_surface_X_v2.pdf` and `_v3.pdf` (or .docx if preferred)

#### Versions 4 and 5 — Refinement

- Continue targeting remaining failure modes
- By version 5, articulate what you've learned:
  - Which phrasing patterns work reliably
  - Which types of instructions consistently fail
  - How this specific model responds to different instruction styles
- Document in: `prompts/iteration_surface_X_v4.pdf` and `_v5.pdf` (or .docx if preferred)

#### Final Entry

- State the final prompt for this surface
- Justify **each design decision** in the prompt (why this phrasing, why this structure)
- Report final pass rate on complete test suite
- Minimum requirement: **≥80% pass rate (8/10 tests minimum per surface)**
- Document in: `prompts/iteration_surface_X_final.pdf` (or .docx if preferred)

### Test Suite Requirements

- Minimum 10 test cases per surface
- Each test case must include:
  - Test ID
  - Input query
  - Retrieved documents
  - Expected behaviors (measurable criteria)
  - Assertion keywords (strings to find in output or patterns to validate)

---

## 2. Deployment Rules

### Dockerfile & Docker Compose Requirements

Every service in this project must include containerization files for AWS EC2 deployment:

#### Required Files per Service

- `Dockerfile` — Complete image specification
- `docker-compose.yml` — Service orchestration
- `.env.example` — Environment variable template

#### Dockerfile Standards

- Base image: Specify explicit version (e.g., `python:3.11-slim`, not `python:latest`)
- Multi-stage builds when applicable (for reducing image size)
- All dependencies installed from requirements.txt
- Expose relevant ports as comments
- Set working directory explicitly
- Include health checks if applicable
- Avoid running as root; use non-root user when possible

#### Docker Compose Standards

- Services defined with explicit versioning
- Volumes for persistent data (e.g., vector stores, databases)
- Environment variables from `.env` file
- Environment variables loaded from .env file using env_file directive: env_file: - .env
- Port mappings documented
- Networks defined for service isolation
- Restart policies set appropriately (`no`, `always`, `on-failure`, etc.)

#### AWS EC2 Deployment Readiness

- Images must be buildable on EC2 t3.small or larger
- Memory footprint documented (minimum RAM requirement)
- Mount points for volumes clearly specified
- Health check endpoints provided for services
- Logs directed to stdout/stderr for CloudWatch integration

---

## 3. Package Installation Rules

### Requirements.txt Management

All Python package dependencies must be managed via `requirements.txt` files.

#### Standards

- One `requirements.txt` per service (or at project root if monolithic)
- Pin versions explicitly: `package==1.2.3` (not `package>=1.0`)
- Group dependencies with comments:

  ```txt
  # Web Framework
  fastapi==0.104.1
  uvicorn==0.24.0

  # Vector Store & Embeddings
  chromadb==0.4.0
  sentence-transformers==2.2.2
  ```

---

## 4. Documentation Rules

### README Files for Services

Every service in this project must include a comprehensive `README.md` file with:

#### Required Sections

- **Overview**: Brief description of the service purpose and stack
- **Architecture Diagram**: Visual diagram (Mermaid, draw.io, or similar) annotating specific design decisions
- **Setup Instructions**: Both local development and Docker deployment
- **API Documentation**: Endpoints, request/response formats, examples
- **Configuration**: Environment variables and their purposes
- **Development**: How to run tests, linting, etc.
- **Deployment**: AWS EC2 deployment instructions and requirements

---

## 5. Code Structure Rules

### Directory Structure Standards

All services in this project must follow a clean architecture pattern with clear separation of concerns:

#### Required Directories per Service

- `models/` — Pydantic models and type definitions
- `controllers/` — FastAPI routers and endpoint definitions
- `services/` — Business logic and service layer implementations
- `middlewares/` — Custom middleware classes and logic
- `utils/` — Utility functions and helpers
- `tests/` — Unit and integration tests

#### Models Directory (`models/`)

- Contains all Pydantic models for API requests, responses, and data structures
- File naming: `{feature}_types.py` (e.g., `property_types.py`, `user_types.py`)
- Each model file should have clear docstrings explaining the purpose
- Import pattern: `from models.property_types import QueryRequest, QueryResponse`

#### Controllers Directory (`controllers/`)

- Contains FastAPI routers with endpoint definitions
- File naming: `{feature}_controller.py` (e.g., `property_controller.py`)
- Each controller should:
  - Use FastAPI's `APIRouter` for grouping related endpoints
  - Import and delegate to service classes for business logic
  - Handle only routing and basic request/response transformation
  - Include comprehensive docstrings for each endpoint

#### Services Directory (`services/`)

- Contains business logic implementations
- File naming: `{feature}_service.py` (e.g., `health_service.py`, `query_service.py`)
- Each service class should:
  - Be a static class with class methods (no instance state)
  - Handle all business logic for a specific feature
  - Import models from `models/` directory
  - Include error handling and validation
  - Return structured data (not raw responses)

#### Middlewares Directory (`middlewares/`)

- Contains custom middleware implementations
- File naming: `{purpose}_middleware.py` (e.g., `logging_middleware.py`, `auth_middleware.py`)
- Each middleware should:
  - Extend `BaseHTTPMiddleware` from Starlette
  - Handle cross-cutting concerns (logging, authentication, etc.)
  - Be imported and added to the FastAPI app in `app.py`

#### Utils Directory (`utils/`)

- Contains utility functions and helpers
- File naming: Descriptive names (e.g., `retrieval.py`, `llama_handler.py`)
- Functions should be pure and testable
- Avoid business logic; keep it focused on technical utilities

### Code Organization Principles

#### Separation of Concerns

- **Controllers**: Handle HTTP routing and request/response transformation only
- **Services**: Contain all business logic and domain operations
- **Models**: Define data structures and validation rules
- **Middlewares**: Handle cross-cutting concerns
- **Utils**: Provide technical utilities and helpers
- Replace step-comments such as `# Download image` or `# Preprocess` with small helper functions whose names describe the behavior; prefer extracting logic into clearly named methods over narrating code with inline comments.

#### Import Patterns

```python
# In controllers/feature_controller.py
from models.feature_types import RequestModel, ResponseModel
from services.feature_service import FeatureService

# In services/feature_service.py
from models.feature_types import DataModel

# In app.py
from controllers.feature_controller import router as feature_router
from middlewares.custom_middleware import CustomMiddleware
```

#### Naming Conventions

- **Directories**: lowercase, plural (models, controllers, services)
- **Files**: snake_case, descriptive (property_controller.py, health_service.py)
- **Classes**: PascalCase (HealthService, QueryRequest)
- **Functions/Methods**: snake_case (check_health, query_properties)

#### File Structure Template

```
service_name/
├── models/
│   ├── __init__.py
│   └── feature_types.py
├── controllers/
│   ├── __init__.py
│   └── feature_controller.py
├── services/
│   ├── __init__.py
│   └── feature_service.py
├── middlewares/
│   ├── __init__.py
│   └── custom_middleware.py
├── utils/
│   └── helper_functions.py
├── tests/
│   ├── test_feature_service.py
│   └── test_feature_controller.py
├── app.py
├── config.py
├── requirements.txt
└── README.md
```

---

## 6. Library Architecture Rules (Libs)

### Lib Directory Organization

Every service must maintain a `lib/` directory containing reusable, abstracted client wrappers and core integrations:

#### Required Structure

```
service_name/
└── lib/
    ├── __init__.py
    └── chromadb_client.py (or similar named clients)
```

#### ChromaDB Client Rules

- **Location**: `lib/chromadb_client.py`
- **Class**: `ChromaDBClient` wrapper class
- **Responsibilities**:
  - Encapsulate all ChromaDB initialization logic
  - Provide high-level methods: `inject()` and `search()`
  - Handle embedding generation internally
  - Manage collection lifecycle
- **Interface**:
  ```python
  class ChromaDBClient:
      def __init__(self, db_path: str, collection_name: str, embedding_model_name: str)
      def inject(self, documents: List[str], metadatas: List[Dict], ids: List[str]) -> int
      def search(self, query_text: str, top_k: int) -> List[Dict]
      def get_count(self) -> int
      def delete_collection(self)
  ```
- **Usage in Scripts**: Import from `lib.chromadb_client` and instantiate with config values
- **Logging**: Include comprehensive logging for debugging and monitoring

#### General Lib Principles

- Keep clients focused on a single external service/library (e.g., ChromaDB, Llama, external API)
- Abstract low-level details; expose only high-level, business-focused methods
- All clients must accept configuration (paths, model names, etc.) as constructor parameters
- Return structured, consistent data types (dicts, lists, custom dataclasses)
- Include error handling and validation at the client level

---

## 7. Environment Configuration Rules (Envs)

### Configuration Centralization

All environment variable reading must be centralized in `config.py` to ensure consistency, validation, and ease of maintenance:

#### Config.py Requirements

- **Single Source of Truth**: All env vars read exactly once in `config.py`
- **Class-Based Container**: Use a `Config` class to store all environment variables
- **Default Values**: Provide sensible defaults for all optional env vars
- **Type Conversion**: Explicitly convert string values to correct types (int, bool, etc.)
- **Documentation**: Include inline comments explaining each env var's purpose
- **Usage Pattern**:

  ```python
  from config import Config

  # Access config values directly
  db_path = Config.CHROMA_DB_PATH
  top_k = Config.TOP_K_LISTINGS
  ```

#### Environment Variables Standards

- Load `.env` file using `python-dotenv` in `config.py` (not in individual modules)
- Never import `os.getenv()` or `load_dotenv()` outside of `config.py`
- Always pass Config class values to library clients and services
- Document all env vars in `.env.example` with descriptions

#### Example Config.py Structure

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables (once, at import time)
load_dotenv()

class Config:
    """Centralized configuration container."""

    # Llama Model Configuration
    LLAMA_MODEL_NAME = os.getenv("LLAMA_MODEL_NAME", "default-model")
    LLAMA_MODEL_FILE = os.getenv("LLAMA_MODEL_FILE", "default.gguf")

    # ChromaDB Configuration
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", "/data/chroma_db")
    CHROMA_COLLECTION_NAME = os.getenv("CHROMA_COLLECTION_NAME", "properties")

    # Type conversions
    TOP_K_LISTINGS = int(os.getenv("TOP_K_LISTINGS", "3"))
    SERVER_PORT = int(os.getenv("SERVER_PORT", "8000"))
```

#### Import Pattern in Other Modules

```python
# data/load_synthetic_data.py
from config import Config
from lib.chromadb_client import ChromaDBClient

db_client = ChromaDBClient(
    db_path=Config.CHROMA_DB_PATH,
    collection_name=Config.CHROMA_COLLECTION_NAME,
    embedding_model_name=Config.EMBEDDING_MODEL
)
```

#### Benefits of Centralization

- Single place to modify configuration behavior
- Type-safe access to all environment values
- Easy to add validation and constraints
- Simplified unit testing (mock Config.py values)
- Clear dependency injection points

# Library/Client Code Placement

- All external service clients (e.g., Ollama, ChromaDB, n8n, external APIs) must be implemented in the `lib/` directory as reusable client classes. Do not place client code in `utils/`.
- The `utils/` directory is reserved for pure, general-purpose utility functions (e.g., math helpers, string manipulation, etc.) that do not encapsulate service or API logic. Example: `utils/math_helpers.py` for functions like `sum_list`, `average`, etc.
- Always import clients from `lib/` and utilities from `utils/` as appropriate.

## Initialize Once, Reuse Everywhere (Client Pattern)

- For lightweight API clients (e.g., `N8NClient`, `OllamaClient`), initialize a shared client once at module load and reuse it inside service classes.
- This avoids re-creating wrappers on every request while still talking to the same external service endpoint.

```python
# services/listing_service.py
from lib.n8n_client import N8NClient
from models.listing_types import ListingRecommendation, ListingSubmissionRequest

_SHARED_N8N_CLIENT = N8NClient()


class ListingService:
    _client = _SHARED_N8N_CLIENT

    @classmethod
    def submit(cls, request: ListingSubmissionRequest) -> ListingRecommendation:
        result = cls._client.submit_listing(
            agent_name=request.agent_name,
            listing_description=request.listing_description,
            image_urls=request.image_urls,
        )
        return ListingRecommendation.model_validate(result)
```

## Execution rules

- Never modify more than 3 files at once
- Never run terminal commands without asking
- Always present a plan before coding
- Stop after implementing the requested change

## Working with plans

- Never read full plan.md files
- Only act on tasks explicitly pasted in the prompt
- Ignore other phases
