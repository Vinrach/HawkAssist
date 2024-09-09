import streamlit as st
import fitz  # PyMuPDF
import nltk
import re
from nltk.tokenize import sent_tokenize
from nltk.tag import pos_tag
import random
from allPages.manage_test_results import insert_test_result



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
def generate_mcqs(text, num_questions=5):
    # Tokenize text into sentences
    sentences = sent_tokenize(text)
    mcqs = []

    # Iterate through sentences and generate MCQs
    for sentence in sentences:
        # Tokenize sentence into words and tag parts of speech
        words = nltk.word_tokenize(sentence)
        tagged_words = pos_tag(words)

        # Filter for nouns and proper nouns
        nouns = [word for word, pos in tagged_words if pos.startswith('NN')]

        # Ensure there are at least two nouns to create options
        if len(nouns) < 2:
            continue

        # Select random noun as answer
        answer = random.choice(nouns)

        # Generate distractors (wrong options) by shuffling other nouns
        other_nouns = [word for word in nouns if word != answer]
        random.shuffle(other_nouns)
        distractors = other_nouns[:min(3, len(other_nouns))]  # Choose up to 3 distractors

        # Remove special characters from options
        answer = re.sub(r'\W+', '', answer)
        distractors = [re.sub(r'\W+', '', option) for option in distractors]

        # Ensure options are unique
        options = list(set([answer] + distractors))

        # If the number of unique options is less than 4, skip this question
        if len(options) < 4:
            continue

        # Shuffle options to randomize their order
        random.shuffle(options)

        # Create MCQ question
        question = f"What is {sentence.replace(answer, '_____')}?"
        mcq = {'question': question, 'options': options, 'answer': answer}
        mcqs.append(mcq)

    return mcqs[:min(num_questions, len(mcqs))]  # Sample random questions

# Main mcqs function
def mcqs(selected_file_path, file_name):
    st.title('PDF MCQs and Answers')
    num_questions = 5
    
    if 'selected_options' not in st.session_state:
        st.session_state.selected_options = {}
    if 'mcqs' not in st.session_state:
        st.session_state.mcqs = []
    if 'submitted' not in st.session_state:
        st.session_state.submitted = False
    if 'previous_file_path' not in st.session_state:
        st.session_state.previous_file_path = None

    if selected_file_path is not None:

        if selected_file_path != st.session_state.previous_file_path:
            # Clear the existing MCQs
            st.session_state.mcqs = []
            st.session_state.submitted = False
            st.session_state.selected_options = {}
            # Generate new MCQs
            text = extract_text_from_pdf(selected_file_path)
            st.session_state.mcqs = generate_mcqs(text, num_questions=num_questions)

            # Update the previous file path
            st.session_state.previous_file_path = selected_file_path

        # if not st.session_state.mcqs:
        #     text = extract_text_from_pdf(selected_file_path)
        #     st.session_state.mcqs = generate_mcqs(text, num_questions=num_questions)

        st.header('MCQs')

        if not st.session_state.submitted:
            for i, mcq in enumerate(st.session_state.mcqs, 1):
                st.subheader(f"Question {i}:")
                st.write(f"{mcq['question'].replace('\n',' ')}")
                if f'question_{i}' not in st.session_state.selected_options:
                    selected_option = st.radio(
                        f'Select an option for Question {i}:',
                        mcq['options'],
                        key=f'question_{i}',
                        on_change=freeze_question,
                        args=(i,)
                    )
                else:
                    st.write(f"Selected Option for Question {i}: {st.session_state.selected_options[f'question_{i}']}")
                    st.radio(
                        f'Select an option for Question {i}:',
                        mcq['options'],
                        key=f'question_{i}',
                        index=mcq['options'].index(st.session_state.selected_options[f'question_{i}']),
                        disabled=True
                    )

            all_answered = len(st.session_state.selected_options) == len(st.session_state.mcqs)
            if all_answered and st.button('Submit'):
                st.session_state.submitted = True

                # Display answers and calculate score
                st.header('Answers and Score')
                score = 0
                total_questions = len(st.session_state.mcqs)
                for i, mcq in enumerate(st.session_state.mcqs, 1):
                    st.write(f"Question {i}: {mcq['question']}")
                    st.write(f"Answer: {mcq['answer']}")
                    if st.session_state.selected_options.get(f'question_{i}') == mcq['answer']:
                        score += 1
                st.write(f"Score: {score}/{total_questions}")
                insert_test_result(file_name,'mcqs', score)

        else:
            st.header('Answers and Score')
            score = 0
            total_questions = len(st.session_state.mcqs)
            for i, mcq in enumerate(st.session_state.mcqs, 1):
                st.write(f"Question {i}: {mcq['question']}")
                st.write(f"Answer: {mcq['answer']}")
                if st.session_state.selected_options.get(f'question_{i}') == mcq['answer']:
                    score += 1
            st.write(f"Score: {score}/{total_questions}")


def freeze_question(i):
    selected_option = st.session_state[f'question_{i}']
    if selected_option:
        st.session_state.selected_options[f'question_{i}'] = selected_option

