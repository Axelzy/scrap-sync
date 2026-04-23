import os
import json
import requests
from dotenv import load_dotenv

load_dotenv()

class GLAIEngine:
    def __init__(self):
        """Initializes the live connection to the Z.AI / ilmu.ai API."""
        self.api_url = os.environ.get("ZAI_API_URL") 
        self.api_key = os.environ.get("ZAI_API_KEY")

    def analyze_and_match(self, raw_ocr_text: str, buyers_list: list) -> dict:
        """
        Sends the messy OCR text and the Supabase buyer list to the AI for live analysis.
        """
        if not self.api_key or not self.api_url:
            return {"error": "Critical: API credentials missing from .env file."}

        # --- REINFORCEMENT: TRUNCATION ---
        # Limits the text size to prevent the model from hanging on messy OCR
        raw_ocr_text = raw_ocr_text[:3000]

        # --- THE SYSTEM PROMPT ---
        system_prompt = f"""
        You are 'ScrapSync', an elite industrial waste broker. 
        Read this unstructured OCR text: "{raw_ocr_text}"
        Match it against these available buyers: {json.dumps(buyers_list, indent=2)}

        You MUST respond STRICTLY in JSON format with no markdown formatting or extra conversational text. 
        Use this exact schema:
        {{
            "material_detected": "string",
            "quantity_detected": "string or 'Unknown'",
            "best_buyer_match": "Company Name",
            "reasoning": "A 2-sentence explanation of why this is the best match.",
            "estimated_profit_myr": "Calculate the exact profit by multiplying the detected quantity by the buyer's offered price per unit. If quantity is unknown, output the buyer's max budget."
        }}
        """

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

        # NOTE: Using the UM Hackathon provisioned model
        payload = {
            "model": "ilmu-glm-5.1", 
            "messages": [{"role": "system", "content": system_prompt}],
            "temperature": 0.2 
        }

        try:
            # --- REINFORCEMENT: TIMEOUT ---
            # Set to 60s to give the AI enough time to handle complex matching
            response = requests.post(self.api_url, headers=headers, json=payload, timeout=60)
            response.raise_for_status()
            
            # Extract the AI's answer
            ai_message = response.json()["choices"][0]["message"]["content"]
            
            # Clean up the response to ensure it is pure JSON
            ai_message = ai_message.replace("```json", "").replace("```", "").strip()
            
            return json.loads(ai_message)

        except requests.exceptions.Timeout:
            return {"error": "The AI took too long to respond (504 Timeout). The server might be busy. Please try again in a few seconds."}
        except Exception as e:
            return {"error": f"Failed to communicate with the AI API: {str(e)}"}