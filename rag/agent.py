import os
import io
from dotenv import load_dotenv
from pinecone import Pinecone
from pypdf import PdfReader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.tools import tool

load_dotenv()

PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX_NAME = os.getenv("PINECONE_INDEX_NAME", "langgraph-rag-1024")

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX_NAME)


def process_and_index_pdf(file_bytes, filename="uploaded_doc.pdf"):
    """PDF file ko read karke Pinecone memory mein store karta hai."""
    try:
        reader = PdfReader(io.BytesIO(file_bytes))
        raw_text = ""
        for page_num, page in enumerate(reader.pages):
            text = page.extract_text()
            if text:
                raw_text += f"\n--- Page {page_num + 1} ---\n" + text

        if not raw_text.strip():
            return False, "PDF se text extract nahi ho saka (ho sakta hai scanned image ho)."

        splitter = RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100)
        chunks = splitter.split_text(raw_text)

        embeddings = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=chunks,
            parameters={"input_type": "passage", "truncate": "END"}
        )

        records = []
        for i, (chunk, emb) in enumerate(zip(chunks, embeddings)):
            records.append({
                "id": f"doc_{filename}_{i}",
                "values": emb.values,
                "metadata": {
                    "text": chunk,
                    "source": filename
                }
            })

        index.upsert(vectors=records)
        return True, f"Successfully indexed {len(records)} chunks from {filename} into memory!"
    except Exception as e:
        return False, f"Indexing error: {str(e)}"


@tool
def query_hosted_pdf_knowledge_base(query: str) -> str:
    """PDF documents, policies, ya knowledge base se mutaliq sawalon ke jawab dhoondne ke liye use karein."""
    try:
        query_emb = pc.inference.embed(
            model="multilingual-e5-large",
            inputs=[query],
            parameters={"input_type": "query"}
        )
        
        results = index.query(
            vector=query_emb[0].values,
            top_k=4,
            include_metadata=True
        )

        contexts = [
            match["metadata"]["text"] 
            for match in results.get("matches", []) 
            if "metadata" in match and "text" in match["metadata"]
        ]
        
        if not contexts:
            return "Knowledge base mein is query se related koi specific information nahi mili."

        return "\n\n---\n\n".join(contexts)
    except Exception as e:
        return f"Error querying vector knowledge base: {str(e)}"


# Backward compatibility ke liye alias
query_knowledge_base = query_hosted_pdf_knowledge_base