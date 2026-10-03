import os
import json
from datetime import datetime
import streamlit as st
from dotenv import load_dotenv

# Local machine ke liye .env load karein
load_dotenv()

# ---------------------------------------------------------
# 1. Cloud Secrets & Credentials Hydration (Error-Safe)
# ---------------------------------------------------------
try:
    if len(st.secrets) > 0 and "GROQ_API_KEY" in st.secrets:
        for key in ["GROQ_API_KEY", "PINECONE_API_KEY", "PINECONE_INDEX_NAME", "GITHUB_PERSONAL_ACCESS_TOKEN"]:
            if key in st.secrets:
                os.environ[key] = st.secrets[key]

        if "GOOGLE_CREDENTIALS_JSON" in st.secrets and not os.path.exists("credentials.json"):
            with open("credentials.json", "w") as f:
                f.write(st.secrets["GOOGLE_CREDENTIALS_JSON"])

        if "GOOGLE_TOKEN_JSON" in st.secrets and not os.path.exists("token.json"):
            with open("token.json", "w") as f:
                f.write(st.secrets["GOOGLE_TOKEN_JSON"])
except Exception:
    # Local environment mein secrets.toml na ho toh ignore karke .env use karega
    pass

# ---------------------------------------------------------
# 2. Imports & Workflow Loading
# ---------------------------------------------------------
from langchain_core.messages import HumanMessage, AIMessage, ToolMessage
from graph.workflow import build_graph

# ---------------------------------------------------------
# 3. Page Configuration & Company Branding Setup
# ---------------------------------------------------------
COMPANY_NAME = "SMIT LangGraph Agent"
TAGLINE = "Enterprise Autonomous Multi-Agent Orchestrator"
COMPANY_LOGO_ICON = "⚡"

st.set_page_config(
    page_title=f"{COMPANY_NAME} | Multi-Agent Hub",
    page_icon=COMPANY_LOGO_ICON,
    layout="wide",
    initial_sidebar_state="expanded"
)

