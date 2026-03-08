import pytesseract
from PIL import Image
import numpy as np

# Note: pytesseract requires tesseract executable installed on the system.
# Typical windows installation path:
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
# We will check if it's available or set the default path.

import sys
import os

if sys.platform == 'win32':
    # Try common installation paths on Windows
    common_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        r'C:\Users\anand\AppData\Local\Programs\Tesseract-OCR\tesseract.exe'
    ]
    for path in common_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            break

def extract_text(image):
    """
    Extract text from a preprocessed image using OCR.
    Args:
        image: Preprocessed image (numpy array or PIL Image)
    Returns:
        str: Raw extracted text
    """
    try:
        # If the image is a numpy array from OpenCV preprocessing,
        # pytesseract can handle it directly or via PIL
        if isinstance(image, np.ndarray):
            # Convert to PIL Image for reliability
            img = Image.fromarray(image)
        else:
            img = image
            
        custom_config = r'--oem 3 --psm 6' # 3 is default OEM, 6 is assume a single uniform block of text
        raw_text = pytesseract.image_to_string(img, config=custom_config)
        return raw_text.strip()
    except pytesseract.TesseractNotFoundError:
        return "ERROR: Tesseract OCR is not installed or not added to PATH. Please install Tesseract-OCR."
    except Exception as e:
        return f"ERROR during OCR extraction: {str(e)}"
