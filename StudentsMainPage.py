import streamlit as st
import pandas as pd
from allPages.mcqs import mcqs
from allPages.qna import showQnA
import os
import fitz
import io
from PIL import Image
import numpy as np
from streamlit_pdf_viewer import pdf_viewer
from langchain.chains import ConversationalRetrievalChain
from langchain.text_splitter import CharacterTextSplitter
from langchain_community.document_loaders import PyPDFLoader
from langchain_community.document_loaders import Docx2txtLoader
from langchain_community.document_loaders import TextLoader
from langchain_community.vectorstores import Chroma
from langchain_openai import ChatOpenAI
from langchain_openai import OpenAIEmbeddings
from allPages.calc_progress import display_progress
from allPages.rapid import rapid_fire




def create_docs(course_dir, choice, documents): 
        if(choice and course_dir):
            file_path = os.path.join(course_dir, choice)
            if choice.endswith(".pdf"):
                loader = PyPDFLoader(file_path)
            elif choice.endswith('.docx') or choice.endswith('.doc'):
                loader = Docx2txtLoader(file_path)
            elif choice.endswith('.txt'):
                loader = TextLoader(file_path)
            documents.extend(loader.load())
        return documents

# def display_pdf(file_path):
    # with open(file_path, "rb") as pdf_file:
    #     pdf_bytes = pdf_file.read()
    #     pdf_viewer(pdf_bytes)
    # with fitz.open(file_path) as pdf_file:
    #     for page_index in range(len(pdf_file)):
    #         page = pdf_file.load_page(page_index)
    #         pix = page.get_pixmap()
    #         st.image(pix, use_column_width=True)



def display_pdf(file_path):
    with open(file_path, "rb") as file:
        try:
            pdf_bytes = file.read()
            pdf_file = fitz.open(stream=pdf_bytes, filetype="pdf")
        except PermissionError:
            st.error("The PDF file is encrypted. Please provide the correct password.")
            return
        
        num_pages = len(pdf_file)
        st.write(f"Total pages: {num_pages}")

        # Create a placeholder for the PDF viewer
        pdf_viewer = st.empty()

        # Function to render and display a page
        def render_page(page_index):
            page = pdf_file.load_page(page_index)
            pix = page.get_pixmap()
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pdf_viewer.image(img, use_column_width=True)

        # Initial rendering of the first page
        render_page(0)

        # Add a button to navigate through pages
        prev_page, next_page = st.columns(2)
        current_page = 0

        def go_prev():
            nonlocal current_page
            if current_page > 0:
                current_page -= 1
                render_page(current_page)

        def go_next():
            nonlocal current_page
            if current_page < num_pages - 1:
                current_page += 1
                render_page(current_page)

        prev_page.button("Previous", on_click=go_prev)
        next_page.button("Next", on_click=go_next)     



def split_docs(documents):
    text_splitter = CharacterTextSplitter(chunk_size=1000, chunk_overlap=10)
    documents = text_splitter.split_documents(documents)
    return documents

def std():

    user_info = st.session_state["user_info"]
    course_id = st.session_state["course_id"]

    courses_df = pd.read_csv("databasedata/tables/courses.csv")
    course_info = courses_df[courses_df["course_id"] == course_id]
    print(course_info.values[0][1])
    os.environ["OPENAI_API_KEY"] = "sk-proj-suTqDV3cP6sQgBVhvqyfT3BlbkFJ8WyhjnxGqgcTg452I59T"

    # Get the absolute path to the project directory
    current_dir = os.path.dirname(os.path.abspath(__file__))
    # Go back to the parent directory
    parent_dir = os.path.join(current_dir, os.pardir)

    # Construct the path to the courses directory
    courses_dir = os.path.join(parent_dir, "databasedata", "courses")
    tabQnA, tabMCQs, tabRapidFire, tabChat, tabProgress, tabDoc = st.tabs([ "Questions and Answers", "MCQs", "Rapid fire", "Chat","Your Progress","View file"])

    # Check if the course_info DataFrame is not empty
    if not course_info.empty:
        st.session_state.current_course_info = course_info.iloc[0].to_dict()
        course_name = course_info.values[0][1]
        course_dir = os.path.join(courses_dir, course_name)

        file_names = []  # Initialize file_names list
        for file in os.listdir(course_dir):
            file_names.append(file)
        documents = []
        current_file_name = ""
        selected_file_path = ""
        if file_names:
            file_names.sort()
            choice = st.sidebar.radio(
                "Choose a file", file_names
            )
            for file_name in file_names:
                if choice == file_name:
                    documents = create_docs(course_dir, file_name, documents)
                    current_file_name = file_name
                    file_path = os.path.join(course_dir, file_name)
                    selected_file_path = file_path
                    break

        if documents == []:
            st.write("No files found in the course directory")
        elif documents:
            print( "You have selected this file: " + selected_file_path)
            splitted_documents = split_docs(documents)
            # Convert the document chunks to embedding and save them to the vector store
            vectordb = Chroma.from_documents(splitted_documents, embedding=OpenAIEmbeddings(), persist_directory="./data")
            vectordb.persist()
            #create questions
            # create our Q&A chain
            pdf_qa = ConversationalRetrievalChain.from_llm(
                    ChatOpenAI(temperature=0.7, model_name='gpt-3.5-turbo'),
                    retriever=vectordb.as_retriever(search_kwargs={'k': 6}),
                    return_source_documents=True,
                    verbose=False
                    )

            with tabProgress:
                display_progress(current_file_name)

            

            with tabChat:
                st.header("Chat with the document!")
                query = st.text_input("Enter your question:")
                chat_history = []
                if query:
                    with st.spinner("Generating answer..."):
                        result = pdf_qa.invoke({"question": query, "chat_history": chat_history})
                        st.write(result["answer"])
                        chat_history.append((query, result["answer"]))

            with tabQnA:
                showQnA(vectordb, current_file_name)
            with tabMCQs:
                mcqs(selected_file_path, current_file_name)

            with tabRapidFire:
                rapid_fire(selected_file_path, current_file_name)

            with tabDoc:
                st.write(f"The choice is {file_name}")
                file_path = os.path.join(course_dir, file_name)
                if file_name.endswith(".pdf"):
                    display_pdf(file_path)
                else:
                    with open(file_path, "r") as file:
                        text = file.read()
                        st.write(text)

    else:
        print("No course information found.")


    
