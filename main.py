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
    
    # Mapper for category display to internal value
    category_map = {
        "Query Tools": "Query Tools",
        "Data Management": "Data Management",
        "Analytics & Dashboard": "Analytics & Dashboard",
        "Predictions": "Predictions"
    }
    
    category_display = st.sidebar.selectbox("Category", list(category_map.keys()))
    category = category_map[category_display]
    
    module_selection = None
    
    # Mapper for tool display to internal value
    if category == "Query Tools":
        tool_map = {
            "Game SQL Library": "Game SQL Library",
            "SQL Execution Tool (Adv)": "SQL Execution Tool (Adv)"
        }
        tool_display = st.sidebar.radio("Tool", list(tool_map.keys()))
        module_selection = tool_map[tool_display]
        
    elif category == "Data Management":
        tool_map = {
            "Data Upload": "Data Upload",
            "JSON Utils": "JSON Editor"
        }
        tool_display = st.sidebar.radio("Tool", list(tool_map.keys()))
        module_selection = tool_map[tool_display]

    elif category == "Analytics & Dashboard":
        tool_map = {
            "KPI Dashboard": "KPI Dashboard"
        }
        tool_display = st.sidebar.radio("Tool", list(tool_map.keys()))
        module_selection = tool_map[tool_display]

    elif category == "Predictions":
        tool_map = {
            "LTV Prediction": "LTV Prediction",
            "DAU Prediction": "DAU Prediction",
            "MAU Prediction": "MAU Prediction"
        }
        tool_display = st.sidebar.radio("Tool", list(tool_map.keys()))
        module_selection = tool_map[tool_display]

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
            st.error("该模块没有 run() 入口点。")

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
