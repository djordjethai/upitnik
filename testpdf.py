import streamlit as st
import subprocess
import os
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement
from PIL import Image
from io import BytesIO

def ensure_image_transparency(docx_file_path):
    doc = Document(docx_file_path)
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image = rel.target_part._blob
            image_stream = BytesIO(image)
            try:
                img = Image.open(image_stream)
                if img.mode in ("RGBA", "LA") or (img.mode == "P" and "transparency" in img.info):
                    continue  # Image already has transparency

                # Convert to PNG with transparency
                img = img.convert("RGBA")
                img_data = BytesIO()
                img.save(img_data, format="PNG")
                img_data.seek(0)

                # Update the image in the document
                new_image_part = rel.target_part.package._image_parts[0]._image
                new_image_part._blob = img_data.read()
                rel.target_part._blob = new_image_part._blob

            except Exception as e:
                st.warning(f"Could not process an image: {e}")

    # Save the modified document
    doc.save(docx_file_path)

def convert_docx_to_pdf(docx_file_path, pdf_file_path):
    # Use LibreOffice to convert the DOCX file to PDF
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', docx_file_path, '--outdir', os.path.dirname(pdf_file_path)], check=True)

st.title("DOCX to PDF Converter")

uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

if uploaded_file is not None:
    st.success("File uploaded successfully")
    
    # Ensure the 'temp' directory exists
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    docx_file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(docx_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    pdf_file_path = os.path.join(temp_dir, f"{os.path.splitext(uploaded_file.name)[0]}.pdf")

    # Ensure image transparency before conversion
    ensure_image_transparency(docx_file_path)

    if st.button("Convert to PDF"):
        with st.spinner("Converting..."):
            try:
                convert_docx_to_pdf(docx_file_path, pdf_file_path)
                st.success("Conversion completed!")
                with open(pdf_file_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=os.path.basename(pdf_file_path), mime="application/pdf")
                os.remove(pdf_file_path)
                os.remove(docx_file_path)
            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred during conversion: {e}")
