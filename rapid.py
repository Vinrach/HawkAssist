import streamlit as st
import fitz  # PyMuPDF
import nltk
import re
from nltk.tokenize import sent_tokenize, word_tokenize
from nltk.tag import pos_tag
import random
from datetime import datetime, timedelta

# Download NLTK resources
nltk.download('punkt')
nltk.download('averaged_perceptron_tagger')

# Function to extract text from PDF
def extract_text_from_pdf(pdf_path):
    text = ""
    with fitz.open(pdf_path) as pdf_document:
        for page_num in range(len(pdf_document)):
            page = pdf_document.load_page(page_num)
            text += page.get_text()
    return text

# Function to generate MCQs from text
def generate_mcqs(text):
    sentences = sent_tokenize(text)
    used_sentences = set()
    mcqs = []

    for sentence in sentences:
        if sentence not in used_sentences:
            words = word_tokenize(sentence)
            tagged_words = pos_tag(words)
            nouns = [word for word, pos in tagged_words if pos.startswith('NN')]

            if len(nouns) < 2:
                continue

            answer = random.choice(nouns)
            other_nouns = [word for word in nouns if word != answer]
            random.shuffle(other_nouns)
            distractors = other_nouns[:min(3, len(other_nouns))]

            answer = re.sub(r'\W+', '', answer).strip()
            distractors = [re.sub(r'\W+', '', option).strip() for option in distractors]

            options = list(set([answer] + distractors))
            options = [option for option in options if option]

            if len(options) < 4:
                continue

            random.shuffle(options)
            question = f"What is {sentence.replace(answer, '_____')}?"
            mcq = {'question': question, 'options': options, 'answer': answer}
            mcqs.append(mcq)
            used_sentences.add(sentence)

    return mcqs

# Function to handle question selection
def freeze_question(i):
    selected_option = st.session_state[f'rapid_question_{i}']
    if selected_option:
        st.session_state.rapid_selected_options[i] = selected_option
        st.session_state.current_question += 1

# Function to display results
def display_results():
    st.header('Time is up! Here are your results:')
    score = 0
    total_questions = len(st.session_state.rapid_selected_options)
    for i in range(total_questions):
        mcq = st.session_state.rapid_mcqs[i]
        st.write(f"Question {i + 1}: {mcq['question']}")
        st.write(f"Your Answer: {st.session_state.rapid_selected_options.get(i, 'Not Answered')}")
        st.write(f"Correct Answer: {mcq['answer']}")
        if st.session_state.rapid_selected_options.get(i) == mcq['answer']:
            score += 1
    st.write(f"Score: {score}/{total_questions}")

# Main Streamlit app
def rapid_fire(selected_file_path, file_name):
    st.title('PDF MCQs and Answers (Rapid Fire)')

    if 'rapid_selected_options' not in st.session_state:
        st.session_state.rapid_selected_options = {}
    if 'rapid_mcqs' not in st.session_state:
        st.session_state.rapid_mcqs = []
    if 'start_time' not in st.session_state:
        st.session_state.start_time = None
    if 'rapid_submitted' not in st.session_state:
        st.session_state.rapid_submitted = False
    if 'current_question' not in st.session_state:
        st.session_state.current_question = 0
    if 'rapid_previous_file_path' not in st.session_state:
        st.session_state.rapid_previous_file_path = None

    if selected_file_path is not None:


        if selected_file_path != st.session_state.rapid_previous_file_path:
            # Clear the existing MCQs
            st.session_state.rapid_selected_options = {}
            st.session_state.rapid_mcqs = []
            st.session_state.start_time = None
            st.session_state.rapid_submitted = False
            st.session_state.current_question = 0
            # Generate new MCQs
            text = extract_text_from_pdf(selected_file_path)
            st.session_state.rapid_mcqs = generate_mcqs(text)
            # Update the previous file path
            st.session_state.rapid_previous_file_path = selected_file_path


        if not st.session_state.rapid_mcqs:
            text = extract_text_from_pdf(selected_file_path)
            st.session_state.rapid_mcqs = generate_mcqs(text)

        if st.session_state.start_time is None:
            if st.button('Start Timer'):
                st.session_state.start_time = datetime.now()

        if st.session_state.start_time:
            time_left = timedelta(minutes=1) - (datetime.now() - st.session_state.start_time)
            if time_left.total_seconds() > 0:
                st.header(f"Time left: {int(time_left.total_seconds())} seconds")
                if st.session_state.current_question < len(st.session_state.rapid_mcqs):
                    mcq = st.session_state.rapid_mcqs[st.session_state.current_question]
                    st.subheader(f"Question {st.session_state.current_question + 1}:")
                    st.write(f"{mcq['question']}")

                    if f'rapid_question_{st.session_state.current_question}' not in st.session_state:
                        st.session_state[f'rapid_question_{st.session_state.current_question}'] = None

                    selected_option = st.radio(
                        'Select an option:',
                        mcq['options'],
                        key=f'rapid_question_{st.session_state.current_question}',
                        on_change=freeze_question,
                        args=(st.session_state.current_question,)
                    )
                else:
                    st.session_state.rapid_submitted = True
            else:
                st.session_state.rapid_submitted = True

        if st.session_state.rapid_submitted:
            display_results()
