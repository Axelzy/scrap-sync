from fastapi import FastAPI, UploadFile, File, HTTPException
import fitz  # PyMuPDF
import io
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

# --- API ENDPOINTS (The Logic) ---
@app.post("/upload-waste")
async def process_waste_document(file: UploadFile = File(...)):
    """
    Receives the uploaded file from the Streamlit frontend and passes 
    it directly to Gemini's visual engine for structural analysis.
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

    # 3. ASK GEMINI TO ANALYZE AND MATCH (Passing the raw image directly!)
    match_result = ai.analyze_and_match(image_bytes=image_to_process, buyers_list=buyers)

    # 4. RETURN THE FINAL JSON TO THE FRONTEND
    return {
        "status": "success",
        "filename": filename,
        "ai_match_results": match_result
    }

# --- RUN THE SERVER ---
if __name__ == "__main__":
    import uvicorn
    print("Starting the ScrapSync Engine (Powered by Gemini)...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)