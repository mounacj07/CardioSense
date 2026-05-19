import time
import ollama
from backend.ml.inference import predict_disease
from backend.rag.retriever import retrieve_evidence

def run_agentic_workflow(user_data):
    trace = []

    def log_step(name, status, summary, details=None):
        trace.append({
            "step": name,
            "timestamp": time.strftime("%H:%M:%S"),
            "status": status,
            "summary": summary,
            "details": details or {}
        })

    # ── Step 1: ML Prediction ──────────────────────────────
    log_step("ML Prediction", "Running", "Starting prediction...")
    try:
        prediction_result = predict_disease(user_data)
        ml_label = "High Risk" if prediction_result["prediction"] == 1 else "Low Risk"
        log_step("ML Prediction", "Success", f"ML predicted: {ml_label}", prediction_result)
    except Exception as e:
        log_step("ML Prediction", "Failed", str(e))
        return {"error": "ML Prediction failed", "trace": trace}

    # ── Step 2: Clinical Flags ─────────────────────────────
    # Evaluate known risk factors the model may underweight
    clinical_flags = []

    if user_data.get("high_blood_sugar"):
        clinical_flags.append({
            "level": "warning",
            "text": "Elevated fasting blood sugar — a known cardiovascular risk factor. Consider diabetes screening."
        })
    if user_data.get("bp", 0) >= 130:
        clinical_flags.append({
            "level": "warning",
            "text": f"Blood pressure {user_data['bp']} mmHg is elevated (≥130 mmHg is above normal per AHA guidelines)."
        })
    if user_data.get("cholesterol", 0) >= 240:
        clinical_flags.append({
            "level": "warning",
            "text": f"Cholesterol {user_data['cholesterol']} mg/dL is high (≥240 mg/dL = High per AHA guidelines)."
        })
    if user_data.get("chest_pain") == 1 and user_data.get("exercise_chest_pain"):
        clinical_flags.append({
            "level": "danger",
            "text": "Typical angina-type chest pain combined with exercise-induced chest pain is a significant cardiac warning sign. Seek medical evaluation promptly."
        })
    if user_data.get("age", 0) >= 55 and user_data.get("sex") == 1:
        clinical_flags.append({
            "level": "info",
            "text": "Men aged 55+ have statistically higher cardiovascular risk. Regular checkups are strongly recommended."
        })

    # ── Step 3: Adjusted Risk Score ────────────────────────
    # Score flags: danger=2pts, warning=1pt, info=0pts
    flag_score = sum(2 if f["level"] == "danger" else (1 if f["level"] == "warning" else 0)
                     for f in clinical_flags)

    if ml_label == "High Risk":
        adjusted_label = "High Risk"
    elif flag_score >= 3:
        adjusted_label = "High Risk"
    elif flag_score >= 1:
        adjusted_label = "Moderate Risk"
    else:
        adjusted_label = "Low Risk"

    log_step("Risk Adjustment", "Success",
             f"ML={ml_label} | Flag score={flag_score} → Final={adjusted_label}",
             {"ml_label": ml_label, "flag_score": flag_score, "adjusted_label": adjusted_label})

    # ── Step 4: Evidence Retrieval ─────────────────────────
    log_step("Evidence Retrieval", "Running", "Fetching relevant medical guidelines...")
    query = f"Heart disease prevention, blood pressure {user_data['bp']}, cholesterol {user_data['cholesterol']}"
    evidence = []
    try:
        evidence = retrieve_evidence(query)
        log_step("Evidence Retrieval", "Success", f"Retrieved {len(evidence)} document chunks.", {"chunks": evidence})
    except Exception as e:
        log_step("Evidence Retrieval", "Failed", str(e))

    # ── Step 5: LLM Advice Generation ─────────────────────
    log_step("Advice Generation", "Running", "Generating personalised advice...")
    evidence_text = "\n\n".join(f"Source ({e['source']}):\n{e['content']}" for e in evidence) \
        if evidence else "No specific evidence retrieved."

    tone_map = {
        "High Risk":     "objective, precise, and professional. State risks and outline necessary lifestyle modifications clearly.",
        "Moderate Risk": "objective, professional, and educational. Focus on healthy habits to manage risk factors.",
        "Low Risk":      "objective, professional, and informative. Emphasize maintaining healthy patterns and managing any borderline levels."
    }

    flag_summary = ""
    if clinical_flags:
        flag_summary = "\nClinical risk flags to address in the advice:\n" + \
                       "\n".join(f"- {f['text']}" for f in clinical_flags if f["level"] != "info")

    prompt = f"""You are CardioSense AI, a professional, objective, and empathetic clinical AI assistant. You are writing a clear, patient-centric health summary based on clinical data.

Patient profile:
- Age: {user_data['age']}, Sex: {'Male' if user_data['sex'] == 1 else 'Female'}
- Resting Blood Pressure: {user_data['bp']} mmHg
- Cholesterol Level: {user_data['cholesterol']} mg/dL
- Fasting Glucose elevated: {'Yes' if user_data['high_blood_sugar'] else 'No'}
- Symptoms / Chest discomfort: {['', 'Discomfort during activity', 'Atypical discomfort', 'Non-cardiac chest pressure', 'No physical discomfort'][user_data['chest_pain']]}
- Activity-induced discomfort: {'Yes' if user_data['exercise_chest_pain'] else 'No'}

Overall Cardiovascular Risk Category: {adjusted_label}
Approach: Be {tone_map[adjusted_label]}.
{flag_summary}

Clinical guidelines for reference:
{evidence_text}

=== STYLE ===
- Tone: Highly professional, formal, and objective.
- Phrasing: Use precise clinical language suitable for a medical report.
- Structure: Clear, patient-focused guidance.

Provide:

Health Insight: State the overall cardiovascular risk category ({adjusted_label}) based on the clinical data. Add 1-2 objective, formal sentences explaining the clinical relevance of the patient's vitals (including blood pressure and cholesterol) in a professional manner.

Actionable Advice:
1. (practical, clinically backed lifestyle recommendation addressing the risk category or specific vital values)
2. (practical nutritional or dietary tip based on guidelines)
3. (practical exercise or stress reduction tip based on guidelines)"""

    try:
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{'role': 'user', 'content': prompt}]
        )
        advice = response['message']['content']
        log_step("Advice Generation", "Success", "Advice generated.", {"advice": advice})
    except Exception as e:
        log_step("Advice Generation", "Failed", str(e))
        return {"error": "LLM Generation failed", "trace": trace}

    return {
        "prediction": {**prediction_result, "adjusted_label": adjusted_label, "ml_label": ml_label},
        "evidence": evidence,
        "advice": advice,
        "clinical_flags": clinical_flags,
        "trace": trace
    }
