from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI

from src.agents.test_agent.agent import graph

app = FastAPI()

add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name='Test agent',
        description='An example agent to use as a starting point for your own agent.',
        graph=graph,
    ),
    path='/api/agents/test',
)
