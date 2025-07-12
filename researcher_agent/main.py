import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew
from crewai_tools import ExaSearchTool
import wandb

# Initialize W&B Weave
wandb.init(project="BioWeave")

# Initialize FastAPI app
app = FastAPI()

# Exa API key setup
os.environ["EXA_API_KEY"] = "your_exa_api_key"  # Replace with your actual key

# Define the research tool
search_tool = ExaSearchTool()

# Define the Researcher Agent
researcher = Agent(
    role='Expert Scientific Researcher',
    goal='Analyze scientific literature to find data on a given biological target.',
    backstory="""You are a renowned scientific researcher with expertise in molecular biology and drug discovery.
    Your mission is to meticulously analyze scientific papers, clinical trials, and research data to extract
    critical information on biological targets. You are known for your precision, accuracy, and ability to
    synthesize complex information into actionable insights.""",
    verbose=True,
    allow_delegation=False,
    tools=[search_tool]
)

class TaskRequest(BaseModel):
    target: str

@app.post("/v1/tasks")
async def run_research_task(request: TaskRequest):
    """
    Executes a research task using the CrewAI agent.
    """
    try:
        # Define the research task
        research_task = Task(
            description=f"Find and analyze scientific literature on the biological target: {request.target}",
            expected_output=f"A comprehensive report on {request.target}, including its function, role in disease, and potential as a drug target.",
            agent=researcher
        )

        # Create and run the crew
        crew = Crew(
            agents=[researcher],
            tasks=[research_task],
            verbose=True
        )

        # Execute the crew's task and get the result
        result = crew.kickoff()

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Researcher Agent is running"}
