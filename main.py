import streamlit as st
import importlib
import sys
import os

# Add current directory to path so modules can be imported if needed,
# though we structure as a package 'app'.
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.auth import login_component

# Page Config
st.set_page_config(page_title="Data Platform", layout="wide")

def main():
    # Authentication
    if not login_component():
        return

    # Sidebar Navigation
    st.sidebar.title("Navigation")
    
    category = st.sidebar.selectbox("Category", [
        "Query Tools",
        "Data Management",
        "Analytics & Dashboard",
        "Predictions"
    ])
    
    module_selection = None
    
    if category == "Query Tools":
        module_selection = st.sidebar.radio("Tool", [
            "Game SQL Library",
            "SQL Execution Tool (Adv)"
        ])
    elif category == "Data Management":
        module_selection = st.sidebar.radio("Tool", [
            "Data Upload",
            "JSON Editor"
        ])
    elif category == "Analytics & Dashboard":
        module_selection = st.sidebar.radio("Tool", [
            "KPI Dashboard"
        ])
    elif category == "Predictions":
        module_selection = st.sidebar.radio("Tool", [
            "LTV Prediction",
            "DAU Prediction",
            "MAU Prediction"
        ])

    st.sidebar.markdown("---")
    st.sidebar.markdown(f"**User:** {st.session_state.get('username', 'Admin')}")

    # Dispatcher
    if module_selection == "Game SQL Library":
        from app.modules import universal_sql_query
        universal_sql_query.run()

    elif module_selection == "SQL Execution Tool (Adv)":
        from app.modules import sql_tool
        sql_tool.render()

    elif module_selection == "Data Upload":
        from app.modules import data_upload
        data_upload.run()
        
    elif module_selection == "JSON Editor":
        from app.modules import json_tool
        if hasattr(json_tool, 'run'):
            json_tool.run()
        else:
            st.error("Module has no run() entry point.")

    elif module_selection == "KPI Dashboard":
        from app.modules import kpi_dashboard
        kpi_dashboard.run()

    elif module_selection == "LTV Prediction":
        from app.modules import ltv_predict
        if hasattr(ltv_predict, 'run'):
            ltv_predict.run()

    elif module_selection == "DAU Prediction":
        from app.modules import dau_predict
        if hasattr(dau_predict, 'run'):
            dau_predict.run()

    elif module_selection == "MAU Prediction":
        from app.modules import mau_predict
        if hasattr(mau_predict, 'run'):
            mau_predict.run()

if __name__ == "__main__":
    main()
