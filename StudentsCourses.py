
import streamlit as st
import pandas as pd
from allPages.StudentsMainPage import std

@st.cache_data
def load_data():
    enrolled_courses_df = pd.read_csv("databasedata/tables/enrollments.csv")
    courses_df = pd.read_csv("databasedata/tables/courses.csv")
    return enrolled_courses_df, courses_df

def showStudentCourses(user_info):
    st.title("Hello " + user_info["name"])
    st.write("Welcome to the student main page!")

    
    if "view" not in st.session_state:
        st.session_state.view = "Courses"

    def render_view(view, enrolled_courses_df, courses_df):
        form_placeholder = st.empty()
        if view == "Courses":
            with form_placeholder.container():
                student_courses_id = enrolled_courses_df[enrolled_courses_df["student_id"] == user_info["id"]]
                print(student_courses_id)
                student_courses = courses_df[courses_df["course_id"].isin(student_courses_id["course_id"])]
                print(student_courses.values)

                st.subheader("Enrolled Courses")
                cols = st.columns(2)
                for idx, course in enumerate(student_courses.values, start=0):
                    col_idx = idx % 2
                    #print( idx, col_idx)
                    with cols[col_idx]:
                        with st.container():
                            metric_label = f"{idx + 1}"
                            metric_value = course[1]
                            st.metric(label=metric_label, value=metric_value)
                            if st.button(f"View Course Details", key=f"course_{course[0]}"):
                                show_courses = False
                                print(f"View Course Details {course[0]}")
                                st.session_state["course_id"] = course[0]
                                st.session_state.view = "Other View"
                                st.rerun()

        elif view == "Other View":
            form_placeholder.empty()
            std()
            if st.button("Back to Courses"):
                st.session_state.view = "Courses"
                st.rerun()
                        
    # Load data and call the render_view function with the current view
    enrolled_courses_df, courses_df = load_data()
    render_view(st.session_state.view, enrolled_courses_df, courses_df)