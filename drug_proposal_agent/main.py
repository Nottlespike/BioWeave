from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import os
import requests

app = FastAPI()

# BioNeMo API configuration
BIONEMO_NIM_URL = os.getenv("BIONEMO_NIM_URL", "https://health.api.nvidia.com/v1/biology/nvidia/genmol/generate")
BIONEMO_API_KEY = os.getenv("BIONEMO_API_KEY")

class TaskInput(BaseModel):
    # For now, we'll expect a masked SMILES string.
    # In a real scenario, this would be more complex, likely derived from research_results.
    masked_smiles: str

class TaskOutput(BaseModel):
    smiles: str

@app.post("/v1/tasks", response_model=TaskOutput)
async def generate_smiles(task_input: TaskInput):
    """
    Receives a masked SMILES string and generates a novel molecule
    using the NVIDIA GenMol NIM.
    """
    # In a real application, you would derive the masked_smiles from the research results.
    # For example, identifying a scaffold and adding a mask for generation.
    # This is a placeholder for that logic.
    
    payload = {
        "smiles": task_input.masked_smiles,
        "num_molecules": 5,
        "scoring": "QED"
    }

    headers = {
        "Content-Type": "application/json"
    }
    if BIONEMO_API_KEY:
        headers["Authorization"] = f"Bearer {BIONEMO_API_KEY}"

    try:
        response = requests.post(BIONEMO_NIM_URL, json=payload, headers=headers)
        response.raise_for_status()  # Raise an exception for bad status codes
        
        response_data = response.json()

        if response_data.get("status") == "success" and response_data.get("molecules"):
            # Return the SMILES of the top-scoring molecule
            top_molecule = response_data["molecules"][0]
            return TaskOutput(smiles=top_molecule["smiles"])
        else:
            error_message = response_data.get("error", "Unknown error from GenMol NIM")
            raise HTTPException(status_code=500, detail=f"Failed to generate molecule: {error_message}")

    except requests.exceptions.RequestException as e:
        raise HTTPException(status_code=502, detail=f"Error communicating with GenMol NIM: {e}")

@app.get("/")
def read_root():
    return {"message": "Drug Proposal Agent is running"}
