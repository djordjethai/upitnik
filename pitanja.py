import streamlit as st
import json
import re

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

# Streamlit app layout
def odgovori(opcija):
    st.subheader(opcija)

    # Load the questions
    questions = load_questions(opcija)

    # Dictionary to store answers
    responses = {}
    email = ""
    # Iterate through questions and display appropriate input options
    for question in questions:
        question_text = question['question_text']
        options = question['options']
        answer_type = question['answer_type']

        # For choice questions (single or multiple options)
        if answer_type == 'choice':
            if any("Molimo navedite" in option for option in options):
                # Assuming "Other [Please specify]" needs a text input
                responses[question_text] = st.multiselect(question_text, options[:-1])
                responses[question_text].append(st.text_input("Please specify if 'Other'"))
            else:
                responses[question_text] = st.selectbox(question_text, options)
        # For free text questions
        elif answer_type == 'opis':
            responses[question_text] = st.text_area(question_text)
    email = st.text_input("Unestite email (obavezno polje):")
    # Submit button
    if st.button('Submit') and is_valid_email(email):
        # Here you can further process responses or save them
        return responses, email
    else:
        return {}, email
    
