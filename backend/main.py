# In app startup / before serving
from backend.rag.retriever import get_retriever
from backend.ml.inference import load_models
import ollama

# Pre-warm everything
load_models()
get_retriever()
ollama.chat(model='llama3.2:1b', messages=[{'role': 'user', 'content': 'ping'}])

from fastapi import FastAPI
from pydantic import BaseModel
from backend.agents.workflow import run_agentic_workflow

app = FastAPI(title="Agentic RAG Healthcare Assistant API")

class PatientData(BaseModel):
    age: int
    sex: int              # 1 = Male, 0 = Female
    chest_pain: int       # 1=typical angina, 2=atypical, 3=non-anginal, 4=asymptomatic
    bp: int
    cholesterol: int
    high_blood_sugar: int # 1 = fasting blood sugar > 120 mg/dL, else 0
    exercise_chest_pain: int  # 1 = yes, 0 = no


@app.post("/analyze")
def analyze_patient(data: PatientData):
    user_data = data.model_dump()
    result = run_agentic_workflow(user_data)
    return result

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
