import streamlit as st
import pandas as pd
from streamlit_navigation_bar import st_navbar
from allPages.StudentsCourses import showStudentCourses
from allPages.calc_progress import display_progress

# Set page title
st.set_page_config(page_title="Login Page", layout="wide",initial_sidebar_state="collapsed")
pages = ["Logout"]
styles = {
    "nav": {
        "background-color": "royalblue",
        "justify-content": "right",
    },
    "img": {
        "padding-right": "14px",
    },
    "span": {
        "color": "white",
        "padding": "14px",        
    },
    "ul": {
        "justify-content": "right",
    },
    "active": {
        "background-color": "white",
        "color": "var(--text-color)",
        "font-weight": "normal",
        "padding": "14px",
    }
}

options = {
    "show_menu": False,
    "show_sidebar": True,
}


def handleLogout():
    st.session_state["logged_in"] = False
    st.session_state["user_type"] = None
    st.session_state["user_data"] = None
    st.rerun()
    main()

# Loading CSV files
students_df = pd.read_csv("databasedata/tables/students.csv")
teachers_df = pd.read_csv("databasedata/tables/teachers.csv")

# function to check login credentials
def check_login(user_type, username, password):
    if user_type == "Student":
        user_data = students_df[(students_df["username"] == username) & (students_df["password"] == password)]
    else:
        user_data = teachers_df[(teachers_df["username"] == username) & (students_df["password"] == password)]

    if not user_data.empty:
        if user_type == "Student":
            user_info = {
                "name": user_data["name"].values[0],
                "id": user_data["student_id"].values[0],
                "username": user_data["username"].values[0]
            }
        else:
            user_info = {
                "name": user_data["name"].values[0],
                "id": user_data["teacher_id"].values[0],
                "username": user_data["username"].values[0]
            }
        return True, user_type, user_info
    else:
        return False, None, None

def show_nav_bar():
    page = st_navbar(
            pages,
            styles=styles,
            options=options,
            selected=None
        )
    if(page == "Logout"):
            handleLogout()

def main():
    # Create login form
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
        st.session_state["user_type"] = None

    if not st.session_state["logged_in"]:
        show_login_page()
    else:
        show_nav_bar()
        if st.session_state["user_type"] == "Student":
            show_student_main_page()
        else:
            show_teacher_main_page()


def show_login_page():
    st.title("Login")
    user_type = st.radio("Select user type", ["Student", "Teacher"])
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        login_success, user_type, user_info = check_login(user_type, username, password)
        if login_success:
            st.success("Login successful!")
            st.session_state["logged_in"] = True
            st.session_state["user_type"] = user_type
            st.session_state["user_info"] = user_info
            st.rerun()
        else:
            st.error("Invalid username or password")

def show_student_main_page():
    user_info = st.session_state["user_info"]
    showStudentCourses(user_info)

def show_teacher_main_page():
    user_info = st.session_state["user_info"]
    st.title("Hello " + user_info["name"])
    tabProgress, = st.tabs(["Progress"])
    if tabProgress:
        with tabProgress:
            display_progress()

if __name__ == "__main__":
    main()
