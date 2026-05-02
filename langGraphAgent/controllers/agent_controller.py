"""
FastAPI router for LangGraph Agent endpoint.
"""
from fastapi import APIRouter, HTTPException

from models.agent_types import AgentQuery, AgentResponse
from services.agent_service import AgentService

router = APIRouter()


@router.post("/agent/run", response_model=AgentResponse, tags=["agent"])
def run_agent(query: AgentQuery):
    """
    Run the LangGraph agent on a complex property query.
    """
    try:
        return AgentService.run_agent(query.query)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    except TimeoutError as exc:
        raise HTTPException(status_code=504, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(
            status_code=500,
            detail="Unexpected error while running the LangGraph agent.",
        ) from exc
