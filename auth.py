import streamlit as st

def login():
    st.sidebar.title("🔐 Είσοδος")
    username = st.sidebar.text_input("Όνομα χρήστη")
    password = st.sidebar.text_input("Κωδικός", type="password")
    if st.sidebar.button("Σύνδεση"):
        if username == "admin" and password == "1234":
            st.session_state["authenticated"] = True
        else:
            st.error("Λάθος στοιχεία σύνδεσης")
