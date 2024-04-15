import streamlit as st
import os
from openai import OpenAI
from myfunc.retrievers import HybridQueryProcessor
from myfunc.mojafunkcija import send_email
from pitanja import odgovori
import matplotlib.pyplot as plt
import numpy as np

client=OpenAI()
avatar_ai="bot.png" 

# agent llm odgovara na razlicite upite - treba u myfunc
def positive_agent(messages):
    with st.chat_message("assistant", avatar=avatar_ai):
        message_placeholder = st.empty()
        full_response = ""
        for response in client.chat.completions.create(
            model="gpt-4-turbo-preview",
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

# salje email
def posalji_mail(email,gap_analiza, image_path):
    st.info(f"Saljem email na adresu {email}")
    send_email(
            subject="Gap Analiza",
            message= gap_analiza,
            from_addr="azure.test@positive.rs",
            to_addr=email,
            smtp_server="smtp.office365.com",
            smtp_port=587,
            username="azure.test@positive.rs",
            password=os.getenv("PRAVNIK_PASS"),
            image_path= image_path
            )
    st.info(f"Poslat je email na adresu {email}")
 
# RAG pretrazuje index za preporuke    
def recommended(full_response):
    processor = HybridQueryProcessor(namespace="positive", top_k=3)
    return processor.process_query_results(full_response)

# glavni program
def main():
    with st.sidebar:
        st.caption("Ver. 14.04.24" )
        st.subheader("Demo GAP sa grafikonon i slanjem maila ")
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
            # prva faza citanje odgovora i komentar
            gap_message=[
                {"role": "system", "content": """[Use only the Serbian language] You are an expert in business data analysis. \
                 Analyze the document. Think critically and do business analysis of the company. The accent is on GAP analysis. """},

                {"role": "user", "content": f"Write your GAP analysis report based on this input: {result}"}
            ]
            full_response = positive_agent(gap_message)
            predlozi = recommended(full_response)
            # druga faza preporuke na osnovu portfolia
            recommend_message=[
                        {"role": "system", "content": """[Use only the Serbian Language] \
                         You are an experienced digital transformation consultant. \
                         You are working for company Positive doo, the leader in Digital Transformation services in Serbia."""},

                        {"role": "user", "content": f"""Based on previous GAP analysis: {full_response}, \
                         make suggestions for business improvement of the descibed business process. \
                         Be sure to suggest solutions in the form of the proposal (offer) \
                         based on the text from portfolio of your company Positive doo: {predlozi}"""}
            ]
            recommendation_response = positive_agent(recommend_message)    
            # treca faza kreiranje dokumenta
            grafikon = show_graph()
            gap_analiza = full_response + "\n\n" + recommendation_response + "\n\n"
            # cetvrta faza slanje maila
            posalji_mail(email, gap_analiza, grafikon)
                
if __name__ == "__main__":
    main()