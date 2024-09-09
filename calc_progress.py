import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np
from allPages.manage_test_results import retrieve_test_results, retrieve_teacher_test_results

def display_progress(current_file_name = None):

    user_type = st.session_state["user_type"]
    if user_type == 'Student':
        test_results = retrieve_test_results()
    elif user_type == 'Teacher':
        test_results = retrieve_teacher_test_results()

    if not test_results:
        st.warning("No test results were found.")
        return
    
    if user_type == 'Student':
        print(current_file_name)
        st.subheader('Your Progress Report')

        # Create three columns
        col1,colEmpty, col2, col3 = st.columns([1,1,1,1])
        df = pd.DataFrame(test_results)
        with col1:
            st.write('Select the range of grades you want to observe')
            grade_selection = st.slider('Grade:', min_value=0, max_value=5, value=(0, 5))
        with col2:
            course_file_names = df['course_file_name'].unique().tolist()
            course_file_names.append('All')
            course_file_name_selection = st.radio('Select a lecture:', course_file_names, index=0)
        with col3:
            test_types = df['test_type'].unique().tolist()
            test_types.append('All')
            test_type_selection = st.radio('Select test type:', test_types, index=0)

        st.markdown('---') 
        

        mask = (df['score'].between(*grade_selection))

        if not course_file_name_selection == 'All':
            mask = mask & (df['course_file_name'] == course_file_name_selection)
        if not test_type_selection == 'All':
            mask = mask & (df['test_type'] == test_type_selection)
        number_of_result = df[mask].shape[0]
        st.markdown(f'*Available Results: {number_of_result}*')

        filtered_df = df[mask].sort_values(by=['course_name','course_file_name','test_type','test_id', 'score'])

        # --- PLOT BAR CHART
        score_counts = filtered_df['score'].value_counts().reset_index()
        score_counts.columns = ['score', 'count']
        # Create & display the bar chart
        bar_chart = px.bar(score_counts,
                    x='score',
                    y='count',
                    title='Score Distribution',
                    labels={'score': 'Score', 'count': 'Count'},
                    template='plotly_white')
        st.plotly_chart(bar_chart)

        total_grades_sum = df[mask]['score'].sum()
        percentage = (total_grades_sum / (df[mask].shape[0] * 5)) * 100
        st.write(f"Percentage of grades scored in {course_file_name_selection}: {percentage:.2f}%")
        st.write(filtered_df[['course_name', 'course_file_name', 'test_type', 'test_id', 'score', 'date']])


    elif user_type == 'Teacher':
        print(current_file_name)
        st.subheader('Students Progress Report')

        # Create three columns
        col1, colEmpty,col2, col3 = st.columns([1,1,1,1])
        df = pd.DataFrame(test_results)

        with col1:
            st.write('Select the range of grades you want to observe')
            grade_selection = st.slider('Grade:', min_value=0, max_value=5, value=(0, 5))
        with col2:
            course_names = df['course_name'].unique().tolist()
            course_names.append('All')
            course_name_selection = st.radio('Select a course you want to observe:', course_names, index=0)
            if(course_name_selection != 'All'):
                course_file_names = df[df['course_name'] == course_name_selection]['course_file_name'].unique().tolist()
                course_file_names.append('All')
                course_file_name_selection = st.radio('Select a lecture:', course_file_names, index=0)
        with col3:
            test_types = df['test_type'].unique().tolist()
            test_types.append('All')
            test_type_selection = st.radio('Select test type:', test_types, index=0)

        st.markdown('---') 

        mask = (df['score'].between(*grade_selection))

        if not course_name_selection == 'All':
            mask = mask & (df['course_name'] == course_name_selection)
            if not course_file_name_selection == 'All':
                mask = mask & (df['course_file_name'] == course_file_name_selection)
        if not test_type_selection == 'All':
            mask = mask & (df['test_type'] == test_type_selection)
        number_of_result = df[mask].shape[0]
        st.markdown(f'*Available Results: {number_of_result}*')

        filtered_df = df[mask].sort_values(by=['course_name','course_file_name','test_type','test_id', 'score'])

        # --- PLOT BAR CHART
        score_counts = filtered_df['score'].value_counts().reset_index()
        score_counts.columns = ['score', 'count']
        # Create & display the bar chart
        bar_chart = px.bar(score_counts,
                    x='score',
                    y='count',
                    title='Score Distribution',
                    labels={'score': 'Score', 'count': 'Count'},
                    template='plotly_white')
        st.plotly_chart(bar_chart)

        total_grades_sum = df[mask]['score'].sum()
        percentage = (total_grades_sum / (df[mask].shape[0] * 5)) * 100
        st.write(f"Percentage of grades: {percentage:.2f}%")
        st.write(filtered_df[['course_name', 'course_file_name', 'test_type', 'test_id', 'score', 'date']])
