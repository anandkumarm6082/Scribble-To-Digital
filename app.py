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
    /* Professional Fonts */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');
    
    html, body, [class*="css"]  {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
    }
    
    /* Clean App Background */
    .stApp {
        background-color: #fafafa;
        color: #111827;
    }

    .main-header {
        font-size: 3rem;
        font-weight: 700;
        color: #111827;
        text-align: center;
        margin-bottom: 0.5rem;
        padding-top: 1.5rem;
        letter-spacing: -0.025em;
    }
    .sub-header {
        font-size: 1.15rem;
        color: #4b5563;
        text-align: center;
        margin-bottom: 3rem;
        font-weight: 400;
        max-width: 600px;
        margin-left: auto;
        margin-right: auto;
    }
    
    /* Professional Buttons */
    .stButton>button {
        width: 100%;
        background-color: #111827;
        color: white;
        border: 1px solid #111827;
        border-radius: 8px;
        font-weight: 500;
        padding: 0.6rem 0;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
        transition: all 0.2s ease;
    }
    .stButton>button:hover {
        background-color: #374151;
        border-color: #374151;
        transform: translateY(-1px);
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        color: white;
    }
    
    /* Text Display Boxes */
    .text-box {
        background: #ffffff;
        padding: 1.5rem;
        border-radius: 8px;
        border: 1px solid #e5e7eb;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1), 0 1px 2px 0 rgba(0, 0, 0, 0.06);
        min-height: 250px;
        font-family: inherit;
        white-space: pre-wrap;
        color: #1f2937;
        line-height: 1.6;
        font-size: 0.95rem;
    }
    
    /* Landing Features */
    .feature-card {
        background: #ffffff;
        padding: 2rem 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03);
        text-align: center;
        border: 1px solid #e5e7eb;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        height: 100%;
        display: flex;
        flex-direction: column;
        align-items: center;
    }
    .feature-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.1), 0 4px 6px -2px rgba(0, 0, 0, 0.05);
    }
    .feature-icon-wrapper {
        background: #f3f4f6;
        padding: 1rem;
        border-radius: 50%;
        margin-bottom: 1.25rem;
        display: flex;
        align-items: center;
        justify-content: center;
        width: 64px;
        height: 64px;
    }
    .feature-icon-wrapper svg {
        width: 32px;
        height: 32px;
        color: #4b5563;
    }
    .feature-title {
        font-size: 1.15rem;
        font-weight: 600;
        color: #111827;
        margin-bottom: 0.75rem;
    }
    .feature-text {
        color: #4b5563;
        font-size: 0.9rem;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# Application Header
st.markdown('<p class="main-header">Scribble to Digital</p>', unsafe_allow_html=True)
st.markdown('<p class="sub-header">Convert messy handwritten notes into structured, professional digital text instantly.</p>', unsafe_allow_html=True)

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
            <div class="feature-icon-wrapper">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 9a2 2 0 012-2h.93a2 2 0 001.664-.89l.812-1.22A2 2 0 0110.07 4h3.86a2 2 0 011.664.89l.812 1.22A2 2 0 0018.07 7H19a2 2 0 012 2v9a2 2 0 01-2 2H5a2 2 0 01-2-2V9z"></path><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 13a3 3 0 11-6 0 3 3 0 016 0z"></path></svg>
            </div>
            <div class="feature-title">Upload Notes</div>
            <div class="feature-text">Snap a photo of your handwritten notes or ideas and upload the image file directly to the sidebar.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-wrapper">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19.428 15.428a2 2 0 00-1.022-.547l-2.387-.477a6 6 0 00-3.86.517l-.318.158a6 6 0 01-3.86.517L6.05 15.21a2 2 0 00-1.806.547M8 4h8l-1 1v5.172a2 2 0 00.586 1.414l5 5c1.26 1.26.367 3.414-1.415 3.414H4.828c-1.782 0-2.674-2.154-1.414-3.414l5-5A2 2 0 009 10.172V5L8 4z"></path></svg>
            </div>
            <div class="feature-title">AI Processing</div>
            <div class="feature-text">Our system uses advanced computer vision and Generative AI to enhance clarity and reconstruct unclear words.</div>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class="feature-card">
            <div class="feature-icon-wrapper">
                <svg fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2m-6 9l2 2 4-4"></path></svg>
            </div>
            <div class="feature-title">Extract To-Dos</div>
            <div class="feature-text">Never miss a task. The engine intelligently separates actionable items into a clean, downloadable checklist.</div>
        </div>
        """, unsafe_allow_html=True)

    st.write("<br><br><p style='text-align: center; color: #94a3b8;'>👈 Start by uploading an image in the sidebar</p>", unsafe_allow_html=True)
    st.session_state.clear()
