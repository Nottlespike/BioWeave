import os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from crewai import Agent, Task, Crew
from crewai.tools import BaseTool
from exa_py import Exa
import wandb
import litellm

# Initialize W&B Weave
wandb.init(project="BioWeave")

# Initialize FastAPI app
app = FastAPI()

class ExaSearchTool(BaseTool):
    name: str = "Exa Search"
    description: str = "Searches Exa for the given query and returns the results."

    def _run(self, query: str) -> str:
        exa = Exa(api_key=os.environ.get("EXA_API_KEY"))
        response = exa.search_and_contents(
            query,
            type="neural",
            num_results=3,
            highlights=True
        )
        return ''.join([
            f'<Title id={idx}>{eachResult.title}</Title>'
            f'<URL id={idx}>{eachResult.url}</URL>'
            f'<Highlight id={idx}>{"".join(eachResult.highlights)}</Highlight>'
            for (idx, eachResult) in enumerate(response.results)
        ])
search_and_get_contents_tool = ExaSearchTool()

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
    tools=[search_and_get_contents_tool],
    llm=None
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
        result = crew.kickoff(inputs={'topic': request.target, "model": "gemini/gemini-2.5-pro"})

        return {"result": result}

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/")
def read_root():
    return {"message": "Researcher Agent is running"}
