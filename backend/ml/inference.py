import joblib
import os
import pandas as pd

# Load model and scaler lazily
_model = None
_scaler = None

def load_models():
    global _model, _scaler
    if _model is None or _scaler is None:
        model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
        model_path = os.path.join(model_dir, "rf_model.joblib")
        scaler_path = os.path.join(model_dir, "scaler.joblib")
        
        if not os.path.exists(model_path) or not os.path.exists(scaler_path):
            raise FileNotFoundError("Model files not found. Please run backend/ml/train.py first.")
            
        _model = joblib.load(model_path)
        _scaler = joblib.load(scaler_path)
        
def predict_disease(user_data):
    """
    Takes a dict with keys: age, sex, chest_pain, bp, cholesterol, high_blood_sugar, exercise_chest_pain
    Returns: { "prediction": 0/1, "confidence": float, "probabilities": list }
    """
    load_models()

    FEATURES = ['age', 'sex', 'chest_pain', 'bp', 'cholesterol', 'high_blood_sugar', 'exercise_chest_pain']
    input_df = pd.DataFrame([{k: user_data[k] for k in FEATURES}])
    input_scaled = _scaler.transform(input_df)

    prediction    = int(_model.predict(input_scaled)[0])
    probabilities = _model.predict_proba(input_scaled)[0].tolist()
    confidence    = probabilities[prediction]

    return {
        "prediction":    prediction,
        "confidence":    confidence,
        "probabilities": probabilities
    }
