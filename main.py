from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import os
from PIL import Image
import io
from dotenv import load_dotenv

# Load explicitly before importing internal logic
load_dotenv()

from image_processing import preprocess_image
from ocr_engine import extract_text
from ai_processing import correct_text, extract_todos
from history_manager import load_history, save_to_history

app = FastAPI(title="Scribble to Digital API")

# Setup CORS for the React Frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev, allow all origins. In production restrict to frontend domain.
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

class DigitizeResponse(BaseModel):
    raw_text: str
    corrected_text: str
    todos: str
    status: str

@app.get("/")
def read_root():
    return {"message": "Scribble to Digital API is running"}

@app.get("/api/history")
def get_history():
    """Retrieve all history items."""
    try:
         items = load_history()
         return {"history": items}
    except Exception as e:
         raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/digitize", response_model=DigitizeResponse)
async def digitize_image(file: UploadFile = File(...)):
    """
    Process an uploaded image through the OCR and GenAI pipeline.
    """
    if not file.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="File uploaded was not an image.")
        
    try:
        # Read file content into PIL Image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # 1. Preprocess
        enhanced_img = preprocess_image(image)
        
        # 2. Extract Text via OCR
        raw_text = extract_text(enhanced_img)
        
        if raw_text.startswith("ERROR:"):
            raise HTTPException(status_code=500, detail=raw_text)
            
        # 3. AI Correction
        corrected = correct_text(raw_text)
        
        # 4. Extract Todos
        todos = extract_todos(corrected)
        
        # 5. Save to JSON History
        save_to_history(raw_text, corrected, todos)
        
        return DigitizeResponse(
            raw_text=raw_text,
            corrected_text=corrected,
            todos=todos,
            status="success"
        )
        
    except Exception as e:
        print(f"Server Error during digitize: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Processing Error: {str(e)}")
