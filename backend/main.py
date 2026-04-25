from fastapi import FastAPI, UploadFile, File, HTTPException
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import io
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Import our custom ScrapSync modules
from db_client import DatabaseManager
from glm_engine import GLAIEngine

# --- WINDOWS TESSERACT SETUP ---
# Ensure this matches the folder where Tesseract was actually installed on your machine.
# If it's in the x86 folder, change it to: r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe'
pytesseract.pytesseract.tesseract_cmd = os.getenv("TESSERACT_CMD_PATH")

# --- INITIALIZE THE APPLICATION ---
app = FastAPI(title="ScrapSync API Engine")
db = DatabaseManager()
ai = GLAIEngine()

# --- HELPER FUNCTIONS (The Eyes) ---
def extract_text_from_image(image_bytes: bytes) -> str:
    """Reads text from messy photos like handwritten logs or receipts."""
    try:
        image = Image.open(io.BytesIO(image_bytes))
        extracted_text = pytesseract.image_to_string(image)
        return extracted_text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image extraction failed: {str(e)}")

def extract_text_from_pdf(pdf_bytes: bytes) -> str:
    """Reads text from structured PDFs like Safety Data Sheets."""
    try:
        text = ""
        doc = fitz.open(stream=pdf_bytes, filetype="pdf")
        for page in doc:
            text += page.get_text()
        return text.strip()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PDF extraction failed: {str(e)}")


# --- API ENDPOINTS (The Logic) ---
@app.post("/upload-waste")
async def process_waste_document(file: UploadFile = File(...)):
    """
    Receives the uploaded file from the Streamlit frontend, extracts the text, 
    and asks the AI to find the most profitable buyer match.
    """
    contents = await file.read()
    filename = file.filename.lower()
    
    # 1. EXTRACT TEXT BASED ON FILE TYPE
    if filename.endswith(('.png', '.jpg', '.jpeg')):
        raw_text = extract_text_from_image(contents)
    elif filename.endswith('.pdf'):
        raw_text = extract_text_from_pdf(contents)
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Please upload a PDF or Image.")

    if not raw_text:
        raise HTTPException(status_code=400, detail="Could not find any readable text in the document.")

    # 2. FETCH AVAILABLE BUYERS FROM SUPABASE
    buyers = db.fetch_all_buyers()
    if not buyers:
        raise HTTPException(status_code=500, detail="Database empty. No buyers found for matching.")

    # 3. ASK THE GLM TO ANALYZE AND MATCH
    match_result = ai.analyze_and_match(raw_ocr_text=raw_text, buyers_list=buyers)

    # 4. RETURN THE FINAL JSON TO THE FRONTEND
    return {
        "status": "success",
        "filename": filename,
        "ai_match_results": match_result
    }

# --- RUN THE SERVER ---
if __name__ == "__main__":
    import uvicorn
    print("Starting the ScrapSync Engine...")
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)