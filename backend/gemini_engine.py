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
        
        # We use 2.5 Flash as it is incredibly fast and perfect for OCR + JSON tasks
        self.model = genai.GenerativeModel('gemini-2.5-flash')

    def analyze_and_match(self, image_bytes: bytes, buyers_list: list) -> dict:
        """
        Sends the raw image directly to Gemini, bypassing traditional OCR entirely.
        This uses the Bulletproof Prompt to ensure strict Net Profit routing.
        """
        if not self.api_key:
            return {"error": "Critical: GEMINI_API_KEY missing from .env file."}

        try:
            # Convert the raw bytes from FastAPI into a PIL Image for Gemini
            image = Image.open(io.BytesIO(image_bytes))

            # --- THE BULLETPROOF SYSTEM PROMPT ---
            system_prompt = f"""
            You are 'ScrapSync', an elite industrial waste broker. 
            Analyze the attached image (it is an unstructured receipt, log, or manifest).
            Match the materials found in the image against these available buyers: {json.dumps(buyers_list, indent=2)}

            Important Rules for Decision Making (You MUST follow these in order):
            1. AGGREGATE: If there are multiple items of the SAME material, SUM their weights together to get the Total Quantity in kg.
            2. CALCULATE ALL: For EVERY buyer in the database that accepts this material, you MUST calculate their specific Net Profit using this exact formula:
               - Gross Revenue = (Total Quantity in kg * max_price_myr)
               - Trucks Needed = Round up (Total Quantity in kg / 1000)
               - Transport Cost = (distance_km * RM 1.50 * Trucks Needed)
               - Net Profit = Gross Revenue - Transport Cost
            3. SELECT THE WINNER: Compare the Net Profit of all valid buyers. You MUST set the 'best_buyer_match' to the company that yields the absolute highest Net Profit.

            CRITICAL: The `max_price_myr` in the database is the price PER KG. Even if the price seems unusually high, you MUST perform a direct, literal multiplication (Quantity * max_price_myr) to calculate Gross Revenue. Do NOT assume it is per tonne and do NOT divide the quantity by 1000 for revenue calculation.

            You MUST respond STRICTLY in JSON format using this exact schema:
            {{
                "material_detected": "string (summarize the main materials)",
                "quantity_detected": "string (e.g., '1000.0 kg')",
                "best_buyer_match": "Company Name",
                "reasoning": "You must show your math. Write a detailed 4-to-5 sentence breakdown comparing the top two options. Example: 'Company A offered a higher raw price generating RM 400 gross, but their 260km distance resulted in a RM 390 transport cost (Net: RM 10). Company B offered a lower raw price but is only 45km away (Net: RM 212.50). Therefore, Company B is the most profitable route.'",
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

    def find_cheapest_supplier(self, search_query: str, volume_kg: float, supply_list: list) -> dict:
        """
        Finds the lowest Total Landed Cost for purchasing materials.
        (Used for the AI Procurement Console)
        """
        if not self.api_key:
            return {"error": "Critical: GEMINI_API_KEY missing from .env file."}
            
        try:
            system_prompt = f"""
            You are ScrapSync's AI Procurement Officer. 
            The user wants to BUY {volume_kg} kg of: '{search_query}'.
            Here are the available suppliers: {json.dumps(supply_list, indent=2)}

            Important Rules for Decision Making:
            1. For EVERY supplier that matches the requested material, calculate their specific Total Landed Cost:
               - Material Cost = ({volume_kg} * price_per_kg_myr)
               - Trucks Needed = Round up ({volume_kg} / 1000)
               - Transport Cost = (distance_km * RM 1.50 * Trucks Needed)
               - Total Landed Cost = Material Cost + Transport Cost

            CRITICAL: The `price_per_kg_myr` in the database is the price PER KG. Even if the price seems unusually high, you MUST perform a direct, literal multiplication (volume * price_per_kg_myr) to calculate Material Cost. Do NOT assume it is per tonne and do NOT divide the quantity by 1000 for material cost calculation.

            You MUST respond STRICTLY in JSON format using this exact schema:
            {{
                "best_supplier": "Company Name",
                "total_landed_cost_myr": "String formatted exactly like 'RM 1,250.00'",
                "material_cost_myr": "String (e.g. 'RM 1,000.00')",
                "transport_cost_myr": "String (e.g. 'RM 250.00')",
                "reasoning": "A 5-sentence explanation in details of why this is the best match."
            }}
            """

            response = self.model.generate_content(
                system_prompt,
                generation_config=genai.GenerationConfig(
                    response_mime_type="application/json", 
                    temperature=0.1
                )
            )
            
            return json.loads(response.text)
            
        except Exception as e:
            return {"error": f"Failed to communicate with the Gemini API: {str(e)}"}