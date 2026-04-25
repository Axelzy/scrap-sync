from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz  # PyMuPDF
import io
import math
import re
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import our custom ScrapSync modules
from db_client import DatabaseManager
from gemini_engine import GeminiEngine # UPGRADE: Using the new Gemini engine

# --- INITIALIZE THE APPLICATION ---
app = FastAPI(title="ScrapSync API Engine")
db = DatabaseManager()
ai = GeminiEngine() # UPGRADE: Initialized Gemini

# --- HELPER FUNCTIONS ---
def convert_pdf_to_image(pdf_bytes: bytes) -> bytes:
    """
    Since Gemini loves images, if a user uploads a PDF, 
    we take a 'screenshot' of the first page to send to the AI.
    """
    try:
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        page = doc.load_page(0)  # Grab the first page
        pix = page.get_pixmap(dpi=150) # High enough resolution for Gemini to read
        return pix.tobytes("png") # Convert to standard PNG bytes
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF conversion failed: {str(e)}")

def extract_numeric_volume(volume_str: str) -> float:
    """Helper to safely extract raw numbers from AI's string output (e.g., '1000 kg' -> 1000.0)"""
    if not volume_str or str(volume_str).lower() == "unknown":
        return 0.0
    # Find all numbers (including commas and decimals)
    numbers = re.findall(r"[-+]?\d*\.\d+|\d+", str(volume_str).replace(',', ''))
    if numbers:
        return float(numbers[0])
    return 0.0

def calculate_logistics_and_profit(volume_kg: float, price_per_kg: float, distance_km: float) -> dict:
    """
    Calculates the true net profit factoring in distance, volume, and trucking logistics.
    """
    TRUCK_CAPACITY_KG = 1000.0  # 1-Ton Lorry
    RATE_PER_KM = 1.50          # Standard Malaysian trucking rate (RM)

    # 1. Calculate base revenue
    gross_revenue = volume_kg * price_per_kg

    # 2. Calculate logistics fleet needed
    trucks_needed = math.ceil(volume_kg / TRUCK_CAPACITY_KG)
    if trucks_needed == 0: 
        trucks_needed = 1  
    
    # 3. Calculate transport cost based on distance AND fleet size
    total_transport_cost = distance_km * RATE_PER_KM * trucks_needed

    # 4. The Final Bottom Line
    net_profit = gross_revenue - total_transport_cost

    return {
        "gross_revenue": round(gross_revenue, 2),
        "transport_cost": round(total_transport_cost, 2),
        "net_profit": round(net_profit, 2),
        "trucks_needed": trucks_needed,
        "is_profitable": net_profit > 0
    }

# --- API ENDPOINTS (The Logic) ---
@app.post("/upload-waste")
async def process_waste_document(file: UploadFile = File(...)):
    """
    Receives the uploaded file from Streamlit, passes it to Gemini for extraction, 
    and applies deterministic logistics math before returning the result.
    """
    contents = await file.read()
    filename = file.filename.lower()
    
    # 1. PREPARE THE IMAGE BYTES
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        image_to_process = contents
    elif filename.endswith('.pdf'):
        image_to_process = convert_pdf_to_image(contents)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Please upload a PDF or Image.")

    # 2. FETCH AVAILABLE BUYERS FROM SUPABASE
    buyers = db.fetch_all_buyers()
    if not buyers:
        raise HTTPException(status_code=500, detail="Database empty. No buyers found for matching.")

    # 3. ASK GEMINI TO ANALYZE AND MATCH 
    match_result = ai.analyze_and_match(image_bytes=image_to_process, buyers_list=buyers)

    # 4. ENRICH WITH DETERMINISTIC LOGISTICS MATH
    try:
        matched_buyer_name = match_result.get("best_buyer_match")
        raw_volume = match_result.get("quantity_detected", "0")
        
        # Find the buyer details from the live database list
        matched_buyer_data = next((b for b in buyers if b.get('company_name') == matched_buyer_name), None)
        
        if matched_buyer_data:
            volume_kg = extract_numeric_volume(raw_volume)
            price_per_kg = matched_buyer_data.get('max_price_myr', 0.0)
            distance_km = matched_buyer_data.get('distance_km', 0.0)
            
            # Run the logistics calculation
            logistics = calculate_logistics_and_profit(volume_kg, price_per_kg, distance_km)
            
            # Inject the true net math back into the AI payload for the frontend
            match_result["logistics_breakdown"] = logistics
            match_result["transport_cost_myr"] = f"RM {logistics['transport_cost']:,.2f}"
            
            # Override the generic AI profit with the True Net Profit
            if logistics["is_profitable"]:
                match_result["estimated_profit_myr"] = f"RM {logistics['net_profit']:,.2f}"
            else:
                match_result["estimated_profit_myr"] = f"LOSS: -RM {abs(logistics['net_profit']):,.2f}"
                match_result["reasoning"] += " WARNING: Logistics costs exceed the raw material value."
                
    except Exception as e:
        print(f"Logistics calculation skipped/failed: {e}")
        pass # Fail gracefully and just return the original AI result if math fails

    # 5. RETURN THE FINAL JSON TO THE FRONTEND
    return {
        "status": "success",
        "filename": filename,
        "ai_match_results": match_result
    }

# --- RUN THE SERVER ---
if __name__ == "__main__":
    import uvicorn
    print("Starting the ScrapSync Engine (Powered by Gemini & Logistics Math)...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)