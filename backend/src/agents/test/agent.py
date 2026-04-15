from enum import Enum

from langchain.agents import create_agent
from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langchain_tavily import TavilySearch
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from pydantic import BaseModel, Field

from src.core.env import env

model = ChatOpenAI(model=env.OPENAI_MODEL, api_key=env.OPENAI_API_KEY, base_url=env.OPENAI_BASE_URL)

tavily_search = TavilySearch(tavily_api_key=env.TAVILY_API_KEY, max_results=1, return_metadata=True)


class DecisionEnum(str, Enum):
    general = 'general'
    web_search = 'web_search'


class RouteDecision(BaseModel):
    decision: DecisionEnum = Field(
        description='The decision of which route to take. Can be either "general" or "web_search".',
    )
    reason: str = Field(
        description='The reason for the decision. Should be written in 30 words or less.'
    )


class State(MessagesState):
    decision: DecisionEnum
    reason: str


async def llm_router(state: State):
    system_message = SystemMessage(
        content='You are a helpful assistant that decides whether to use web search or not based on the user query. If the user query is asking for information that is likely to be found on the web, you should decide to use web search. Otherwise, you should decide to use the general agent.'
    )

    agent = create_agent(
        model=model,
        response_format=RouteDecision,
        system_prompt=system_message,
    )

    response = await agent.ainvoke(
        {
            'messages': [
                system_message,
                *state['messages'],
            ]
        }
    )

    return {
        'decision': response['structured_response'].decision,
        'reason': response['structured_response'].reason,
    }


def route_decision(state: State):
    if state['decision'] == DecisionEnum.web_search:
        return 'web_search_agent'
    elif state['decision'] == DecisionEnum.general:
        return 'general_agent'


async def general_agent(state: MessagesState):
    system_message = SystemMessage(content='You are a helpful assistant.')
    response = await model.ainvoke(
        [
            system_message,
            *state['messages'],
        ]
    )
    return {'messages': response}


async def web_search_agent(state: MessagesState):
    agent = create_agent(
        model=model,
        tools=[tavily_search],
    )
    system_message = SystemMessage(
        content='You are a helpful assistant that can use tavily_search to find information needed to answer the user query.'
    )
    response = await agent.ainvoke(
        {
            'messages': [
                system_message,
                *state['messages'],
            ]
        }
    )

    return {'messages': response['messages']}


graph = StateGraph(State)
graph.add_node(llm_router)
graph.add_node(general_agent)
graph.add_node(web_search_agent)

graph.add_edge(START, 'llm_router')
graph.add_conditional_edges(
    'llm_router',
    route_decision,
    {
        'general_agent': 'general_agent',
        'web_search_agent': 'web_search_agent',
    },
)
graph.add_edge('general_agent', END)
graph.add_edge('web_search_agent', END)

if env.USE_CUSTOM_CHECKPOINTER:
    graph = graph.compile(checkpointer=InMemorySaver())
else:
    graph = graph.compile()
