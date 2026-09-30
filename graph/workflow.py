import os
from typing import Literal
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage
from langgraph.graph import StateGraph, END
from langgraph.prebuilt import ToolNode
from graph.state import AgentState
from rag.agent import query_hosted_pdf_knowledge_base
from mcp_agents.github_agent import query_github_repo
from mcp_agents.google_agent import google_calendar_tool, google_gmail_tool

# Sub-agents ke tools
all_tools = [
    query_hosted_pdf_knowledge_base,
    query_github_repo,
    google_calendar_tool,
    google_gmail_tool
]

def build_graph():
    llm = ChatGroq(
        model="qwen/qwen3.8-27b",
        temperature=0,
        max_tokens=500,
        request_timeout=60.0,
        max_retries=3,
        api_key=os.getenv("GROQ_API_KEY")
    )
    model_with_tools = llm.bind_tools(all_tools)
    
    system_prompt = (
        "You are the Master Orchestrator Agent powered by LangGraph. You manage three sub-agents:\n\n"
        "1. **RAG Sub-Agent** (`query_hosted_pdf_knowledge_base`): Handles questions regarding documents, contracts, reports, or policies from hosted PDF vector storage.\n"
        "2. **GitHub Sub-Agent** (`query_github_repo`): Handles questions about repositories, issues, PRs, and code inspection via GitHub MCP.\n"
        "3. **Google Workspace Sub-Agent** (`google_calendar_tool`, `google_gmail_tool`): Reads meetings, creates calendar schedules, writes drafts, and sends emails.\n\n"
        "Instructions:\n"
        "- Analyze the user request carefully.\n"
        "- If the request requires multiple steps, execute all necessary tools step-by-step.\n"
        "- Provide a clear, structured, and helpful final response."
    )

    def supervisor_node(state: AgentState):
        messages = [SystemMessage(content=system_prompt)] + list(state["messages"])
        response = model_with_tools.invoke(messages)
        return {"messages": [response]}

    def should_continue(state: AgentState) -> Literal["tools", "__end__"]:
        last_message = state["messages"][-1]
        if hasattr(last_message, "tool_calls") and last_message.tool_calls:
            return "tools"
        return "__end__"

    workflow = StateGraph(AgentState)
    
    # Nodes
    workflow.add_node("supervisor", supervisor_node)
    workflow.add_node("tools", ToolNode(all_tools))
    
    # Edges
    workflow.set_entry_point("supervisor")
    workflow.add_conditional_edges(
        "supervisor",
        should_continue,
        {
            "tools": "tools",
            "__end__": END
        }
    )
    workflow.add_edge("tools", "supervisor")
    
    return workflow.compile()