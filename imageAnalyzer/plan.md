# Image Analyzer Service Plan

## Overview

A FastAPI-based image analysis service for property images using PyTorch and EfficientNet-B0. The service classifies room types (kitchen, bathroom, living room, bedroom, exterior, other) and predicts condition scores (1-5), with a confidence threshold of 0.85 below which it returns an "uncertain" label.

## Endpoint Specification

### POST /analyse

**Input:**

```json
{
  "image_url": "<url>"
}
```

**Output:**

```json
{
  "room_type": "kitchen",
  "condition_score": 4,
  "confidence": 0.91
}
```

When confidence < 0.85:

```json
{
  "room_type": "uncertain",
  "condition_score": null,
  "confidence": <actual_confidence>
}
```

## Technology Stack

- **Framework**: FastAPI, Uvicorn
- **Deep Learning**: PyTorch, torchvision, timm (EfficientNet)
- **Image Processing**: Pillow
- **Configuration**: python-dotenv, Pydantic
- **Dataset**: Kaggle public datasets
- **Testing**: pytest, httpx

## Implementation Phases

### Phase 1: Project Structure Setup

Create directory structure following AGENTS.md clean architecture patterns:

```
imageAnalyzer/
├── models/
│   ├── __init__.py
│   └── image_types.py
├── controllers/
│   ├── __init__.py
│   └── image_controller.py
├── services/
│   ├── __init__.py
│   └── image_service.py
├── lib/
│   ├── __init__.py
│   └── pytorch_model_client.py
├── middlewares/
│   ├── __init__.py
│   └── logging_middleware.py
├── utils/
│   ├── __init__.py
│   ├── image_utils.py
│   └── augmentation.py
├── data/
│   ├── download_dataset.py
│   ├── prepare_dataset.py
│   └── README.md
├── scripts/
│   ├── train_model.py
│   └── docker-start.sh
├── tests/
│   ├── test_model_client.py
│   ├── test_image_service.py
│   └── test_controller.py
├── app.py
├── config.py
├── requirements.txt
├── .env.example
├── Dockerfile
├── docker-compose.yml
└── plan.md
```

### Phase 2: Data Models

**File: models/image_types.py**

Define Pydantic models for request/response validation.

### Phase 3: Dataset Preparation

**Phase 3a: Download Dataset** - Kaggle public datasets (≥200 images per room class)
**Phase 3b: Data Preprocessing** - Resize to 224×224, normalize with ImageNet stats
**Phase 3c: Data Augmentation** - RandomResizedCrop, HorizontalFlip, rotation, ColorJitter, blur, erasing

### Phase 4: Model Training

**File: lib/pytorch_model_client.py** - EfficientNet-B0 with frozen backbone + 2 heads
**File: scripts/train_model.py** - Training loop with early stopping, target ≥80% accuracy

### Phase 5: Service Implementation

**File: controllers/image_controller.py** - POST /analyse, GET /health endpoints
**File: services/image_service.py** - Image download, preprocess, inference, confidence logic

### Phase 6: Deployment Setup

**File: Dockerfile** - Multi-stage build, python:3.11-slim, health checks
**File: docker-compose.yml** - Service orchestration with volumes

Status: Completed on 2026-04-22

Implemented:
- Multi-stage `Dockerfile` using explicit `python:3.11-slim` images
- Non-root runtime user for safer container execution
- Health checks against `GET /health`
- `docker-compose.yml` with `env_file`, named volumes, bridge network, and restart policy
- Expanded `.env.example` and centralized runtime settings in `config.py`
- Container entrypoint script using `uvicorn app:app`

### Phase 7: Testing & Documentation

**File: tests/** - Unit tests for model, service, controller
**File: README.md** - Complete documentation with architecture, setup, results

Status: Completed on 2026-04-22

Implemented:
- Unit tests for `PytorchModelClient`, `ImageService`, and API endpoints
- README with overview, Mermaid architecture diagram, setup, API, configuration, development, and deployment sections
- Additional testing dependencies and the `timm` model package added to `requirements.txt`

## Key Decisions

- **Base Model**: EfficientNet-B0 (efficient, good accuracy)
- **Confidence Threshold**: 0.85 (balanced precision/coverage)
- **Uncertain Handling**: Return "uncertain" as room_type with null condition_score
- **Dataset Source**: Kaggle public datasets
- **Augmentations**: RandomResizedCrop, HorizontalFlip, ±10° rotation, ColorJitter, blur, RandomErasing
- **Transfer Learning**: Freeze backbone, fine-tune classifier heads
- **Multi-head Model**: Classification head (6 room types) + Regression head (condition 1-5)
- **Target Accuracy**: ≥80% on test set

## Success Criteria

✅ Service starts without errors
✅ POST /analyse accepts image URL, returns correct JSON format
✅ Confidence threshold logic works (≥0.85 = definitive, <0.85 = "uncertain")
✅ Model test accuracy ≥80%
✅ Docker build succeeds, service runs in container
✅ Unit tests pass
✅ Documentation complete with results
