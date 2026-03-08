import os
from PIL import Image

# Import project modules
from image_processing import preprocess_image
from ocr_engine import extract_text
from ai_processing import correct_text, extract_todos

def main():
    if not os.path.exists("sample_note.jpg"):
        print("Please run create_test_image.py first.")
        return

    print("--- 1. Loading Image ---")
    image = Image.open("sample_note.jpg")
    print(f"Loaded image size: {image.size}")

    print("\n--- 2. Preprocessing Image ---")
    processed_img = preprocess_image(image)
    print("Image preprocessed via OpenCV.")

    print("\n--- 3. Extracting Text (OCR) ---")
    raw_text = extract_text(processed_img)
    print("Raw OCR Output:")
    print(">" * 20)
    print(raw_text)
    print("<" * 20)

    # Note: Ensure GEMINI_API_KEY is available in .env for these to work
    if "GEMINI_API_KEY" in os.environ or os.path.exists(".env"):
        print("\n--- 4. Running AI Correction ---")
        corrected = correct_text(raw_text)
        print("Corrected Text:")
        print(">" * 20)
        print(corrected)
        print("<" * 20)

        print("\n--- 5. Extracting To-Dos ---")
        todos = extract_todos(corrected)
        print("Extracted Action Items:")
        print(">" * 20)
        print(todos)
        print("<" * 20)
    else:
         print("\nGEMINI_API_KEY not found in .env, skipping GenAI step")

    print("\nPipeline test complete.")

if __name__ == "__main__":
    main()
