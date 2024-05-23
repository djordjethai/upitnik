import streamlit as st
import pypandoc
import os

def convert_docx_to_pdf(docx_file_path, pdf_file_path):
    # Use Pandoc to convert the DOCX file to PDF
    pypandoc.convert_file(docx_file_path, 'pdf', outputfile=pdf_file_path)

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
                convert_docx_to_pdf(docx_file_path, pdf_file_path)
                st.success("Conversion completed!")
                with open(pdf_file_path, "rb") as f:
                    st.download_button("Download PDF", f, file_name=os.path.basename(pdf_file_path), mime="application/pdf")
                os.remove(pdf_file_path)
                os.remove(docx_file_path)
            except Exception as e:
                st.error(f"An error occurred during conversion: {e}")
