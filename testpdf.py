import os
import io
import markdown
import pdfkit
from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from smtplib import SMTP
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders
import streamlit as st

def sacuvaj_dokument_upitnik(content, file_name):
    """
    Saves a markdown content as a text, DOCX, and PDF file, providing options to download each format.
    
    Args:
    content (str): The markdown content to be saved.
    file_name (str): The base name for the output files.

    This function converts the markdown content into HTML, then into a DOCX document
    and a PDF file. It justifies the paragraphs in the DOCX document. The function 
    also provides Streamlit download buttons for each file format: text, DOCX, and PDF.
    The function assumes an environment where Streamlit, markdown, html2docx, and pdfkit
    libraries are available, and uses UTF-8 encoding for the text file.
    """
    st.info("Čuva dokument")
    options = {
        "enable-local-file-access": "",
        "encoding": "UTF-8",
        "no-outline": None,
        "quiet": "",
    }

    # Adding the image to the markdown content
    cwd = os.getcwd()

    html = markdown.markdown(content)

    # Convert HTML to DOCX
    buf = io.BytesIO()
    doc = Document()
    doc.add_paragraph(html)
    for paragraph in doc.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    with open(f"{file_name}.docx", "wb") as f:
        f.write(doc_io.getvalue())

    pdf_file_name = os.path.join(cwd, f"{file_name}.pdf")  # Use an absolute path
    # Convert HTML to PDF with the image embedded
    pdfkit.from_string(html, pdf_file_name, options=options)
    if not os.path.exists(pdf_file_name):
        raise Exception(f"Failed to create PDF file at {pdf_file_name}")
    return pdf_file_name

def posalji_mail(email, ime, pdf_file):
    st.info(f"Sending email to {email}")
    cwd = os.getcwd()
    pdf_path = os.path.join(cwd, pdf_file)
    send_email(
        subject="Izveštaj - Gap Analiza",
        message=f"Poštovani {ime}, izveštaj se nalazi u prilogu ovog maila",
        from_addr="azure.test@positive.rs",
        to_addr=email,
        smtp_server="smtp.office365.com",
        smtp_port=587,
        username="azure.test@positive.rs",
        password=os.getenv("PRAVNIK_PASS"),
        attachments=[pdf_path]
    )
    send_email(
        subject="Izveštaj - Gap Analiza",
        message=f"Poštovani {ime}, izveštaj se nalazi u prilogu ovog maila",
        from_addr="azure.test@positive.rs",
        to_addr="prodaja@positive.rs",
        smtp_server="smtp.office365.com",
        smtp_port=587,
        username="azure.test@positive.rs",
        password=os.getenv("PRAVNIK_PASS"),
        attachments=[pdf_path]
    )
    st.info(f"Email sent to {email}")
    os.remove(pdf_path)  # Optionally remove the file after sending

def send_email(subject, message, from_addr, to_addr, smtp_server, smtp_port, username, password, attachments=None):
    msg = MIMEMultipart()
    msg['From'] = from_addr
    msg['To'] = to_addr
    msg['Subject'] = subject
    msg.attach(MIMEText(message, 'plain'))
    
    if attachments:
        for attachment in attachments:
            with open(attachment, 'rb') as file:
                part = MIMEBase('application', 'octet-stream')
                part.set_payload(file.read())
            encoders.encode_base64(part)
            part.add_header('Content-Disposition', 'attachment', filename=os.path.basename(attachment))
            msg.attach(part)

    server = SMTP(smtp_server, smtp_port)
    server.starttls()
    server.login(username, password)
    server.send_message(msg)
    server.quit()


if st.button("start"):
    content = "# Sample Markdown\nThis is a sample markdown content."
    file_name = "output"
    pdf_file_name = sacuvaj_dokument_upitnik(content, file_name)
    posalji_mail("nemanja.perun98@gmail.com", "Nemanja Perunicic", pdf_file_name)
