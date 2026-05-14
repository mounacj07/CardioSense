import ollama

def analyze_health(data):
    issues = []

    if data["bp"] > 140:
        issues.append("high blood pressure")
    if data["cholesterol"] > 200:
        issues.append("high cholesterol")
    if data["heart_rate"] > 100:
        issues.append("elevated heart rate")

    return issues


def generate_advice(data, prediction):
    issues = analyze_health(data)

    risk_text = "at risk of heart disease" if prediction == 1 else "currently at low risk"

    prompt = f"""
You are a calm and helpful health assistant.

User Details:
- Age: {data['age']}
- Blood Pressure: {data['bp']}
- Cholesterol: {data['cholesterol']}
- Heart Rate: {data['heart_rate']}

Health Status: {risk_text}

Key Concerns: {", ".join(issues) if issues else "none"}

Instructions:
- Give clear and practical advice
- If at risk → focus on prevention
- If low risk → focus on maintaining health
- Mention specific improvements
- Keep response under 120 words
- Do NOT diagnose diseases

Format:
🩺 Health Insight:
...
💡 Advice:
- ...
⚠️ Note:
...

Generate response:
"""

    response = ollama.chat(
        model='llama3',
        messages=[{'role': 'user', 'content': prompt}]
    )

    return response['message']['content']