# ---------------------------------------------------------
# 4. Custom Styling (Modern Dark Theme Look)
# ---------------------------------------------------------
st.markdown("""
<style>
    .brand-header {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 24px 28px;
        margin-bottom: 24px;
        color: white;
    }
    .brand-title {
        font-size: 1.85rem;
        font-weight: 700;
        margin: 0;
        letter-spacing: -0.5px;
    }
    .brand-tagline {
        color: #94A3B8;
        font-size: 0.95rem;
        margin-top: 6px;
        margin-bottom: 0;
    }
    .badge-container {
        display: flex;
        gap: 8px;
        margin-top: 14px;
        flex-wrap: wrap;
    }
    .subagent-pill {
        display: inline-block;
        padding: 4px 10px;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.3px;
        border: 1px solid rgba(255, 255, 255, 0.1);
    }
    .pill-rag { background-color: rgba(56, 189, 248, 0.15); color: #38BDF8; }
    .pill-github { background-color: rgba(192, 132, 252, 0.15); color: #C084FC; }
    .pill-google { background-color: rgba(74, 222, 128, 0.15); color: #4ADE80; }
    .stChatInput {
        border-radius: 16px;
    }
</style>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 5. Initialize LangGraph State Machine
# ---------------------------------------------------------
@st.cache_resource
def get_graph():
    return build_graph()

graph = get_graph()

# Session State for Messages
if "messages" not in st.session_state:
    st.session_state.messages = []

# ---------------------------------------------------------
# 6. Export Helpers (Markdown & JSON)
# ---------------------------------------------------------
def prepare_export_markdown(messages):
    lines = [
        f"# {COMPANY_NAME} - Chat Session Export",
        f"**Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"**Orchestrator System:** LangGraph Multi-Agent",
        "\n---\n"
    ]
    for msg in messages:
        role = "User" if isinstance(msg, HumanMessage) else "Assistant (Supervisor)"
        lines.append(f"### {role}\n{msg.content}\n")
    return "\n".join(lines)

def prepare_export_json(messages):
    payload = {
        "company": COMPANY_NAME,
        "exported_at": datetime.now().isoformat(),
        "total_messages": len(messages),
        "history": [
            {
                "role": "user" if isinstance(m, HumanMessage) else "assistant",
                "content": m.content
            }
            for m in messages
        ]
    }
    return json.dumps(payload, indent=2)

# ---------------------------------------------------------
# 7. Sidebar Controls, Status & Downloads
# ---------------------------------------------------------
with st.sidebar:
    st.markdown(f"### {COMPANY_LOGO_ICON} {COMPANY_NAME}")
    st.caption("Agent Orchestration Management")

    st.subheader("Sub-Agents Status")
    st.success("🟢 Pinecone Vector RAG")
    st.success("🟢 GitHub Live REST API")
    st.success("🟢 Google Workspace API")
    
    st.divider()
    st.subheader("⚡ Quick Prompts")
    if st.button("📅 Upcoming Meetings", use_container_width=True):
        st.session_state.preset_prompt = "Google Calendar ke aane wale meetings check karke batao."
    if st.button("🐙 Fetch GitHub Issues", use_container_width=True):
        st.session_state.preset_prompt = "GitHub repository 'psf/requests' ke open issues check karo."
    if st.button("📄 RAG Document Query", use_container_width=True):
        st.session_state.preset_prompt = "Document (PDF) ke mutabiq policy details batao."

    st.divider()
    st.subheader("💾 Export & Session")
    
    if st.session_state.messages:
        md_data = prepare_export_markdown(st.session_state.messages)
        json_data = prepare_export_json(st.session_state.messages)
        timestamp_slug = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        st.download_button(
            label="📥 Download Chat (.MD)",
            data=md_data,
            file_name=f"chat_export_{timestamp_slug}.md",
            mime="text/markdown",
            use_container_width=True
        )
        st.download_button(
            label="📦 Download Chat (.JSON)",
            data=json_data,
            file_name=f"chat_export_{timestamp_slug}.json",
            mime="application/json",
            use_container_width=True
        )
    else:
        st.caption("Export buttons activate once messages are sent.")

    if st.button("🗑️️ Clear Session", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

# ---------------------------------------------------------
# 8. Main Workspace Hero Header
# ---------------------------------------------------------
st.markdown(f"""
<div class="brand-header">
    <div class="brand-title">{COMPANY_LOGO_ICON} {COMPANY_NAME}</div>
    <div class="brand-tagline">{TAGLINE}</div>
    <div class="badge-container">
        <span class="subagent-pill pill-rag">Hosted Pinecone RAG</span>
        <span class="subagent-pill pill-github">Live GitHub API</span>
        <span class="subagent-pill pill-google">Google Workspace OAuth 2.0</span>
    </div>
</div>
""", unsafe_allow_html=True)

# ---------------------------------------------------------
# 9. Render Chat History
# ---------------------------------------------------------
for msg in st.session_state.messages:
    role = "user" if isinstance(msg, HumanMessage) else "assistant"
    with st.chat_message(role):
        st.markdown(msg.content)

# ---------------------------------------------------------
# 10. User Input & Streaming Orchestration
# ---------------------------------------------------------
user_query = st.chat_input("Ask a question, query code repositories, or manage your schedule...")

if "preset_prompt" in st.session_state and st.session_state.preset_prompt:
    user_query = st.session_state.preset_prompt
    st.session_state.preset_prompt = None

if user_query:
    st.session_state.messages.append(HumanMessage(content=user_query))
    with st.chat_message("user"):
        st.markdown(user_query)

    with st.chat_message("assistant"):
        with st.status("Coordinating sub-agents...", expanded=True) as status:
            final_content = ""
            state_input = {"messages": st.session_state.messages}
            
            try:
                for event in graph.stream(state_input, stream_mode="values"):
                    last_msg = event["messages"][-1]
                    
                    if isinstance(last_msg, AIMessage) and last_msg.tool_calls:
                        for tool in last_msg.tool_calls:
                            t_name = tool.get('name', 'tool')
                            status.write(f"⚡ **Sub-agent invoked:** `{t_name}`")
                            
                    elif isinstance(last_msg, ToolMessage):
                        status.write("📥 Successfully received payload from external agent...")
                        
                    elif isinstance(last_msg, AIMessage) and last_msg.content:
                        final_content = last_msg.content
                        
                status.update(label="All agent tasks completed!", state="complete", expanded=False)
                st.markdown(final_content)
                st.session_state.messages.append(AIMessage(content=final_content))
                st.rerun()
                
            except Exception as e:
                status.update(label="Agent Coordination Error", state="error")
                st.error(f"Error executing agent workflow: {str(e)}")