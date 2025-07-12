from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from mcp_client import MCPClient

app = FastAPI()

class DiscoveryRequest(BaseModel):
    target: str

@app.post("/initiate_discovery")
async def initiate_discovery(request: DiscoveryRequest):
    """
    Receives a user request and delegates it to the Researcher agent using MCP.
    """
    researcher_agent_mcp_server = "http://researcher_agent:8000"
    
    try:
        async with MCPClient(server_url=researcher_agent_mcp_server) as client:
            # Discover available tools
            tools = await client.discover()
            
            # Assuming the researcher agent has a 'research' tool
            research_tool = next((t for t in tools if t.name == "research"), None)
            
            if not research_tool:
                raise HTTPException(status_code=500, detail="Researcher agent does not have a 'research' tool")

            # Execute the task using the discovered tool
            result = await client.execute(tool_name="research", parameters={"target": request.target})
            return result
            
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"MCP request failed: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Orchestrator Agent is running"}
