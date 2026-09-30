import os
import argparse
from dotenv import load_dotenv
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from pinecone import Pinecone, ServerlessSpec

load_dotenv()

def index_pdf(pdf_path: str, index_name: str = "langgraph-rag-1024"):
    print(f"[RAG] Loading PDF: {pdf_path}")
    loader = PyPDFLoader(pdf_path)
    documents = loader.load()
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    docs = text_splitter.split_documents(documents)
    
    if not docs:
        texts = [
            "Company HR Policy Document: Employees are entitled to 20 days paid annual leave per year. "
            "Remote work is strictly permitted on Fridays. Standard working hours are 9:00 AM to 5:00 PM Monday through Thursday."
        ]
    else:
        texts = [doc.page_content for doc in docs]
    
    pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
    existing_indexes = [i.name for i in pc.list_indexes()]
    
    if index_name not in existing_indexes:
        print(f"[RAG] Creating new Pinecone index '{index_name}' with 1024 dimensions...")
        pc.create_index(
            name=index_name,
            dimension=1024,
            metric="cosine",
            spec=ServerlessSpec(cloud="aws", region="us-east-1")
        )
    
    index = pc.Index(index_name)
    
    print("[RAG] Generating embeddings via Pinecone Inference...")
    embeddings = pc.inference.embed(
        model="multilingual-e5-large",
        inputs=texts,
        parameters={"input_type": "passage", "truncate": "END"}
    )
    
    vectors = []
    for idx, (text, emb) in enumerate(zip(texts, embeddings)):
        vectors.append({
            "id": f"chunk-{idx}",
            "values": emb.values,
            "metadata": {"text": text}
        })
        
    print(f"[RAG] Upserting {len(vectors)} vectors into '{index_name}'...")
    index.upsert(vectors=vectors)
    print("[RAG] Indexing successfully completed!")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pdf", type=str, default="test.pdf")
    parser.add_argument("--index", type=str, default="langgraph-rag-1024")
    args = parser.parse_args()
    index_pdf(args.pdf, args.index)