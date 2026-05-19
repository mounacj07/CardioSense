import os
import glob
from langchain_community.document_loaders import TextLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

def index_knowledge_base():
    base_dir = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    kb_dir = os.path.join(base_dir, "knowledge_base")
    vectorstore_dir = os.path.join(base_dir, "vectorstore")

    print("Loading documents from:", kb_dir)
    documents = []
    
    # Load txt files
    for filepath in glob.glob(os.path.join(kb_dir, "*.txt")):
        loader = TextLoader(filepath)
        documents.extend(loader.load())

    if not documents:
        print("No documents found to index.")
        return

    print(f"Loaded {len(documents)} documents. Chunking...")
    
    text_splitter = RecursiveCharacterTextSplitter(
        chunk_size=500,
        chunk_overlap=50,
        separators=["\n\n", "\n", "- ", " ", ""]
    )
    chunks = text_splitter.split_documents(documents)
    
    print(f"Created {len(chunks)} chunks. Embedding into ChromaDB...")
    
    # Use sentence-transformers
    embeddings = HuggingFaceEmbeddings(model_name="all-MiniLM-L6-v2")
    
    # Create or update vectorstore
    vectorstore = Chroma.from_documents(
        documents=chunks,
        embedding=embeddings,
        persist_directory=vectorstore_dir
    )
    
    print(f"Successfully indexed and persisted to {vectorstore_dir}")

if __name__ == "__main__":
    index_knowledge_base()
