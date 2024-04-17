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
    st.caption("Polja obeležena * su obavezna za unos")
    questions = load_questions(opcija)
    print("AAA", questions)
    # Dictionaries to store answers and requirement statuses
    responses = {}
    requirement_statuses = {}
    email = ""
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
            st.write(question_text)
            responses[question_text] = st.radio(f"q{index}", options, index=None, label_visibility="collapsed")
            if responses[question_text] == "Drugo":
                responses[question_text] = st.text_input(f"Upišite odgovor na prethodno pitanje", key=f"odgovor {index}", placeholder="Upišite odgovor ovde")
        elif answer_type == 'multichoice':
            
            #responses[question_text] = st.multiselect(question_text, options[:-1], placeholder="Možete odabrati više opcija i upisati nove ")
            #########
            current_answers = []
            st.write(question_text)  # Optional, for displaying the question
            for option in options:
                # Create a checkbox for each option
                if st.checkbox(option, key=f"{question_text}_{option}_{index}"):
                    # If the checkbox is checked, append the option to the current answers list
                    current_answers.append(option)
    
                # Store the collected answers in the responses dictionary
                responses[question_text] = current_answers
            
            #########
            responses[question_text].append(st.text_input(f"Opciono možete navesti dodatni odgovor na prethodno pitanje", key=f"dodatni odgovor {index}", placeholder="Upišite odgovor ovde"))
        elif answer_type == 'opis':
            st.write(question_text)
            responses[question_text] = st.text_area(f"q{index}", placeholder="Upišite odgovor ovde", key=f"{index}_text_area", label_visibility="collapsed")

    # Email input and submit action
    email = st.text_input("Unesite email * :")
    potvrda = st.button('Pošalji')
    if potvrda and is_valid_email(email) and check_reqQ(responses, requirement_statuses):
        with st.expander("Odgovori"):
            st.write(responses)
        # Further processing or saving the responses can be added here
        return responses, email
    else:
        if potvrda:
            st.error("Niste popunili sva obavezna polja. Molim Vas popunite sva polja obeležena sa *")
        return {}, email
        
