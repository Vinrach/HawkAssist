from langchain.chains import ConversationalRetrievalChain
from langchain_openai import ChatOpenAI
import re
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
import os



# Function to generate context-based questions and answers using LangChain
def generate_questions_and_answers(vectordb):
    if vectordb is None:
        return []
    if 'questions_and_answers' in st.session_state and len(st.session_state.questions_and_answers):
        print("questions_and_answers already exists in session state and not empty")
        print(f"questions_and_answers : {st.session_state.questions_and_answers}")
        print("returning questions_and_answers")
        return st.session_state.questions_and_answers
    else:
        print("questions_and_answers don't exist in session state ")
        print(f"{'questions_and_answers' in st.session_state}")
        qa = ConversationalRetrievalChain.from_llm(ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'), retriever=vectordb.as_retriever(search_kwargs={'k': 6}))
        chat_history = []

        # Generate questions and answers
        result = qa({"question": f"Generate 6 context-based questions and elaborative answers from the given text.", "chat_history": chat_history})
        result_str = str(result['answer'])
        pattern = r'Question: (.*?)\nAnswer: (.*?)\n'
        pattern2 = r'(\d+\.\s\*\*.*?\*\*)\n\s+-\s\*\*Answer:\*\*\s(.*?)\n'
        pattern3 = r'\*\*(.*?)\*\*\n\s*-\s*(.*?)\n'
        pattern4 = r'\*\*(.*?)\*\*\n\s*(.*?)\n'
        pattern5 = r'(\d+\.\s*.*?)\n-\s*(.*?)\n'
        pattern6 = r'(\d+\.\s*Question:\s*.*?)\n(Answer:\s*.*?)\n'

        questions_and_answers = []
        matches = re.findall(pattern, result_str, re.DOTALL)
        if not matches:
            matches = re.findall(pattern2, result_str, re.DOTALL)
        if not matches:
            matches = re.findall(pattern3, result_str, re.DOTALL)
        if not matches:
            matches = re.findall(pattern4, result_str, re.DOTALL)
        if not matches:
            matches = re.findall(pattern5, result_str, re.DOTALL)
        if not matches:
            matches = re.findall(pattern6, result_str, re.DOTALL)
        for match in matches:
            question, answer = match
            questions_and_answers.append({"question": question, "answer": answer})
            chat_history.append((question, answer))  # Update the chat history
        st.session_state.questions_and_answers = questions_and_answers
        print(questions_and_answers)
        return questions_and_answers
