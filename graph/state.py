from typing import Sequence, TypedDict, Annotated
from langchain_core.messages import BaseMessage
from langgraph.graph.message import add_messages

class AgentState(TypedDict):
    # LangGraph message history reducer
    messages: Annotated[Sequence[BaseMessage], add_messages]
