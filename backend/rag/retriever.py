import os
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

_vectorstore = None

def get_retriever():
    global _vectorstore
    if _vectorstore is None:
        base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
        vectorstore_dir = os.path.join(base_dir, "vectorstore")
        
        embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
        
        _vectorstore = Chroma(
            persist_directory=vectorstore_dir,
            embedding_function=embeddings
        )
    return _vectorstore.as_retriever(search_kwargs={"k": 3})

def retrieve_evidence(query):
    """
    Returns a list of dictionaries with page_content and metadata (source)
    """
    retriever = get_retriever()
    docs = retriever.invoke(query)
    
    evidence = []
    for doc in docs:
        evidence.append({
            "content": doc.page_content,
            "source": os.path.basename(doc.metadata.get("source", "Unknown"))
        })
    return evidence
