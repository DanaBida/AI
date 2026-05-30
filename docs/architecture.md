# Architecture Diagram and Design Decisions

Below is the architecture diagram for aiPropertyTriageProject, annotated with key design decisions.

```mermaid
flowchart TD
    A([User submits listing description & image URLs])
    B([WebUI])
    C([n8n Webhook])
    D([Guardrails Input\nReal estate relevance check])
    E([Gemini LLM\nInformation Executor])
    F([AI Agent])
    G([RAG Service\nMarket info])
    H([Image Analyzer\nRoom quality analysis])
    I([LangGraphAgent\nSummary of RAG & Image Analyzer])
    J([Basic LLM Chain\nProperty brief])
    K([Guardrails Output\nReliable check])
    L([Leads Service\nDepartment routing & logging])

    A --> B --> C --> D --> E --> F
    F -->|RAG| G
    F -->|Image Analysis| H
    F -->|Summary| I
    G --> J
    H --> J
    I --> J
    J --> K --> L
```

## Design Decisions

- **Microservices:** Each major function is a separate service for modularity and scalability.
- **n8n Orchestration:** n8n manages the workflow, making it easy to modify or extend the process.
- **Guardrails:** Input and output validation ensures only relevant and reliable data is processed.
- **LLM Executor:** Uses Gemini for robust property field extraction.
- **AI Agent:** Dynamically selects the best analysis tool(s) based on context.
- **RAG Service:** Retrieval-augmented generation for market data.
- **Image Analyzer:** Uses PyTorch for image quality analysis.
- **LangGraphAgent:** Aggregates and summarizes multi-tool results.
- **Leads Service:** Ensures leads are routed and logged correctly.

(Replace this diagram with your own annotated version if needed.)
