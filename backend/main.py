from ag_ui_langgraph import add_langgraph_fastapi_endpoint
from copilotkit import LangGraphAGUIAgent
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.agents.test.agent import graph

app = FastAPI()

CORS_ORIGINS = ['*']

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

add_langgraph_fastapi_endpoint(
    app=app,
    agent=LangGraphAGUIAgent(
        name='test_agent',
        description='An example agent to use as a starting point for your own agent.',
        graph=graph,
    ),
    path='/api/agents/test',
)
