# Agentic RAG Healthcare Assistant

An explainable AI healthcare copilot that predicts heart disease risk, retrieves medical evidence, generates advice, verifies its own outputs for hallucinations, and visibly warns users when claims are unsupported.

## 🚀 Quick Start

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Setup External Services
Make sure you have Ollama installed and the `llama3` model pulled:
```bash
ollama run llama3
```

### 3. Initialize ML & RAG
Train the ML model and create the vector database:
```bash
# Train ML model and save it
python -m backend.ml.train

# Index the knowledge base into ChromaDB
python -m backend.rag.indexer
```

### 4. Run the Backend API
Start the FastAPI orchestration server:
```bash
python -m backend.main
```
The API will run on `http://localhost:8000`.

### 5. Run the Frontend Dashboard
In a new terminal window, start the Streamlit UI:
```bash
streamlit run frontend/app.py
```
This will open the premium UI in your browser.

## 📁 Project Structure

- `backend/ml/`: Model training and inference.
- `backend/rag/`: Document indexing and retrieval.
- `backend/agents/`: Orchestration workflow (Prediction -> RAG -> Generation -> Verification).
- `backend/grounding/`: Hallucination checker checking advice against evidence.
- `frontend/`: Premium Streamlit dashboard.
- `knowledge_base/`: Place your PDFs or text medical guidelines here.
