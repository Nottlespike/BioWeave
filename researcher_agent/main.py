import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import litellm

app = FastAPI()

class TaskRequest(BaseModel):
    target: str

@app.post("/v1/tasks")
async def run_research_task(request: TaskRequest):
    """
    Executes a research task.
    """
    try:
        result = litellm.completion(
            model="gemini/gemini-2.5-pro",
            messages=[{"role": "user", "content": f"Find and analyze scientific literature on the biological target: {request.target}"}],
            api_key=os.environ.get("GEMINI_API_KEY"),
            stream=False,
        )
        
        return {"result": result["choices"][0]["message"]["content"]}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Researcher Agent is running"}
