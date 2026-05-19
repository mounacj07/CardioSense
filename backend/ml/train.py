import pandas as pd
import joblib
import os
import numpy as np
from sklearn.model_selection import train_test_split, cross_val_score, StratifiedKFold
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, roc_auc_score

def train_model():
    print("Loading dataset...")
    data_path = "heart_disease_uci.csv"
    if not os.path.exists(data_path):
        data_path = os.path.join(os.path.dirname(__file__), "..", "..", "heart_disease_uci.csv")

    df = pd.read_csv(data_path)
    df = df.replace('?', pd.NA).fillna(df.median(numeric_only=True))

    # Encode categorical features
    df['sex_enc']   = df['sex'].map({'Male': 1, 'Female': 0}).fillna(0)
    cp_map = {'typical angina': 1, 'atypical angina': 2, 'non-anginal': 3, 'asymptomatic': 4}
    df['cp_enc']    = df['cp'].map(cp_map).fillna(3)
    df['fbs_enc']   = df['fbs'].astype(float).fillna(0)
    df['exang_enc'] = df['exang'].astype(float).fillna(0)

    X = df[['age', 'sex_enc', 'cp_enc', 'trestbps', 'chol', 'fbs_enc', 'exang_enc']].copy()
    X.columns = ['age', 'sex', 'chest_pain', 'bp', 'cholesterol', 'high_blood_sugar', 'exercise_chest_pain']
    y = df['num'].apply(lambda x: 1 if x > 0 else 0)

    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

    # Class weights to handle imbalance
    n_neg = (y_train == 0).sum()
    n_pos = (y_train == 1).sum()
    sample_weights = y_train.map({0: n_pos / (n_neg + n_pos), 1: n_neg / (n_neg + n_pos)}).values

    print("Scaling features...")
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s  = scaler.transform(X_test)

    print("Training Gradient Boosting model...")
    model = GradientBoostingClassifier(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=4,
        subsample=0.8,
        min_samples_leaf=10,
        random_state=42
    )
    model.fit(X_train_s, y_train, sample_weight=sample_weights)

    y_pred = model.predict(X_test_s)
    y_prob = model.predict_proba(X_test_s)[:, 1]

    print(f"\nTest Accuracy : {accuracy_score(y_test, y_pred):.2%}")
    print(f"Test ROC-AUC  : {roc_auc_score(y_test, y_prob):.2%}")
    print("\nDetailed Report:")
    print(classification_report(y_test, y_pred))

    # 5-fold CV
    cv = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    X_all = scaler.transform(X)
    cv_scores = cross_val_score(model, X_all, y, cv=cv, scoring='roc_auc')
    print(f"5-Fold ROC-AUC: {cv_scores.mean():.2%} (+/- {cv_scores.std():.2%})")

    # Feature importances
    print("\nFeature Importances:")
    for feat, imp in sorted(zip(X.columns, model.feature_importances_), key=lambda x: -x[1]):
        print(f"  {feat:<25} {imp:.3f}  {'#' * int(imp * 100)}")

    model_dir = os.path.join(os.path.dirname(__file__), "saved_models")
    os.makedirs(model_dir, exist_ok=True)
    joblib.dump(model, os.path.join(model_dir, "rf_model.joblib"))
    joblib.dump(scaler, os.path.join(model_dir, "scaler.joblib"))
    print("\nModel and scaler saved.")

if __name__ == "__main__":
    train_model()

