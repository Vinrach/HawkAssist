import os
import pandas as pd
from datetime import date
import streamlit as st
from typing import Dict, Union

def retrieve_test_results():
    user_info = st.session_state.get('user_info', {})
    course_info = st.session_state.get('current_course_info', {})

    if not user_info or not course_info:
        st.warning("Error retrieving data from session state. No user_info or course_info specified.")
        return []

    user_id = user_info.get('id')
    course_id = course_info.get('course_id')

    file_path = os.path.join("databasedata", "tables", "test_results.csv")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return []

    if df.empty:
        st.warning("The test_results.csv file is empty.")
        return []

    filtered_df = df[(df['student_id'] == user_id) & (df['course_id'] == course_id)]
    print(f"test results found for {user_id} in {course_id} are : {filtered_df.shape[0]} ")
    if not filtered_df.empty:
        results = filtered_df.to_dict('records')
        return results
    else:
        return []

def insert_test_result(course_file_name, test_type, score):
    file_path = os.path.join("databasedata", "tables", "test_results.csv")
    user_info = st.session_state.get('user_info', {})
    course_info = st.session_state.get('current_course_info', {})
    if not course_file_name or not test_type:
        st.warning(f"Error entering data in File!. No file_name, test_type specified. {course_file_name} , {test_type} ")
        return None
    if not user_info or not course_info:
        st.warning("Error entering data in File!. No user_info or course_info specified.")
        return None
    if not score:
        score = 0

    course_id = course_info['course_id']
    user_id = user_info['id']
    course_name = course_info['name']

    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return None

    if df.empty:
        new_row = {'id': 1, 'student_id': str(user_id), 'course_id': str(course_id), 'course_name': course_name, 'course_file_name': course_file_name, 'test_type': test_type, 'test_id': 1, 'score': score, 'date': str(date.today())}
        df = pd.DataFrame([new_row])
    else:
        # Filter the DataFrame based on the combination of student_id, course_id, course_file_name, and test_type
        filter_condition = (df['student_id'] == user_id) & (df['course_id'] == course_id) & (df['course_file_name'] == course_file_name) & (df['test_type'] == test_type)
        # If there are existing test_id values for the given combination, get the maximum value
        existing_test_ids = df.loc[filter_condition, 'test_id']
        print(f"existing test ids are: {existing_test_ids}")
        next_test_id = existing_test_ids.max() + 1 if not existing_test_ids.empty else 1

        next_id = df['id'].max() + 1

        new_row = pd.DataFrame({'id': [next_id], 'student_id': [str(user_id)], 'course_id': [str(course_id)], 'course_name': [course_name], 'course_file_name': [course_file_name], 'test_type': [test_type], 'test_id': [next_test_id], 'score': [score], 'date': [str(date.today())]})
        df = pd.concat([df, new_row], ignore_index=True)

    try:
        with open(file_path, 'w') as file:
            df.to_csv(file, index=False)
    except Exception as e:
        st.error(f"Error writing to CSV file: {e}")
        return None

    print(new_row)
    return new_row


def retrieve_teacher_test_results():
    teacher_info = st.session_state.get('user_info', {})
    print(f"teacher info is {teacher_info}")

    courses_df = pd.read_csv("databasedata/tables/courses.csv")
    teacher_courses = courses_df[courses_df["teacher_id"].isin([teacher_info.get('id')])].to_dict('records')
    print(teacher_courses)
    if not teacher_info:
        st.warning("Error retrieving data from session state. No teacher_info")
        return []
    if not teacher_courses:
        st.warning("Teacher is offering no courses")
        return []
    course_ids = [course['course_id'] for course in teacher_courses]
    print(course_ids)


    file_path = os.path.join("databasedata", "tables", "test_results.csv")
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        st.error(f"Error reading CSV file: {e}")
        return []

    if df.empty:
        st.warning("The test_results.csv file is empty.")
        return []

    filtered_df = df[df['course_id'].isin(course_ids)]
    print(f"test results found are : {filtered_df.shape[0]} ")
    if not filtered_df.empty:
        results = filtered_df.to_dict('records')
        return results
    else:
        return []