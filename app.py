import streamlit as st
from PIL import Image
import io
import os
from dotenv import load_dotenv

# Load environment variables explicitly for Streamlit process before importing child modules
load_dotenv()
from image_processing import preprocess_image
from ocr_engine import extract_text
from ai_processing import correct_text, extract_todos
from history_manager import load_history, save_to_history

# Configure page settings
st.set_page_config(
    page_title="Scribble to Digital",
    page_icon="📝",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state for history selection if not exists
if 'view_history_mode' not in st.session_state:
    st.session_state['view_history_mode'] = False
if 'history_data' not in st.session_state:
    st.session_state['history_data'] = None

# Custom CSS for better aesthetics
st.markdown("""
<style>
    /* Google Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', sans-serif;
    }
    
    /* Main Background & Text */
    .stApp {
        background-color: #f8fafc;
        color: #0f172a;
    }

    .main-header {
        font-size: 3.5rem;
        font-weight: 700;
        background: linear-gradient(135deg, #2563EB 0%, #7C3AED 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        margin-bottom: 0px;
        padding-top: 1rem;
    }
    .sub-header {
        font-size: 1.25rem;
        color: #64748b;
        text-align: center;
        margin-bottom: 2.5rem;
        font-weight: 400;
    }
    
    /* Buttons */
    .stButton>button {
        width: 100%;
        background: linear-gradient(135deg, #2563EB 0%, #3B82F6 100%);
        color: white;
        border: none;
        border-radius: 12px;
        font-weight: 600;
        padding: 0.75rem 0;
        box-shadow: 0 4px 6px -1px rgba(37, 99, 235, 0.2);
        transition: all 0.3s ease;
    }
    .stButton>button:hover {
        background: linear-gradient(135deg, #1D4ED8 0%, #2563EB 100%);
        transform: translateY(-2px);
        box-shadow: 0 10px 15px -3px rgba(37, 99, 235, 0.3);
    }
    
    /* Text Display Boxes (Glassmorphism) */
    .text-box {
        background: rgba(255, 255, 255, 0.7);
        backdrop-filter: blur(10px);
        padding: 1.5rem;
        border-radius: 12px;
        border: 1px solid rgba(255, 255, 255, 0.5);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
        min-height: 200px;
        font-family: inherit;
        white-space: pre-wrap;
        color: #1e293b;
        line-height: 1.6;
    }
    
    /* Landing Features */
    .feature-card {
        background: white;
        padding: 1.5rem;
        border-radius: 16px;
        box-shadow: 0 10px 25px -5px rgba(0, 0, 0, 0.05), 0 8px 10px -6px rgba(0, 0, 0, 0.01);
        text-align: center;
        border: 1px solid #f1f5f9;
        transition: transform 0.3s ease;
        height: 100%;
    }
    .feature-card:hover {
        transform: translateY(-5px);
    }
    .feature-icon {
        font-size: 3rem;
        margin-bottom: 1rem;
    }
    .feature-title {
        font-size: 1.25rem;
        font-weight: 600;
        color: #0f172a;
        margin-bottom: 0.5rem;
    }
    .feature-text {
        color: #64748b;
        font-size: 0.95rem;
        line-height: 1.5;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown('<p class="main-header">📝 Scribble to Digital</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Convert Messy Handwritten Notes to Structured Digital Text</p>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("Upload Notes")
    uploaded_file = st.file_uploader("Upload an image (JPG, PNG)", type=["jpg", "jpeg", "png"])
    
    if uploaded_file is not None:
        if st.session_state['view_history_mode']:
            # Automatically turn off history mode if a new file is uploaded
            st.session_state['view_history_mode'] = False
            
    st.markdown("---")
    st.markdown("### Process Status")
    status_placeholder = st.empty()
    status_placeholder.info("Awaiting image upload...")
    
    st.markdown("---")
    st.header("📚 History")
    
    history_items = load_history()
    
    if history_items:
        st.write(f"Showing last {len(history_items)} uploads")
        for i, item in enumerate(history_items):
            # Extract a short preview from the corrected text for the button label
            preview = item.get('corrected_text', '')[:25]
            preview = preview.replace('\n', ' ') + "..." if len(preview) > 0 else "Empty Scan"
            btn_label = f"🕒 {item['timestamp'][:16]} | {preview}"
            
            if st.button(btn_label, key=f"hist_{item['id']}"):
                st.session_state['view_history_mode'] = True
                st.session_state['history_data'] = item
    else:
        st.info("No saved history yet.")


if st.session_state['view_history_mode'] and st.session_state['history_data']:
    item = st.session_state['history_data']
    
    st.markdown(f"### 🕒 History Record: {item['timestamp']}")
    if st.button("← Back to Scanner"):
        st.session_state['view_history_mode'] = False
        st.rerun()
        
    st.markdown("---")
    
    tabs = st.tabs(["Corrected Digital Text", "Actionable To-Dos", "Raw OCR Output"])
    with tabs[0]:
        st.markdown(f'<div class="text-box">{item.get("corrected_text", "")}</div>', unsafe_allow_html=True)
        st.download_button("Download Text", data=item.get("corrected_text", ""), key="dl_hist_txt", file_name="notes_corrected.txt", mime="text/plain")
    with tabs[1]:
        st.markdown(f'<div class="text-box">{item.get("todos", "")}</div>', unsafe_allow_html=True)
        st.download_button("Download Tasks", data=item.get("todos", ""), key="dl_hist_todo", file_name="tasks.txt", mime="text/plain")
    with tabs[2]:
        st.markdown(f'<div class="text-box">{item.get("raw_text", "")}</div>', unsafe_allow_html=True)
        
elif uploaded_file is not None:
    # 1. Image Upload
    image = Image.open(uploaded_file)
    
    # Create two primary columns for layout
    col1, col2 = st.columns([1, 1], gap="large")
    
    with col1:
        st.subheader("Original Image")
        st.image(image, use_column_width=True)
        
        if st.button("Digitize Setup Process"):
            with st.spinner("Processing image..."):
                try:
                    # 2. Preprocessing
                    status_placeholder.warning("Enhancing image...")
                    enhanced_img_cv = preprocess_image(image)
                    st.subheader("Enhanced Image (Machine View)")
                    st.image(enhanced_img_cv, use_column_width=True, channels="GRAY")
                    
                    # 3. OCR Text Extraction
                    status_placeholder.warning("Extracting text via OCR...")
                    raw_text = extract_text(enhanced_img_cv)
                    
                    # Ensure OCR didn't fail
                    if raw_text.startswith("ERROR:"):
                        st.error(raw_text)
                    else:
                        st.session_state['raw_text'] = raw_text
                        
                        # 4. AI Correction
                        status_placeholder.warning("Running AI Correction...")
                        corrected = correct_text(raw_text)
                        st.session_state['corrected_text'] = corrected
                        
                        # 5. Todo Extraction
                        status_placeholder.warning("Extracting Actionable Tasks...")
                        todos = extract_todos(corrected)
                        st.session_state['todos'] = todos
                        
                        # 6. Save to History
                        save_to_history(raw_text, corrected, todos)
                        
                        status_placeholder.success("Processing Complete & Saved to History!")
                except Exception as e:
                    st.error(f"An error occurred during processing: {e}")
                    status_placeholder.error("Processing Failed.")

    with col2:
        st.subheader("Process Output")
        
        tabs = st.tabs(["Corrected Digital Text", "Actionable To-Dos", "Raw OCR Output"])
        
        with tabs[0]:
            if 'corrected_text' in st.session_state:
                st.markdown(f'<div class="text-box">{st.session_state["corrected_text"]}</div>', unsafe_allow_html=True)
                # Download button
                st.download_button("Download Text", data=st.session_state["corrected_text"], file_name="notes_corrected.txt", mime="text/plain")
            else:
                st.info("Run the 'Digitize Setup Process' to view results.")
                
        with tabs[1]:
            if 'todos' in st.session_state:
                st.markdown(f'<div class="text-box">{st.session_state["todos"]}</div>', unsafe_allow_html=True)
                st.download_button("Download Tasks", data=st.session_state["todos"], file_name="tasks.txt", mime="text/plain")
            else:
                st.info("Run the 'Digitize Setup Process' to view results.")
                
        with tabs[2]:
            if 'raw_text' in st.session_state:
                st.markdown(f'<div class="text-box">{st.session_state["raw_text"]}</div>', unsafe_allow_html=True)
            else:
                st.info("Run the 'Digitize Setup Process' to view results.")
else:
    # Landing instructions (Beautiful HTML/CSS blocks)
    st.write("<br>", unsafe_allow_html=True)
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">📸</div>
            <div class="feature-title">Upload Notes</div>
            <div class="feature-text">Snap a photo of your messy handwritten notes or ideas and upload the image file directly to the sidebar.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">🤖</div>
            <div class="feature-title">AI Processing</div>
            <div class="feature-text">Our system uses OpenCV and advanced Generative AI to enhance clarity and reconstruct unclear words automatically.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon">✅</div>
            <div class="feature-title">Extract To-Dos</div>
            <div class="feature-text">Never miss a task. The AI intelligently separates actionable items into a clean, downloadable checklist.</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("<br><br><p style='text-align: center; color: #94a3b8;'>👈 Start by uploading an image in the sidebar</p>", unsafe_allow_html=True)
    st.session_state.clear()
