import streamlit as st
import subprocess
import os
from docx import Document
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

def set_background_image(doc, image_path):
    header = doc.sections[0].header
    hdr_xml = header._sectPr.xpath('./w:headerReference')[0].getparent()
    
    background = OxmlElement('w:background')
    fill = OxmlElement('v:fill')
    fill.set(qn('r:id'), image_path)
    fill.set('recolor', 't')
    fill.set('type', 'frame')
    fill.set('aspect', 'meet')
    background.append(fill)
    
    hdr_xml.addprevious(background)

def convert_docx_to_pdf(docx_file_path, pdf_file_path):
    subprocess.run(['libreoffice', '--headless', '--convert-to', 'pdf', docx_file_path, '--outdir', os.path.dirname(pdf_file_path)], check=True)

st.title("DOCX to PDF Converter")

uploaded_file = st.file_uploader("Upload a DOCX file", type="docx")

if uploaded_file is not None:
    st.success("File uploaded successfully")
    
    temp_dir = "temp"
    os.makedirs(temp_dir, exist_ok=True)
    
    docx_file_path = os.path.join(temp_dir, uploaded_file.name)
    
    with open(docx_file_path, "wb") as f:
        f.write(uploaded_file.getbuffer())
    
    # Load the DOCX file and set the background image with transparency
    doc = Document(docx_file_path)
    background_image_path = 'path/to/your/background/image.png'  # Ensure this path is correct
    set_background_image(doc, background_image_path)
    
    # Save the modified DOCX file
    modified_docx_file_path = os.path.join(temp_dir, f"modified_{uploaded_file.name}")
    doc.save(modified_docx_file_path)
    
    pdf_file_path = os.path.join(temp_dir, f"{os.path.splitext(uploaded_file.name)[0]}.pdf")

    if st.button("Convert to PDF"):
        with st.spinner("Converting..."):
            try:
                convert_docx_to_pdf(modified_docx_file_path, pdf_file_path)
                st.success("Conversion completed!")
                with open(pdf_file_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=os.path.basename(pdf_file_path), mime="application/pdf")
                os.remove(pdf_file_path)
                os.remove(docx_file_path)
                os.remove(modified_docx_file_path)
            except subprocess.CalledProcessError as e:
                st.error(f"An error occurred during conversion: {e}")
