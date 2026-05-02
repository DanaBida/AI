"""
FastAPI app entrypoint for LangGraph Agent service.
"""
from fastapi import FastAPI
from controllers.agent_controller import router as agent_router

app = FastAPI(title="LangGraph Agent Service")
app.include_router(agent_router)

@app.get("/", tags=["meta"])
def root():
    return {"service": "LangGraph Agent", "status": "ready", "agent_endpoint": "/agent/run"}
