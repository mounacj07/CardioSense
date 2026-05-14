from ml import predict_disease
from genai import generate_advice

user_data = {
    "age": 45,
    "bp": 150,
    "cholesterol": 240,
    "heart_rate": 95
}

prediction = predict_disease(user_data)

result = generate_advice(user_data, prediction)

print("\n--- FINAL OUTPUT ---\n")
print(result)