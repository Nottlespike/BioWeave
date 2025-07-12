import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()

class DiscoveryRequest(BaseModel):
    target: str

async def send_a2a_request(agent_url: str, task_payload: dict):
    """
    Sends a task request to an A2A-compliant agent.
    """
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(agent_url, json=task_payload, timeout=300.0)
            response.raise_for_status()
            return response.json()
        except httpx.HTTPStatusError as e:
            raise HTTPException(status_code=e.response.status_code, detail=f"A2A request failed: {e.response.text}")
        except httpx.RequestError as e:
            raise HTTPException(status_code=500, detail=f"A2A request failed: {str(e)}")

@app.post("/initiate_discovery")
async def initiate_discovery(request: DiscoveryRequest):
    """
    Receives a user request and delegates it to the Researcher agent.
    """
    researcher_agent_url = "http://researcher_agent:8000/v1/tasks"
    task_payload = {"target": request.target}

    try:
        result = await send_a2a_request(researcher_agent_url, task_payload)
        return result
    except HTTPException as e:
        raise e

@app.get("/")
def read_root():
    return {"message": "Orchestrator Agent is running"}
