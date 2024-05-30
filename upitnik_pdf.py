import io
import markdown
import matplotlib.pyplot as plt
import numpy as np
import os
import pdfkit
import streamlit as st

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH
from email import encoders
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from html2docx import html2docx
from openai import OpenAI
from pitanja import odgovori
from smtplib import SMTP

from myfunc.mojafunkcija import initialize_session_state
from myfunc.prompts import get_prompts
from myfunc.retrievers import HybridQueryProcessor
from myfunc.varvars_dicts import work_vars

client=OpenAI()
avatar_ai="bot.png" 
pdf_file = "analysis_report.pdf"

default_values = {
    "gap_ba_expert" : "You are a helpful assistant",
    "gap_dt_consultant" : "You are helpful assistant",
    "gap_service_suggestion" : "You are a helpful assistant",
    "gap_write_report" : "You are a helpful assistant",
}

initialize_session_state(default_values)

if st.session_state.gap_ba_expert == "You are a helpful assistant":
    get_prompts("gap_ba_expert", "gap_dt_consultant", "gap_service_suggestion", "gap_write_report")


# modifikovano iz myfunc.mojafunkcija (umesto downlaod ide save pdf)
def sacuvaj_dokument_upitnik(content, file_name):
    """
    Saves a markdown content as a text, DOCX, and PDF file, providing options to download each format.
    
    Args:
    content (str): The markdown content to be saved.
    file_name (str): The base name for the output files.
    image_path (str): Path to the image file to include in the document.

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

    # # Specify your file name
    # file_name = 'radar_chart.png'

    # # Join the current working directory with the file name
    # image_path = os.path.join(cwd, file_name)
    # #image_path = os.path.abspath(r'C:\Users\nemanja.perunicic\OneDrive - Positive doo\Desktop\allIn1\upitnik\radar_chart.png')

    # image_html = f'<img src="{image_path}" alt="Radar Chart">'
    html = markdown.markdown(content) # + image_html

    # Convert HTML to DOCX
    buf = html2docx(html, title="Content")
    doc = Document(io.BytesIO(buf.getvalue()))
    for paragraph in doc.paragraphs:
        paragraph.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
    
    doc_io = io.BytesIO()
    doc.save(doc_io)
    doc_io.seek(0)
    pdf_file_name = os.path.join(cwd, "analysis_report.pdf")  # Use an absolute path
    # Convert HTML to PDF with the image embedded
    pdfkit.from_string(html, f"{pdf_file_name}", options=options)
    if not os.path.exists(file_name):
        raise Exception(f"Failed to create PDF file at {pdf_file_name}")
 

# Function to send email, adjusted for the new PDF generation
def posalji_mail(email, ime):
    st.info(f"Sending email to {email}")
    cwd = os.getcwd()
    pdf_path = os.path.join(cwd, pdf_file)
    #pdf_path = pdf_file
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


# Adjusted mail sending function to attach PDF
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


# agent llm odgovara na razlicite upite - treba u myfunc
def positive_agent(messages):
    with st.chat_message("assistant", avatar=avatar_ai):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model=work_vars["names"]["openai_model"],
            messages=messages,
            stream=True,
        ):
            full_response += (response.choices[0].delta.content or "")
            message_placeholder.markdown(full_response + "▌")
        message_placeholder.markdown(full_response)
        
    return full_response


# privremeni grafikon
def create_radar_chart(data, labels, num_vars):
    angles = np.linspace(0, 2 * np.pi, num_vars, endpoint=False).tolist()
    data += data[:1]
    angles += angles[:1]

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw=dict(polar=True))
    ax.fill(angles, data, color='red', alpha=0.25)
    ax.plot(angles, data, color='red', linewidth=2)  # Draw the outline
    ax.set_yticklabels([])
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(labels)
    return fig


# cuva grafikon
def show_graph():
    st.title('Polar Chart Example')
    labels = ['Poslovna zrelostt', 'Digitalna zrelost', 'Upotreba AI', 'Sajber bezbednost', 'IT infrastruktura']
    data = [4, 3, 4, 2, 5]
    num_vars = len(data)
    # Plotting
    radar_fig = create_radar_chart(data, labels, num_vars)
    radar_fig.savefig('radar_chart.png', bbox_inches='tight')
    # Display in Streamlit
    st.pyplot(radar_fig)
    return 'radar_chart.png'

 
# RAG pretrazuje index za preporuke    
def recommended(full_response):
    processor = HybridQueryProcessor(namespace="positive", top_k=3)
    return processor.process_query_results(full_response)


# glavni program
def main():
    opcija = os.getenv("ANKETA", "Sve")

    if opcija == "Sve":
        with st.sidebar:
            st.caption("Ver. 30.05.24" )
            st.subheader("Demo GAP sa grafikonon i slanjem maila ")
            opcija = st.selectbox("Odaberite upitnik", ("",
                                                        "Opsti", 
                                                        "Poslovna zrelost", 
                                                        "Digitalna zrelost", 
                                                        "Sajber bezbednost", 
                                                        "IT infrastruktura", 
                                                        "Upotreba AI" ))
            


#### Dodati u pdf i pitanja i odgovore !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! #############################
    if opcija !="":  # Check if the result is not None
        result, email, ime = odgovori(opcija)
        if result:
            # prva faza citanje odgovora i komentar
            gap_message=[
                {"role": "system", "content": st.session_state.gap_ba_expert},
                {"role": "user", "content": st.session_state.gap_write_report.format(result=result)}
            ]
            full_response = positive_agent(gap_message)
            predlozi = recommended(full_response)
            #full_response = "xx"
            #predlozi = "xx"
            # druga faza preporuke na osnovu portfolia
            recommend_message=[
                        {"role": "system", "content": st.session_state.gap_dt_consultant},
                        {"role": "user", "content": st.session_state.gap_service_suggestion.format(full_response=full_response, predlozi=predlozi)}
            ]
            recommendation_response = positive_agent(recommend_message)
            #recommendation_response = "xx"  
            # treca faza kreiranje dokumenta
            # show_graph()
            gap_analiza = full_response + "\n\n" + recommendation_response + "\n\n"
            sacuvaj_dokument_upitnik(gap_analiza, pdf_file)
            # cetvrta faza slanje maila
            posalji_mail(email, ime)
            try:    
                os.remove(pdf_file)
            except:
                pass
                
if __name__ == "__main__":
    main()