import streamlit as st
from odps import ODPS
import pandas as pd
import numpy as np
import os
import traceback
import app.config as config
import io

def run():
    st.title("Data Upload Tool (ODPS)")
    
    if 'maxcompute_project' not in st.session_state:
        st.session_state.maxcompute_project = "g13001230_dev"
    if 'partition' not in st.session_state:
        st.session_state.partition = "game_id=13001230"
    if 'overwrite' not in st.session_state:
        st.session_state.overwrite = True
    
    selected_environment = st.radio("Select Environment:", ["Domestic", "Overseas"])
    
    if selected_environment == "Domestic":
        creds = config.get_odps_credentials('domestic')
        if not creds:
             st.error("Missing Domestic Credentials")
             return
        access_id = creds['access_id']
        access_key = creds['access_key']
        project_name = creds['project']
        end_point = creds['endpoint']
    else:
        # Upload tool seemingly uses mixed credentials in original code:
        # V1 User (EasyQuery) with V2 Project (Download/Holo).
        # We try to reconstruct this behavior or use V2 full if logical.
        # Original: V1 Key, V2 Project.
        creds_v1 = config.get_odps_credentials('overseas') # V1
        creds_v2 = config.get_odps_credentials('overseas_v2') # V2
        
        if not creds_v1 or not creds_v2:
             st.error("Missing Overseas Credentials")
             return
             
        access_id = creds_v1['access_id']
        access_key = creds_v1['access_key']
        project_name = creds_v2['project'] # explicitly from V2
        end_point = creds_v1['endpoint']

    def extract_text_after_dash(file_name):
        base_name = os.path.splitext(file_name)[0]
        parts = base_name.split('-')
        if len(parts) > 1:
            return parts[-1]
        return None
        
    file_path = st.file_uploader("Upload File:", type=["csv", "txt"])
    
    if file_path is not None:
        try:
            if file_path.name.endswith('.csv'):
                df = pd.read_csv(file_path, sep=',', header=0, encoding='utf-8').replace(np.nan, None)
            elif file_path.name.endswith('.txt'):
                delimiter = st.text_input("Enter Delimiter (press Enter to confirm):", value=",")
                df = pd.read_csv(file_path, sep=delimiter, header=0, encoding='utf-8').replace(np.nan, None)
            
            st.write("Preview:")
            st.dataframe(df.head())
        
            default_table_name = extract_text_after_dash(file_path.name)
            if default_table_name is None:
                default_table_name = os.path.splitext(file_path.name)[0]
                
            st.header("MaxCompute Configuration")
            maxcompute_project = st.text_input("MaxCompute Project:", value=st.session_state.maxcompute_project)
            table_name = st.text_input("Table Name:", value=default_table_name)
            partition = st.text_input("Partition (leave empty for none):", value=st.session_state.partition)
            overwrite = st.checkbox("Overwrite Existing Data", value=st.session_state.overwrite)
            
            if st.button("Upload to MaxCompute"):
                st.session_state.maxcompute_project = maxcompute_project
                st.session_state.partition = partition
                st.session_state.overwrite = overwrite
                
                try:
                    o = ODPS(access_id, access_key, project_name, endpoint=end_point)
                    data_to_upload = df.values.tolist()
                    st.write("Connecting...")
                    
                    if partition:
                        st.write(f"Writing to {table_name} (partition: {partition}) in {maxcompute_project}...")
                        o.write_table(
                            table_name,
                            data_to_upload,
                            partition=partition,
                            create_partition=True,
                            project=maxcompute_project,
                            overwrite=overwrite
                        )
                    else:
                        st.write(f"Writing to {table_name} in {maxcompute_project}...")
                        o.write_table(
                            table_name,
                            data_to_upload,
                            project=maxcompute_project,
                            overwrite=overwrite
                        )
                    st.success("Upload Successful!")
                except Exception as e:
                    st.error(f"Upload Failed: {e}")
                    st.error(traceback.format_exc())
                    
        except Exception as e:
            st.error(f"Error reading file: {e}")
