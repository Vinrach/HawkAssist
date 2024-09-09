import streamlit as st
import os
import numpy as np
from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
from allPages.generate_questions import generate_questions_and_answers
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from allPages.manage_test_results import insert_test_result

def showQnA(vectordb, file_name):

    form_submitted = False
    def regenerate_onclick():
        nonlocal form_submitted 
        form_submitted = False
        regenerate_questions(vectordb)
    
    if(vectordb is None):
        st.warning("No documents were provided.")
        return
    if 'questions_and_answers' not in st.session_state:
        questions_and_answers = generate_questions_and_answers(vectordb)
        st.session_state.questions_and_answers = questions_and_answers
    if not st.session_state.questions_and_answers:
        questions_and_answers = regenerate_questions(vectordb)
    else:
        questions_and_answers = st.session_state.questions_and_answers
    if not questions_and_answers:
        st.warning("No questions and answers could be generated from the provided documents.")
        return
    print(questions_and_answers)
    user_answers = []
    st.header('Questions and Answers')

    form_placeholder = st.empty()
    with form_placeholder.container():
        if not form_submitted:
            with st.form("qna_form"):
                for i,qa_pair in enumerate(questions_and_answers,0):
                    question = qa_pair['question']
                    answer_key = f"user_answer_{i}"
                    if answer_key not in st.session_state:
                        st.session_state[answer_key] = ""
                        st.subheader("Question: " + question)
                        st.text_area(label="Enter your answer", height=200, key=f"{answer_key}")            
                submit = st.form_submit_button(label='Submit my Answers!')

        if submit:
            form_submitted = True

    if form_submitted:
        form_placeholder.empty()
        result_score = 0
        for i, qa_pair in enumerate(questions_and_answers, 0):
            answer_key = f"user_answer_{i}"
            user_answer = st.session_state[answer_key]
            if st.session_state[answer_key]:
                user_answer = st.session_state[answer_key]
            else:
                user_answer = "No answer provided"
            user_answers.append(user_answer)
            st.subheader(f"Question {i+1}: {qa_pair['question']}")
            st.write(f"Correct Answer: {qa_pair['answer']}")
            st.write(f"User Answer: {user_answers[i]}")
            score = calculate_cosine_similarity(qa_pair['answer'], user_answer)
            st.write(f"Your score out of 5:  {score}")
            result_score += score
        result_score = round(result_score / 5, 1)
        insert_test_result(file_name,'qna', result_score)
        st.subheader(f"Your total score for this test is: {result_score} / 5")

    
    st.button("Regenerate Questions!", on_click=regenerate_onclick)

    
            

def regenerate_questions(vectordb):
        st.session_state.questions_and_answers.clear()
        print("Regenerating questions")
        print(st.session_state.questions_and_answers)
        return generate_questions_and_answers(vectordb)

def calculate_cosine_similarity(text1,text2):
    if (text2 == "No answer provided"):
        return 0
    if (text1 == text2):
        return 5
    embeddings = OpenAIEmbeddings(openai_api_key=os.environ.get("OPENAI_API_KEY"))
    embedding1 = embeddings.embed_query(text1)
    embedding2 = embeddings.embed_query(text2)
    cosine_sim = np.dot(embedding1, embedding2) / (np.linalg.norm(embedding1) * np.linalg.norm(embedding2))
    print(f"Cosine similarity between '{text1}' and '{text2}': {cosine_sim}")
    cosine_sim= (cosine_sim * 100) - 70
    print(f"cosine similarity after multiplication {cosine_sim}")
    if cosine_sim <= 0:
        cosine_sim = 0
    elif cosine_sim >= 22:
        cosine_sim = cosine_sim -20
        cosine_sim = 4 + (cosine_sim/10 * 1)
    else:
        cosine_sim = (cosine_sim/30) * 5
    print(f"cosine similarity after multiplication {cosine_sim}")
    print(f"cosine similarity after round off {round(cosine_sim, 1)}")
    return round(cosine_sim, 1)