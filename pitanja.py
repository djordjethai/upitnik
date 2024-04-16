import streamlit as st
import json
import re

# proverava ispravnost email adrese - treba u myfunc
def is_valid_email(email):
    # Regular expression pattern for validating an email
    email_regex = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    
    # Using re.match to see if the pattern matches the string
    if re.match(email_regex, email):
        return True
    else:
        return False

# Function to load questions from a JSON file
def load_questions(opcija):
    with open(f'{opcija}.json', 'r', encoding='utf-8') as file:
        questions = json.load(file)
    return questions

# Streamlit app layout - univerzalni formular
def odgovori(opcija):
    st.subheader(opcija)

    # Load the questions na osnovu odabrane vrste upitnika
    questions = load_questions(opcija)

    # Dictionary to store answers
    responses = {}
    email = ""
    # Iterate through questions and display appropriate input options
    counter = 0
    for question in questions:
        question_text = question['question_text']
        options = question['options']
        answer_type = question['answer_type']

        # For choice questions (single or multiple options)
        if answer_type == 'choice':
            responses[question_text] = st.selectbox(question_text, options[:-1], index=None, placeholder = "Odaberite jednu opciju ")
        # za multiselect i mogucnost upisa dodatnog odgovora
        elif answer_type == 'multichoice':
            counter += 1
            responses[question_text] = st.multiselect(question_text, options[:-1], placeholder = "Možete odabrati vise opcija i upisati nove ")
            responses[question_text].append(st.text_input(f"Navedite dodatni odgovor na prethodno pitanje", key=f"dodatni odgovor {counter}"))
        # za tekstualne odgovore        
        elif answer_type == 'opis':
            responses[question_text] = st.text_area(question_text, placeholder="Upišite odgovor ovde")

    email = st.text_input("Unestite email (obavezno polje):")
    # Submit button
    if st.button('Submit') and is_valid_email(email):
        with st.expander("Odgovori"):
            st.write(responses)
        # Here you can further process responses or save them
        return responses, email
    else:
        return {}, email
    
