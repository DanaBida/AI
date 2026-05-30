from fastapi import FastAPI, Request
import logging

app = FastAPI()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("leadsService")

@app.post("/residential-team")
async def residential_team_webhook(request: Request):
    data = await request.json()
    logger.info(f"Residential Team Lead: {data}")
    return {"status": "received", "team": "residential"}

@app.post("/commercial-team")
async def commercial_team_webhook(request: Request):
    data = await request.json()
    logger.info(f"Commercial Team Lead: {data}")
    return {"status": "received", "team": "commercial"}
