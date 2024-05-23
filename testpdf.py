import streamlit as st
import subprocess
import os
from docx import Document
from docx.oxml import parse_xml
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

def process_images_in_part(part, transparency_factor):
    image_count = 0
    for rel in part.rels.values():
        if "image" in rel.target_ref:
            image_part = rel.target_part
            image_data = image_part._blob
            image_stream = BytesIO(image_data)
            try:
                img = Image.open(image_stream)
                st.write(f"Processing image {image_count + 1} with size {img.size}")
                img = adjust_image_transparency(img, transparency_factor)

                img_data = BytesIO()
                img.save(img_data, format="PNG")
                img_data.seek(0)

                # Replace the image in the document
                image_part._blob = img_data.read()
                image_count += 1

            except Exception as e:
                st.warning(f"Could not process an image: {e}")
    return image_count

def process_anchored_images(doc, transparency_factor):
    image_count = 0
    for shape in doc.element.findall('.//{http://schemas.openxmlformats.org/drawingml/2006/main}blip'):
        rId = shape.get('{http://schemas.openxmlformats.org/officeDocument/2006/relationships}embed')
        if rId:
            image_part = doc.part.related_parts[rId]
            image_data = image_part._blob
            image_stream = BytesIO(image_data)
            try:
                img = Image.open(image_stream)
                st.write(f"Processing anchored image {image_count + 1} with size {img.size}")
                img = adjust_image_transparency(img, transparency_factor)

                img_data = BytesIO()
                img.save(img_data, format="PNG")
                img_data.seek(0)

                # Replace the image in the document
                image_part._blob = img_data.read()
                image_count += 1

            except Exception as e:
                st.warning(f"Could not process an anchored image: {e}")
    return image_count

def ensure_image_transparency(docx_file_path, transparency_factor=0.5):
    doc = Document(docx_file_path)
    image_count = 0

    # Process images in headers and footers only
    for section in doc.sections:
        for header in section.header.part.rels.values():
            if "image" in header.target_ref:
                image_count += process_images_in_part(header.target_part, transparency_factor)
        for footer in section.footer.part.rels.values():
            if "image" in footer.target_ref:
                image_count += process_images_in_part(footer.target_part, transparency_factor)

    # Process anchored images
    image_count += process_anchored_images(doc, transparency_factor)

    st.write(f"Total images processed in headers/footers: {image_count}")

    # Save the modified document
    temp_docx_path = os.path.join("temp", "modified_" + os.path.basename(docx_file_path))
    doc.save(temp_docx_path)
    return temp_docx_path

def convert_docx_to_pdf(docx_file_path):
    # Use LibreOffice to convert the DOCX file to PDF
    result = subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', docx_file_path, '--outdir', os.path.dirname(docx_file_path)], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    st.write(result.stdout.decode())
    st.write(result.stderr.decode())
    if result.returncode != 0:
        raise Exception("LibreOffice conversion failed")

    # Extract the output PDF path from the command output
    output_pdf_path = docx_file_path.replace('.docx', '.pdf')
    return output_pdf_path

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
    
    if st.button("Convert to PDF"):
        with st.spinner("Converting..."):
            try:
                modified_docx_path = ensure_image_transparency(docx_file_path, transparency_factor=0.2)  # Adjust transparency factor as needed
                st.write(f"Modified DOCX saved at: {modified_docx_path}")
                pdf_file_path = convert_docx_to_pdf(modified_docx_path)
                st.write(f"PDF saved at: {pdf_file_path}")
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
