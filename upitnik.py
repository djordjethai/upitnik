import streamlit as st
import os
from openai import OpenAI
from myfunc.retrievers import HybridQueryProcessor
from myfunc.mojafunkcija import send_email
from pitanja import odgovori

client=OpenAI()
avatar_ai="bot.png" 


def posalji_mail(email,gap_analiza):
    st.info(f"Saljem email na adresu {email}")
    send_email(
            subject="Gap Analiza",
            message= gap_analiza,
            from_addr="azure.test@positive.rs",
            to_addr=email,
            smtp_server="smtp.office365.com",
            smtp_port=587,
            username="azure.test@positive.rs",
            password=os.getenv("PRAVNIK_PASS")
            )
    st.info(f"Poslat je email na adresu {email}")
    
def recommended(full_response):
    processor = HybridQueryProcessor(namespace="positive", top_k=3)
    return processor.process_query_results(full_response)

def main():
    with st.sidebar:
        st.caption("Ver. 13.04.24" )
        st.subheader("Demo GAP sa slanjem maila ")
        opcija = st.selectbox("Odaberite upitnik", ("",
                                                    "Opsti", 
                                                    "Poslovna zrelost", 
                                                    "Digitalna zrelost", 
                                                    "Sajber bezbednost", 
                                                    "IT infrastruktura", 
                                                    "Upotreba AI" ))
    if opcija !="":  # Check if the result is not None
        result, email = odgovori(opcija)
        if result:
            with st.chat_message("assistant", avatar=avatar_ai):
                message_placeholder = st.empty()
                full_response = ""
                for response in client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "[Use only the Serbian language] You are an expert in business data analysis. Analyze the document. Think critically and do business analysis of the company. The accent is on GAP analysis. "},
                        {"role": "user", "content": f"Write your report based on this input: {result}"}
                    ],
                    stream=True,
                ):
                    full_response += (response.choices[0].delta.content or "")
                    message_placeholder.markdown(full_response + "▌")
                message_placeholder.markdown(full_response)
                predlozi = recommended(full_response)
                
            with st.chat_message("assistant", avatar=avatar_ai):
                message_placeholder = st.empty()
                recommendation_response = ""
                for response in client.chat.completions.create(
                    model="gpt-4-turbo-preview",
                    messages=[
                        {"role": "system", "content": "[Use only the Serbian Language] You are an experienced digital transformation consultant. You are working for company Positive doo, the leader in Digital Transformation services in Serbia."},
                        {"role": "user", "content": f"Based on previous GAP analysis: {full_response}, make suggestions for business improvement of the descibed business process. Suggest solutins based on the text from portfolio of your company Positive doo: {predlozi}"}
                    ],
                    stream=True,
                ):
                    recommendation_response += (response.choices[0].delta.content or "")
                    message_placeholder.markdown(recommendation_response + "▌")
                message_placeholder.markdown(recommendation_response)
                
            st.info("U ovoj fazi ce se dodati grafikoni...") 
            gap_analiza = full_response + "\n\n" + recommendation_response + "\n\n" + "Ovde ce biti i grafikoni..."
            
            # sledi formatiranje i slanje maila
            posalji_mail(email, gap_analiza)
                
if __name__ == "__main__":
    main()