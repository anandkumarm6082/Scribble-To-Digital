import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_genai_model():
    """Initialize and return the GenAI model."""
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable not set. Please set it in .env file.")
        
    genai.configure(api_key=api_key)
    # Using gemini-2.5-flash for text tasks
    model = genai.GenerativeModel('gemini-2.5-flash')
    return model

def correct_text(raw_text):
    """
    Uses Generative AI to correct spelling, improve grammar,
    and reconstruct unclear words from the raw OCR text.
    """
    if not raw_text or raw_text.startswith("ERROR"):
        return ""
        
    try:
        model = get_genai_model()
        prompt = f"""
        You are an expert editor dealing with raw OCR text extracted from messy handwritten notes. 
        Your task is to correct spelling mistakes, improve grammar, and reconstruct incomplete or unclear words 
        using contextual understanding.
        
        Format the text into structured, readable paragraphs. Do not add any new information not present in the text, 
        just clean it up and make it professional.
        
        Raw OCR Text:
        ---
        {raw_text}
        ---
        
        Corrected Text:
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during AI correction: {str(e)}"

def extract_todos(corrected_text):
    """
    Uses Generative AI to identify and extract actionable tasks from the text.
    """
    if not corrected_text or corrected_text.startswith("Error"):
        return ""
        
    try:
        model = get_genai_model()
        prompt = f"""
        Analyze the following text (which is a digitized version of handwritten notes) and identify any actionable tasks or To-Do items.
        
        Extract these actionable items and organize them into a clean, structured bullet-point To-Do list.
        If there are no clear tasks, output "No actionable tasks found in the notes."
        Do not include general information, only things that look like tasks, action items, or reminders.
        
        Text to analyze:
        ---
        {corrected_text}
        ---
        
        To-Do List:
        """
        
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        return f"Error during To-Do extraction: {str(e)}"
