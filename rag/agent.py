import os
from langchain_core.tools import tool
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from pinecone import Pinecone

@tool
def query_hosted_pdf_knowledge_base(query: str) -> str:
    """Useful to answer questions from the hosted PDF knowledge base regarding company policies, reports, or rules."""
    try:
        pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
        index_name = os.getenv("PINECONE_INDEX_NAME", "langgraph-rag-1024")
        index = pc.Index(index_name)
        
        # Pinecone hosted embedding for the query
        res = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[query],
            parameters={"input_type": "query"}
        )
        query_vec = res[0].values
        
        results = index.query(vector=query_vec, top_k=2, include_metadata=True)
        
        if not results.get("matches"):
            return "Knowledge base mein is topic par koi information nahi mili."
            
        context_text = "\n\n".join(
            [m["metadata"]["text"] for m in results["matches"] if "metadata" in m and "text" in m["metadata"]]
        )
        
        llm = ChatGroq(
            model="qwen/qwen3.8-27b",
            temperature=0,
            max_tokens=400,
            api_key=os.getenv("GROQ_API_KEY")
        )
        
        prompt = ChatPromptTemplate.from_template(
            "Answer the question based only on the provided context:\n\n"
            "Context:\n{context}\n\n"
            "Question: {question}\n\n"
            "Answer clearly and concisely:"
        )
        
        chain = prompt | llm
        response = chain.invoke({"context": context_text, "question": query})
        return response.content
        
    except Exception as e:
        return f"Error querying knowledge base: {str(e)}"