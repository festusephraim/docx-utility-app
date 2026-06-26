import streamlit as st
import zipfile
import re
import io
import os

st.set_page_config(page_title="Docx Utility Suite", page_icon="🛠️", layout="centered")
st.title("🛠️ Word Document Utility Suite")
st.write("Upload a `.docx` file to remove metadata or extract hidden images.")

uploaded_file = st.file_uploader("Choose a Word Document (.docx)", type=["docx"])

if uploaded_file is not None:
    # Read uploaded file into memory
    file_bytes = uploaded_file.read()
    
    # Let user choose what feature they want
    action = st.radio(
        "What would you like to do?",
        ["Clean Metadata Only", "Extract Images Only", "Do Both (Clean & Extract Images)"]
    )
    
    # Process actions on button click
    if st.button("Process Document"):
        base_name = os.path.splitext(uploaded_file.name)[0]
        
        # --- FEATURE 1: CLEAN METADATA ---
        if "Clean" in action or "Both" in action:
            input_zip_stream = io.BytesIO(file_bytes)
            output_zip_stream = io.BytesIO()
            
            try:
                with zipfile.ZipFile(input_zip_stream, 'r') as src_zip:
                    file_list = src_zip.namelist()
                    with zipfile.ZipFile(output_zip_stream, 'w', zipfile.ZIP_DEFLATED) as dest_zip:
                        for item in file_list:
                            if item in ['docProps/core.xml', 'docProps/app.xml']:
                                continue
                            file_data = src_zip.read(item)
                            if item == 'word/document.xml':
                                text_data = file_data.decode('utf-8', errors='ignore')
                                text_data = re.sub(r'</?w:(del|ins|moveFrom|moveTo|rsid)[^>]*>', '', text_data)
                                file_data = text_data.encode('utf-8')
                            dest_zip.writestr(item, file_data)
                
                output_zip_stream.seek(0)
                st.success("✨ Metadata cleaned successfully!")
                st.download_button(
                    label="⬇️ Download Cleaned Document",
                    data=output_zip_stream,
                    file_name=f"CLEANED_{uploaded_file.name}",
                    mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                )
            except Exception as e:
                st.error(f"Error cleaning metadata: {e}")

        # --- FEATURE 2: EXTRACT IMAGES ---
        if "Images" in action or "Both" in action:
            input_zip_stream = io.BytesIO(file_bytes)
            images_zip_stream = io.BytesIO()
            
            try:
                with zipfile.ZipFile(input_zip_stream, 'r') as src_zip:
                    media_files = [f for f in src_zip.namelist() if f.startswith('word/media/')]
                    
                    if media_files:
                        # Bundle all extracted images into a new downloadable .zip file
                        with zipfile.ZipFile(images_zip_stream, 'w', zipfile.ZIP_DEFLATED) as img_zip:
                            for media_file in media_files:
                                img_data = src_zip.read(media_file)
                                img_name = os.path.basename(media_file)
                                img_zip.writestr(img_name, img_data)
                        
                        images_zip_stream.seek(0)
                        st.success(f"🖼️ Found and extracted {len(media_files)} images!")
                        st.download_button(
                            label="⬇️ Download Extracted Images (.zip)",
                            data=images_zip_stream,
                            file_name=f"images_from_{base_name}.zip",
                            mime="application/zip"
                        )
                    else:
                        st.warning("No images found inside this document.")
            except Exception as e:
                st.error(f"Error extracting images: {e}")
