import json
import re
import ollama

def verify_claims(advice, evidence_list):
    """
    Checks the generated advice against retrieved evidence.
    Returns:
    {
        "grounded": bool,
        "grounding_score": float,
        "verified_claims": int,
        "unsupported_claims": int,
        "flagged_claims": ["claim1", "claim2"]
    }
    """
    if not evidence_list:
        return {
            "grounded": False,
            "grounding_score": 0.0,
            "verified_claims": 0,
            "unsupported_claims": 1,
            "flagged_claims": ["All claims are unverified due to missing evidence."]
        }
        
    evidence_text = "\n".join([e["content"] for e in evidence_list])
    
    prompt = f"""
You are a strict medical hallucination checker. 
Your job is to verify if the claims in the 'Generated Advice' are fully supported by the 'Retrieved Evidence'.

Retrieved Evidence:
{evidence_text}

Generated Advice:
{advice}

Instructions:
1. Extract the main medical or health claims from the advice.
2. For each claim, check if it is explicitly supported by the evidence.
3. If a claim is NOT supported, flag it as unsupported.
4. You MUST output your final answer as valid JSON only, exactly matching this format, with no markdown formatting or extra text outside the JSON:
{{
  "claims": [
    {{"claim": "Drink 8 glasses of water", "supported": false}},
    {{"claim": "Blood pressure above 140/90 is high", "supported": true}}
  ]
}}
"""
    try:
        response = ollama.chat(
            model='llama3.2:1b',
            messages=[{'role': 'user', 'content': prompt}],
            options={"temperature": 0.0}
        )
        
        result_text = response['message']['content']
        # Try to parse JSON from the response
        # Using a regex to extract JSON in case the model added markdown like ```json ... ```
        match = re.search(r'\{.*\}', result_text, re.DOTALL)
        if match:
            parsed = json.loads(match.group(0))
        else:
            parsed = json.loads(result_text)
            
        claims = parsed.get("claims", [])
        
        verified_count = sum(1 for c in claims if c.get("supported"))
        total_claims = len(claims)
        unsupported_count = total_claims - verified_count
        flagged_claims = [c.get("claim") for c in claims if not c.get("supported")]
        
        grounding_score = verified_count / total_claims if total_claims > 0 else 1.0
        
        return {
            "grounded": unsupported_count == 0,
            "grounding_score": grounding_score,
            "verified_claims": verified_count,
            "unsupported_claims": unsupported_count,
            "flagged_claims": flagged_claims
        }
        
    except Exception as e:
        print(f"Error in verification: {e}")
        # Fail safe
        return {
            "grounded": False,
            "grounding_score": 0.0,
            "verified_claims": 0,
            "unsupported_claims": 1,
            "flagged_claims": ["Error verifying claims. Considered unverified."]
        }
