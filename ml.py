import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, classification_report
 
df = pd.read_csv("heart_disease_uci.csv")
df = df.replace('?', pd.NA)
df = df.fillna(df.median(numeric_only=True))
 

X = df[['age', 'trestbps', 'chol', 'thalch']]
y = df['num'].apply(lambda x: 1 if x > 0 else 0) 
 
X.columns = ['age', 'bp', 'cholesterol', 'heart_rate']
 
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
 
scaler = StandardScaler()
X_train = scaler.fit_transform(X_train)
X_test  = scaler.transform(X_test)

lr = LogisticRegression()
lr.fit(X_train, y_train)
 
dt = DecisionTreeClassifier(max_depth=4, random_state=42)
dt.fit(X_train, y_train)

rf = RandomForestClassifier(n_estimators=100, random_state=42)
rf.fit(X_train, y_train)

knn = KNeighborsClassifier(n_neighbors=5)
knn.fit(X_train, y_train)
 
gb = GradientBoostingClassifier(n_estimators=100, random_state=42)
gb.fit(X_train, y_train)
 
models = {
    "Logistic Regression":   lr,
    "Decision Tree":         dt,
    "Random Forest":         rf,
    "K-Nearest Neighbors":   knn,
    "Gradient Boosting":     gb,
}
 
print("=" * 50)
print("        MODEL ACCURACY COMPARISON")
print("=" * 50)
for name, model in models.items():
    acc = accuracy_score(y_test, model.predict(X_test))
    print(f"  {name:<25} → {acc:.2%}")
print("=" * 50)

best_model = rf
print("\n Best Model selected: Random Forest")
print("\nDetailed Report (Random Forest):")
print(classification_report(y_test, best_model.predict(X_test)))
 
def predict_disease(user_data):
    """
    Takes a dict: {age, bp, cholesterol, heart_rate}
    Returns: 1 (at risk) or 0 (low risk)
    """
    input_df = pd.DataFrame([user_data])
    input_scaled = scaler.transform(input_df)

    prediction = best_model.predict(input_scaled)[0]
 
    return prediction