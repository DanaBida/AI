
# aiPropertyTriageProject

This repository contains an AI-powered property triage platform, orchestrating multiple microservices for real estate listing analysis, image processing, and lead routing.

---

## Directory Structure

- `/code` — All source code and workflow files
    - `n8n.json` — Importable n8n flow
    - `guardrails/`, `imageAnalyzer/`, `langGraphAgent/`, `ragService/` — Each EC2 service with Dockerfile and requirements.txt
    - `webui/` — Web interface source code
- `/docs` — All documentation
    - `architecture.md` — Architecture diagram and design notes
    - `Deployment_Notes.md` — EC2 instance types, ports, and deviations
- `/demo` — Video file or link

---

## Setup & Run Instructions

### 1. Clone the repository
```sh
git clone <your-repo-url>
cd aiPropertyTriageProject
```

### 2. Build and Run Services
Each service is in `/code/<service>/`. Example for `guardrails`:
```sh
cd code/guardrails
pip install -r requirements.txt
uvicorn app:app --host 0.0.0.0 --port 8011
```
Or with Docker:
```sh
docker build -t guardrails .
docker run -p 8011:8011 guardrails
```
Repeat for other services (`imageAnalyzer`, `langGraphAgent`, `ragService`) with relative ports.

### 3. WebUI
```sh
cd code/webui
pip install -r requirements.txt
streamlit run app.py --server.address=0.0.0.0 --server.port=8501
```

### 4. Pre-populate ChromaDB (ImageAnalyzer)
```sh
cd code/imageAnalyzer
python prepopulate_chromadb.py
```

### 5. Train Image Analyzer Model (or use .pth checkpoint)
```sh
python train_image_model.py
```

### 6. n8n Workflow
- Import `code/n8n.json` into your n8n instance.

---

## Documentation
- See `/docs/architecture.md` for the architecture diagram and design notes.
- See `/docs/Deployment_Notes.md` for deployment specifics.

---

## Demo
- Demo video in `/demo`.

---

## Notes
- Each service has its own README for local running instructions.
- For EC2 deployment, see `/docs/Deployment_Notes.md`.
