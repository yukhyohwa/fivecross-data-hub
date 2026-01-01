import streamlit as st
from odps import ODPS
import pandas as pd
import numpy as np
import os
import traceback
import app.config as config

def run():
    st.title("Data Upload Tool (ODPS)")
    
    # Layout: Sidebar for critical configuration
    with st.sidebar:
        st.header("Environment Config")
        env_choice = st.radio("Select Environment", ["Domestic", "Overseas"], index=0)
        
    # --- 1. Credential Resolution ---
    try:
        if env_choice == "Domestic":
            creds = config.get_odps_credentials('domestic')
            # Domestic behavior: use its project
            default_project = creds.get('project', '') if creds else ''
        else:
            # Overseas behavior: Logic from legacy code preserved
            # Use V1 keys but V2 project often preferred for some datasets
            creds_v1 = config.get_odps_credentials('overseas')
            creds_v2 = config.get_odps_credentials('overseas_v2')
            
            creds = creds_v1
            # Fallback project
            default_project = creds_v2.get('project') if (creds_v2 and creds_v2.get('project')) else (creds_v1.get('project') if creds_v1 else '')
            
        if not creds:
             st.error("No credentials found in configuration.")
             st.info("Please check your .env file or config.py")
             return

        access_id = creds['access_id']
        access_key = creds['access_key']
        endpoint = creds['endpoint']
        
    except Exception as e:
        st.error(f"Credential Error: {e}")
        return

    # --- 2. File Selection ---
    st.info("Supported formats: CSV, Excel (.xlsx), Text")
    uploaded_file = st.file_uploader("Drag and drop file here", type=['csv', 'xlsx', 'xls', 'txt'])
    
    if uploaded_file:
        try:
            # Read Data
            df = None
            fname = uploaded_file.name
            fname_lower = fname.lower()
            
            if fname_lower.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(uploaded_file)
            elif fname_lower.endswith('.csv'):
                df = pd.read_csv(uploaded_file)
            elif fname_lower.endswith('.txt'):
                delimiter = st.text_input("Specify Delimiter", value=",")
                df = pd.read_csv(uploaded_file, sep=delimiter)
            
            if df is not None:
                # Sanitize NaN to None for ODPS
                df = df.replace({np.nan: None})
                
                st.write(f"### Preview: {fname}")
                st.caption(f"Shape: {df.shape[0]} rows, {df.shape[1]} columns")
                st.dataframe(df.head(), use_container_width=True)
                
                st.markdown("---")
                st.subheader("Target Settings")
                
                col1, col2 = st.columns(2)
                
                # Infer default table name
                # Clean filename (e.g. g3300..._name.csv -> name etc if needed, or just use raw)
                clean_name = os.path.splitext(fname)[0]
                
                with col1:
                    project_val = st.text_input("ODPS Project", value=default_project)
                    table_val = st.text_input("Table Name", value=clean_name)
                
                with col2:
                    # Session state memory for partition could be nice, but simple default is okay
                    partition_val = st.text_input("Partition Spec", value="game_id=13001230", help="e.g. ds='20230101' or leave empty")
                    overwrite_val = st.checkbox("Overwrite Data", value=True)

                if st.button("Upload to MaxCompute", type="primary"):
                    if not table_val:
                        st.error("Table name is required.")
                        st.stop()
                        
                    with st.spinner("Connecting and Uploading..."):
                        try:
                            o = ODPS(access_id, access_key, project_val, endpoint=endpoint)
                            
                            # Determine write args
                            write_args = {
                                "project": project_val,
                                "overwrite": overwrite_val
                            }
                            if partition_val.strip():
                                write_args["partition"] = partition_val
                                write_args["create_partition"] = True
                                
                            # Execute
                            o.write_table(table_val, df.values.tolist(), **write_args)
                            
                            st.success(f"Done! Uploaded to `{project_val}.{table_val}`")
                            st.balloons()
                            
                        except Exception as e:
                            st.error(f"MaxCompute Error: {e}")
                            st.code(traceback.format_exc())

        except Exception as e:
            st.error(f"File Processing Error: {e}")
