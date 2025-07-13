import httpx
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import litellm
import os

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
    Receives a user request, delegates it to the Researcher agent,
    and then to the Drug Proposal agent.
    """
    researcher_agent_url = "http://researcher_agent:8000/v1/tasks"
    drug_proposal_agent_url = "http://drug_proposal_agent:80/v1/tasks"

    # Step 1: Send task to Researcher Agent
    researcher_task_payload = {"target": request.target}
    try:
        research_result = await send_a2a_request(researcher_agent_url, researcher_task_payload)
    except HTTPException as e:
        raise e

    # Step 2: Send task to Drug Proposal Agent
    # Step 2: Process the research result to generate a masked SMILES
    try:
        masked_smiles_response = litellm.completion(
            model="gemini/gemini-2.5-pro",
            messages=[
                {"role": "system", "content": "You are a medicinal chemist. Your task is to propose a starting point for drug discovery. Based on the provided research, identify a relevant chemical scaffold and represent it as a SMILES string with a wildcard atom '[*]' at a position suitable for modification. Your output should be a single SMILES string and nothing else."},
                {"role": "user", "content": f"Here is the research report on {request.target}:\n\n{research_result['result']}"}
            ],
            api_key=os.environ.get("GEMINI_API_KEY"),
        )
        masked_smiles = masked_smiles_response["choices"][0]["message"]["content"].strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate masked SMILES: {str(e)}")

    # Step 3: Send task to Drug Proposal Agent
    drug_proposal_task_payload = {
        "masked_smiles": masked_smiles
    }
    try:
        drug_proposal_result = await send_a2a_request(drug_proposal_agent_url, drug_proposal_task_payload)
        return {
            "research_result": research_result,
            "drug_proposal": drug_proposal_result
        }
    except HTTPException as e:
        raise e

@app.get("/")
def read_root():
    return {"message": "Orchestrator Agent is running"}
