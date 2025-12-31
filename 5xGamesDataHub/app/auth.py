import toml
import streamlit as st
import os

CREDENTIALS_FILE = 'credentials.toml'

def load_credentials():
    """Load user credentials from TOML file."""
    if os.path.exists(CREDENTIALS_FILE):
        try:
            return toml.load(CREDENTIALS_FILE)
        except Exception as e:
            st.error(f"Error loading credentials: {e}")
            return {}
    return {}

def check_login(user_credentials, username, password):
    """Verify login credentials."""
    if username in user_credentials and user_credentials[username]['password'] == password:
        return True, user_credentials[username].get('permissions', [])
    return False, []

def login_component():
    """Reusable login component."""
    if 'logged_in' not in st.session_state:
        st.session_state['logged_in'] = False
        st.session_state['user_permissions'] = []

    if not st.session_state['logged_in']:
        st.title("Admin Login")
        with st.form("login_form"):
            username = st.text_input("Username")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                creds = load_credentials()
                success, permissions = check_login(creds, username, password)
                if success:
                    st.session_state['logged_in'] = True
                    st.session_state['user_permissions'] = permissions
                    st.success("Logged in successfully!")
                    st.rerun()
                else:
                    st.error("Invalid username or password.")
        return False
    return True
