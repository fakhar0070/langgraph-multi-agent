# LangGraph Multi-Agent System (RAG + GitHub MCP + Google Workspace MCP)

Yeh project aik complete LangGraph based Multi-Agent System hai jisme 3 primary sub-agent components hain:
1. **RAG Sub-Agent**: Hosted Vector Store (Pinecone) se PDF documents retrieve karne ke liye.
2. **GitHub MCP Sub-Agent**: GitHub repositories, issues, PRs aur codebase se sawalat karne ke liye.
3. **Google Workspace MCP Sub-Agent**: Google Calendar (meetings parhna aur create karna) aur Gmail (emails draft karna aur auto send karna).

---

## 📁 Project Structure

```text
langgraph_multiagent_system/
├── requirements.txt         # Zaroori Python libraries
├── .env.example             # Environment variables ka template
├── README.md                # Complete setup guide
├── rag/
│   ├── __init__.py
│   ├── indexer.py          # PDF load karke Pinecone me upload karne ka script
│   └── agent.py            # RAG retriever tool definition
├── mcp_agents/
│   ├── __init__.py
│   ├── github_agent.py     # GitHub MCP integration & tools
│   └── google_agent.py     # Google Calendar & Gmail MCP tools
├── graph/
│   ├── __init__.py
│   ├── state.py            # LangGraph state schema
│   └── workflow.py         # Multi-agent graph / supervisor setup
└── main.py                 # Runner script aur CLI test interface
```

---

## 🚀 Setup & Installation Guide

### Step 1: Virtual Environment banayein aur dependencies install karein
```bash
# Python virtual environment
python -m venv venv

# Activate (Linux / Mac)
source venv/bin/activate

# Activate (Windows PowerShell)
venv\Scripts\activate

# Dependencies install karein
pip install -r requirements.txt
```

### Step 2: Environment Variables (.env) configure karein
`.env.example` file ko copy karke `.env` banayein:
```bash
cp .env.example .env
```
Aur apni actual API keys enter karein:
- **OPENAI_API_KEY**: OpenAI Platform se lein.
- **PINECONE_API_KEY**: Pinecone dashboard se lein.
- **PINECONE_INDEX_NAME**: Pinecone par banaye gaye index ka naam (e.g., `langgraph-rag`).
- **GITHUB_PERSONAL_ACCESS_TOKEN**: GitHub Developer Settings -> Personal Access Tokens (classic ya fine-grained).
- **GOOGLE_APPLICATION_CREDENTIALS**: Google Cloud Console se downloaded Service Account ya OAuth client JSON ka path.

---

## 📄 PDF Indexing (RAG Setup)

Apni kisi bhi PDF ko hosted Pinecone vector store me index karne ke liye:
```bash
python -m rag.indexer --pdf path/to/your/document.pdf
```
Yeh script automatically PDF ke chunks banakar Pinecone par embeddings upload kar dega.

---

## 🏃 Run the System

Main interactive agent chalane ke liye:
```bash
python main.py
```

### Sample Commands:
- **RAG**: *"PDF document ke mutabiq policy details kya hain?"*
- **GitHub**: *"Repository 'owner/repo' par latest PRs aur open issues check karo."*
- **Calendar & Gmail**: *"Kal dopahar 3 baje team meeting schedule karo aur uski confirmation email team@example.com ko draft kardo."*
