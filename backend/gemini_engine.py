import os
import json
import io
from PIL import Image
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class GeminiEngine:
    def __init__(self):
        """Initializes the live connection to the Gemini API."""
        self.api_key = os.environ.get("GEMINI_API_KEY")
        if self.api_key:
            genai.configure(api_key=self.api_key)
        
        # We use 1.5 Flash as it is incredibly fast and perfect for OCR + JSON tasks
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_and_match(self, image_bytes: bytes, buyers_list: list) -> dict:
        """
        Sends the raw image directly to Gemini, bypassing traditional OCR entirely.
        """
        if not self.api_key:
            return {"error": "Critical: GEMINI_API_KEY missing from .env file."}

        try:
            # Convert the raw bytes from FastAPI into a PIL Image for Gemini
            image = Image.open(io.BytesIO(image_bytes))

            # --- THE SYSTEM PROMPT ---
            system_prompt = f"""
            You are 'ScrapSync', an elite industrial waste broker. 
            Analyze the attached image (it is an unstructured receipt, log, or manifest).
            Match the materials found in the image against these available buyers: {json.dumps(buyers_list, indent=2)}

            Important Rules:
            1. If there are multiple items of the SAME material (e.g., sawdust and wood shavings), SUM their weights together.
            2. Calculate profit by multiplying the total detected quantity by the buyer's offered price per unit.

            You MUST respond STRICTLY in JSON format using this exact schema:
            {{
                "material_detected": "string (summarize the main materials)",
                "quantity_detected": "string or 'Unknown'",
                "best_buyer_match": "Company Name",
                "reasoning": "A 2-sentence explanation of why this is the best match.",
                "estimated_profit_myr": "String formatted exactly like 'RM 150.00'."
            }}
            """

            # Send the request with STRICT JSON formatting enabled
            response = self.model.generate_content(
                [system_prompt, image],
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", 
                    temperature=0.1 # Low temperature for analytical accuracy
                )
            )

            # Gemini natively returns pure JSON because of the mime_type config
            return json.loads(response.text)

        except Exception as e:
            return {"error": f"Failed to communicate with the Gemini API: {str(e)}"}