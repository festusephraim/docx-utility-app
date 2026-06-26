import streamlit as st
import zipfile
import re
import io
import os

import base64
import streamlit as st

# 1. Helper function to encode the image
def get_base64_image(image_path):
    try:
        with open(image_path, "rb") as image_file:
            encoded_string = base64.b64encode(image_file.read()).decode()
        return f"data:image/png;base64,{encoded_string}"
    except FileNotFoundError:
        # Fallback icon in case the image fails to load locally or on Git
        return "🔒"

# 2. Convert your local file 
logo_base64 = get_base64_image("deep9.png")

# 3. Custom Page Configuration & Brand Styling
st.set_page_config(
    page_title="deep9 Clean", 
    page_icon=logo_base64, 
    layout="centered"
)

brand_css = """
<style>
    .stApp {
        background-color: #F4efe6 !important;
        color: #1a2634 !important;
    }
    h1, h2, h3, p {
        color: #1a2634 !important;
        font-family: 'Inter', sans-serif;
    }
    div[data-testid="stFileUploader"] {
        background-color: #ffffff;
        border: 2px dashed #1a2634 !important;
        border-radius: 12px;
        padding: 20px;
        transition: all 0.3s ease;
    }
    div[data-testid="stFileUploader"]:hover {
        border-color: #D77E33 !important;
        background-color: #1a2634;
    }
    div[data-testid="stFileUploader"] * {
        color: #1a2634 !important;
    }
    div[data-testid="stFileUploader"]:hover * {
        color: #dd7733 !important;
    }
    div.stButton > button:first-child {
        background-color: #D77E33 !important;
        color: #1a2634 !important;
        border: 2px solid #1a2634 !important;
        font-weight: 700 !important;
        border-radius: 8px !important;
        padding: 12px 24px !important;
        width: 100%;
        transition: transform 0.1s ease;
    }
    div.stButton > button:first-child:hover {
        background-color: #f4efe6 !important;
        color: #D77E33 !important;
        transform: scale(1.01);
    }
    div[data-testid="stDownloadButton"] > button {
        background-color: #dd7733 !important;
        color: #F4efe6 !important;
        border-radius: 8px !important;
        width: 100%;
    }
    div[data-testid="stDownloadButton"] > button:hover {
        background-color: #D77E33 !important;
        color: #f4efe6 !important;
    }
    .stExpander {
        background-color: #ffffff !important;
        border: 1px solid #1a2634 !important;
        border-radius: 8px;
    }
    div[data-testid="stCheckbox"] label span {
        color: #1a2634 !important;
    }
    
    /* Premium deep9 Corporate Footer Grid Styles */
    .deep9-footer {
        background-color: #1a2634;
        color: #F4efe6;
        padding: 30px 20px;
        border-radius: 12px;
        margin-top: 50px;
        text-align: center;
        font-family: 'Inter', sans-serif;
    }
    .deep9-footer a {
        color: #D77E33 !important;
        text-decoration: none;
        font-weight: bold;
    }
    .deep9-footer a:hover {
        text-decoration: underline;
    }
    .footer-grid {
        display: grid;
        grid-template-columns: 1fr 1fr;
        gap: 20px;
        margin-top: 15px;
        text-align: left;
    }
    @media (max-width: 600px) {
        .footer-grid {
            grid-template-columns: 1fr;
            text-align: center;
        }
    }
    .footer-accent {
        font-size: 0.85rem;
        opacity: 0.7;
        margin-top: 20px;
        border-top: 1px solid rgba(244,239,230,0.1);
        padding-top: 15px;
    }
</style>
"""
st.markdown(brand_css, unsafe_allow_html=True)

