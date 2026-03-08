# Scribble to Digital

Turn messy handwritten notes, whiteboard sketches, and journal entries into clean, structured digital text and actionable to-do lists instantly using the power of AI.

## 🚀 Features

- **High-Fidelity AI Transcription:** Uses Google's advanced Generative AI and Optical Character Recognition to decipher poor handwriting.
- **Task Extraction:** Automatically segments actionable items from your notes into a clean checklist.
- **Enterprise-Grade UI:** A beautiful, responsive React Single Page Application built with Vite and Tailwind CSS.
- **FastAPI Backend:** High-performance Python backend handling complex OpenCV image processing and AI orchestration.
- **Local History:** Automatically saves and instantly recalls past scans and their generated tasks.

## 🏗 Architecture

The project has recently been migrated to a modern, decoupled architecture:
1. **Frontend (`/frontend`)**: A React (Vite) application styled with Tailwind CSS v4.
2. **Backend (`main.py`)**: A fast, asynchronous REST API powered by FastAPI.
3. **AI Pipeline**:
   - OpenCV (Adaptive Thresholding, Grayscale, Noise Reduction)
   - PyTesseract (Raw OCR extraction)
   - Google Gemini AI (Context reconstruction, grammar fixing, task segmentation)

## 💻 Getting Started

### Prerequisites
- Python 3.9+
- Node.js & npm (for the frontend)
- Tesseract OCR installed on your system
- A Google Gemini API Key

### Backend Setup
1. Clone the repository.
2. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   .\venv\Scripts\activate
   ```
3. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   pip install fastapi uvicorn[standard] python-multipart pydantic
   ```
4. Create a `.env` file in the root directory and add your key:
   ```env
   GEMINI_API_KEY="your_api_key_here"
   ```
5. Start the FastAPI server:
   ```bash
   uvicorn main:app --reload --port 8000
   ```

### Frontend Setup
1. Open a new terminal and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install dependencies:
   ```bash
   npm install
   ```
3. Start the Vite development server:
   ```bash
   npm run dev
   ```
4. The application will be available at `http://localhost:5173` (or the port specified in your terminal).

## 🛡 License
This project is open-source and available for educational and personal use.
