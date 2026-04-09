from langchain_core.messages import SystemMessage
from langchain_openai import ChatOpenAI
from langgraph.checkpoint.memory import InMemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph

from src.core.env import env


async def mock_llm(state: MessagesState):
    model = ChatOpenAI(
        model=env.OPENAI_MODEL, api_key=env.OPENAI_API_KEY, base_url=env.OPENAI_BASE_URL
    )
    system_message = SystemMessage(content='You are a helpful assistant.')
    response = await model.ainvoke(
        [
            system_message,
            *state['messages'],
        ]
    )
    return {'messages': response}


checkpointer = InMemorySaver()

graph = StateGraph(MessagesState)
graph.add_node(mock_llm)
graph.add_edge(START, 'mock_llm')
graph.add_edge('mock_llm', END)
graph = graph.compile(checkpointer=checkpointer)