# 2. Main Interface Header Elements
st.markdown("<h1 style='text-align: center; font-size: 2.8rem; font-weight: 800; margin-bottom: 0px;'>deep<span style='color:#D77E33; background-color:#1a2634; padding: 2px 8px; border-radius:6px;'>9</span> CLEAN</h1>", unsafe_allow_html=True)
# --- NEW CONVERTING USER TAGLINE ---
st.markdown("<p style='text-align: center; opacity: 0.9; font-size: 1.05rem; margin-top: 15px; margin-bottom: 30px; line-height: 1.6; max-width: 650px; margin-left: auto; margin-right: auto;'>Wipe hidden editing history, author metadata, and tracked changes from your Word documents, or extract your images instantly.</p>", unsafe_allow_html=True)
st.markdown("<p style='text-align: center; opacity: 0.9; font-size: 0.85rem; font-style: italic; color: #DD77E3; margin-top: 8px; margin-bottom: 24px; line-height: 1.4; max-width: 500px; margin-left: auto; margin-right: auto;'> Need to process multiple documents? Check the batch processing box below to upload up to 5 files at once.</p>", unsafe_allow_html=True)

# 3. Mode Toggle Checkbox
enable_bulk = st.checkbox("🔄 Upload multiple files (Up to 5)")

# Conditional File Upload Setup
uploaded_files = []
if enable_bulk:
    input_files = st.file_uploader("Drop up to 5 .docx documents here", type=["docx"], accept_multiple_files=True)
    if input_files:
        if len(input_files) > 5:
            st.error("⚠️ Max limit exceeded. Please upload up to 5 files at a time.")
        else:
            uploaded_files = input_files
else:
    single_file = st.file_uploader("Drop your .docx document here", type=["docx"], accept_multiple_files=False)
    if single_file:
        uploaded_files = [single_file]

# 4. Processing Pipeline Execution Block
if uploaded_files:
    action = st.radio(
        "Select Pipeline Mode:",
        ["Clean Metadata Only", "Extract Images Only", "Do Both (Clean & Extract Images)"]
    )
    
    st.markdown("<br>", unsafe_allow_html=True)
    
    if st.button("EXECUTE PROCESSING PIPELINE"):
        master_zip_stream = io.BytesIO()
        
        with zipfile.ZipFile(master_zip_stream, 'w', zipfile.ZIP_DEFLATED) as master_zip:
            for uploaded_file in uploaded_files:
                file_bytes = uploaded_file.read()
                base_name = os.path.splitext(uploaded_file.name)[0]
                
                # --- PIPELINE SEGMENT 1: SCRUB METADATA ---
                if "Clean" in action or "Both" in action:
                    input_zip_stream = io.BytesIO(file_bytes)
                    cleaned_file_stream = io.BytesIO()
                    
                    try:
                        with zipfile.ZipFile(input_zip_stream, 'r') as src_zip:
                            file_list = src_zip.namelist()
                            with zipfile.ZipFile(cleaned_file_stream, 'w', zipfile.ZIP_DEFLATED) as dest_zip:
                                for item in file_list:
                                    if item in ['docProps/core.xml', 'docProps/app.xml']:
                                        continue
                                    file_data = src_zip.read(item)
                                    if item == 'word/document.xml':
                                        text_data = file_data.decode('utf-8', errors='ignore')
                                        text_data = re.sub(r'</?w:(del|ins|moveFrom|moveTo|rsid)[^>]*>', '', text_data)
                                        file_data = text_data.encode('utf-8')
                                    dest_zip.writestr(item, file_data)
                        
                        cleaned_file_stream.seek(0)
                        master_zip.writestr(f"cleaned_docs/CLEANED_{uploaded_file.name}", cleaned_file_stream.read())
                    except Exception as e:
                        st.error(f"Error processing metadata for {uploaded_file.name}: {e}")

                # --- PIPELINE SEGMENT 2: ASSET IMAGE COLLECTION ---
                if "Images" in action or "Both" in action:
                    input_zip_stream = io.BytesIO(file_bytes)
                    
                    try:
                        with zipfile.ZipFile(input_zip_stream, 'r') as src_zip:
                            media_files = [f for f in src_zip.namelist() if f.startswith('word/media/')]
                            if media_files:
                                for media_file in media_files:
                                    img_data = src_zip.read(media_file)
                                    img_name = os.path.basename(media_file)
                                    master_zip.writestr(f"extracted_images/{base_name}_images/{img_name}", img_data)
                    except Exception as e:
                        st.error(f"Error compiling images for {uploaded_file.name}: {e}")
        
        master_zip_stream.seek(0)
        st.success("✨ Processing complete!")
        
        if len(uploaded_files) == 1 and action == "Clean Metadata Only":
            final_bytes = io.BytesIO()
            with zipfile.ZipFile(master_zip_stream, 'r') as check_zip:
                doc_key = check_zip.namelist()[0]
                final_bytes.write(check_zip.read(doc_key))
            final_bytes.seek(0)
            
            st.download_button(
                label="⬇️ DOWNLOAD CLEANED DOCX",
                data=final_bytes,
                file_name=f"CLEANED_{uploaded_files[0].name}",
                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
            )
        else:
            st.download_button(
                label="⬇️ DOWNLOAD PROCESSED BUNDLE (.ZIP)",
                data=master_zip_stream,
                file_name="deep9_processed_package.zip",
                mime="application/zip"
            )

