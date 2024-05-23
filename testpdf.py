import streamlit as st
import subprocess
import os
from docx import Document
from PIL import Image, ImageEnhance
from io import BytesIO

def adjust_image_transparency(image, transparency_factor=0.5):
    """Adjust the transparency of an image."""
    if image.mode != 'RGBA':
        image = image.convert('RGBA')
    alpha = image.split()[3]
    alpha = ImageEnhance.Brightness(alpha).enhance(transparency_factor)
    image.putalpha(alpha)
    return image

def ensure_image_transparency(docx_file_path, transparency_factor=0.5):
    doc = Document(docx_file_path)
    for rel in doc.part.rels.values():
        if "image" in rel.target_ref:
            image_part = rel.target_part
            image_data = image_part._blob
            image_stream = BytesIO(image_data)
            try:
                img = Image.open(image_stream)
                img = adjust_image_transparency(img, transparency_factor)

                img_data = BytesIO()
                img.save(img_data, format="PNG")
                img_data.seek(0)

                # Replace the image in the document
                image_part._blob = img_data.read()

            except Exception as e:
                st.warning(f"Could not process an image: {e}")

    # Save the modified document
    temp_docx_path = os.path.join("temp", "modified_" + os.path.basename(docx_file_path))
    doc.save(temp_docx_path)
    return temp_docx_path

def convert_docx_to_pdf(docx_file_path, pdf_file_path):
    # Use LibreOffice to convert the DOCX file to PDF
    result = subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', docx_file_path, '--outdir', os.path.dirname(pdf_file_path)], check=True)
    if result.returncode != 0:
        raise Exception("LibreOffice conversion failed")

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

    if st.button("Convert to PDF"):
        with st.spinner("Converting..."):
            try:
                modified_docx_path = ensure_image_transparency(docx_file_path, transparency_factor=0.2)  # Adjust transparency factor as needed
                convert_docx_to_pdf(modified_docx_path, pdf_file_path)
                st.success("Conversion completed!")
                with open(pdf_file_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=os.path.basename(pdf_file_path), mime="application/pdf")
                os.remove(pdf_file_path)
                os.remove(docx_file_path)
                os.remove(modified_docx_path)
            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred during conversion: {e}")
            except FileNotFoundError as e:
                st.error(f"File not found: {e}")
            except Exception as e:
                st.error(f"An error occurred: {e}")
