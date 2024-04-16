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


def check_reqQ(responses, requirement_statuses):
    for question_text, required in requirement_statuses.items():
        if required:  # Only check required questions
            answer = responses.get(question_text, '')
            # If the answer is a list, check if it contains any valid non-empty entries
            if isinstance(answer, list):
                # Check for non-empty and non-whitespace string entries
                if not any(isinstance(a, str) and a.strip() for a in answer):
                    return False
            elif isinstance(answer, str) and not answer.strip():
                # If it's a string, ensure it's not empty or just whitespace
                return False
    return True


# Streamlit app layout - universal form
def odgovori(opcija):
    st.subheader(opcija)
    questions = load_questions(opcija)

    # Dictionaries to store answers and requirement statuses
    responses = {}
    requirement_statuses = {}
    email = ""
    counter = 0

    # Iterating through each question to create the form
    for index, question in enumerate(questions, start=1):
        question_text = question['question_text']
        options = question['options']
        answer_type = question['answer_type']
        required = question['required']

        # Storing requirement status
        requirement_statuses[question_text] = required

        # Handling different types of questions
        if answer_type == 'choice':
            responses[question_text] = st.selectbox(question_text, options[:-1], index=None, placeholder="Odaberite jednu opciju ")
        elif answer_type == 'multichoice':
            counter += 1
            responses[question_text] = st.multiselect(question_text, options[:-1], placeholder="Možete odabrati više opcija i upisati nove ")
            responses[question_text].append(st.text_input(f"Navedite dodatni odgovor na prethodno pitanje", key=f"dodatni odgovor {counter}", placeholder="Upišite odgovor ovde"))
        elif answer_type == 'opis':
            responses[question_text] = st.text_area(question_text, placeholder="Upišite odgovor ovde")

    # Email input and submit action
    email = st.text_input("Unesite email (obavezno polje):")

    if st.button('Submit') and is_valid_email(email) and check_reqQ(responses, requirement_statuses):
        with st.expander("Odgovori"):
            st.write(responses)
        # Further processing or saving the responses can be added here
        return responses, email
    else:
        st.info("Niste popunili sva obavezna polja")
        return {}, email
    