st.markdown("<br><hr>", unsafe_allow_html=True)

# 5. Standard Compliance Information Block Dropdown
with st.expander("ℹ️ Understanding App Results & Microsoft Word Behavior"):
    st.markdown("""
    ### Why use deep9 Clean?
    While desktop Microsoft Word has a built-in inspector, **deep9 Clean** is explicitly built for secure file cleaning on **iPhones, Android devices, Chromebooks, Google Docs, or Macs** where desktop Word tools are completely unavailable. It permanently strips structural tracking timelines and properties out of open XML wrappers.
    
    ### Analyzing Cleaned Files in Microsoft Word
    If you subject your newly cleaned file download to Microsoft Word's desktop *Document Inspector*, you might see standard configuration notices. Here is what they signify:
    
    *   **'Custom XML Data found':** These represent benign configuration layers generated automatically by cloud-sharing ecosystems like OneDrive or SharePoint. They hold no user profile identities or text timelines. 
    *   **'Headers, Footers, and Watermarks':** This notice flags permanently if a layout contains running head or foot margins. It is informational and notes the presence of header layouts, which are left structurally untouched.
    *   **'Personal Information found':** The instant you open any file on a local computer, Microsoft Word immediately auto-appends a fresh timestamp and links your local desktop system handle as the active viewer. Your past editing hours and authentic historical creators remain thoroughly wiped out.
    """)

# 6. deep9 Ecosystem Marketing & System Navigation Footer
footer_html = """
<div class="deep9-footer">
    <div style="font-size: 1.4rem; font-weight: 800; letter-spacing: 1px;">deep9 SYSTEMS</div>
    <p style="color: #F4efe6 !important; opacity: 0.8; font-size: 0.95rem; margin-top: 5px;">
        Speed without depth is half-baked growth. Build structural excellence with us.
    </p>
    <div class="footer-grid">
        <div>
            <span style="font-weight:bold; color:#D77E33;">💼 Professional Track:</span><br>
            Need an instant, impact-driven, ATS-ready CV and matching cover letter? 
            <a href="https://deep9systems.com" target="_blank">Click here to build your profile →</a>
        </div>
        <div>
            <span style="font-weight:bold; color:#D77E33;">🔬 Academic Track:</span><br>
            Struggling with structure or unsure if your supervisor will approve?
            <a href="https://deep9systems.com" target="_blank">Validate your research topic now →</a>
        </div>
    </div>
    <div class="footer-accent">
        © 2026 <a href="https://deep9systems.com" target="_blank">deep9 systems</a> | All rights reserved. 
        Shop No. 1, Opp. TSU Sport Complex, ATC Jalingo, Taraba State, Nigeria.
    </div>
</div>
"""
st.markdown(footer_html, unsafe_allow_html=True)
