import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class GLAIEngine:
    def __init__(self):
        """Initializes the connection to the Z.AI GLM API."""
        self.api_url = os.environ.get("ZAI_API_URL", "https://api.z.ai/v1/chat/completions") 
        self.api_key = os.environ.get("ZAI_API_KEY")

    def analyze_and_match(self, raw_ocr_text: str, buyers_list: list) -> dict:
        """
        Sends the messy text to the GLM. If no API key exists, it returns a Mock result 
        so the frontend team isn't blocked.
        """
        # --- MOCK MODE (For Local Testing without an API Key) ---
        if not self.api_key or self.api_key == "1f6f12ed961c4664b60573ce2a940a96.RztcLgrw8GVuYcLN" or self.api_key == "":
            print("\n⚠️ MOCK MODE ACTIVATED: No real Z.AI API key found.")
            print("Returning simulated AI response for frontend testing...\n")
            
            # This is exactly what the real AI will eventually output
            return {
                "material_detected": "Untreated Wood Dust (Meranti)",
                "quantity_detected": "Unknown (Estimated Bulk)",
                "best_buyer_match": "Aisha Fungi Farms",
                "reasoning": "Aisha Fungi Farms specifically requires wood dust for agricultural substrate in Selangor and has a budget of RM1500, making this a highly profitable synergy.",
                "estimated_profit_myr": "RM 800.00"
            }

        # --- REAL PRODUCTION MODE (Runs when you get your hackathon key) ---
        system_prompt = f"""
        You are 'ScrapSync', an elite industrial waste broker. 
        Read this unstructured OCR text: "{raw_ocr_text}"
        Match it against these buyers: {json.dumps(buyers_list, indent=2)}

        You MUST respond STRICTLY in JSON format:
        {{
            "material_detected": "string",
            "quantity_detected": "string or 'Unknown'",
            "best_buyer_match": "Company Name",
            "reasoning": "A 2-sentence explanation of why this is the best match.",
            "estimated_profit_myr": "Calculate an estimate based on the buyer's max budget"
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "glm-4", 
            "messages": [{"role": "system", "content": system_prompt}],
            "temperature": 0.2 
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=payload)
            response.raise_for_status()
            ai_message = response.json()["choices"][0]["message"]["content"]
            ai_message = ai_message.replace("```json", "").replace("```", "").strip()
            return json.loads(ai_message)

        except Exception as e:
            return {"error": f"Failed to communicate with Z.AI: {str(e)}"}