import pandas as pd
from odps import ODPS
import psycopg2
import streamlit as st
import app.config as config
from datetime import datetime
import io

def create_odps_conn(location):
    # Mapping location to config key
    # If location is 'overseas', download.py used the V2 project (g65002010)
    config_key = 'overseas_v2' if location == 'overseas' or location == '海外环境' else 'domestic'
    creds = config.get_odps_credentials(config_key)
    if not creds:
        return None
    return ODPS(creds['access_id'], creds['access_key'], creds['project'], creds['endpoint'])

def create_holo_conn(location):
    creds = config.get_hologres_credentials(location)
    if not creds:
        return None
    return psycopg2.connect(
        host=creds['host'],
        port=creds['port'],
        dbname=creds['dbname'],
        user=creds['user'],
        password=creds['password']
    )

def render(title="SQL Execution Tool"):
    st.title(title)

    env = st.selectbox('Select Environment', ('Domestic', 'Overseas'))
    engine = st.selectbox('Select Engine', ('ODPS', 'Hologres'))
    
    # Map selection to config keys
    loc_key = 'domestic' if env == 'Domestic' else 'overseas' # This maps to 'overseas' in general, but for ODPS inside create_odps_conn we handle v2
    
    default_sql = """SELECT *
FROM g13001230.dm_standard_daily_role_label 
WHERE game_id = 13001230
    AND day = '20230405'
ORDER BY total_payment DESC 
LIMIT 50"""

    sql = st.text_area("Input SQL", value=default_sql, height=300)

    if st.button('Execute'):
        try:
            df = None
            if engine == 'ODPS':
                odps_conn = create_odps_conn(loc_key) # Will use overseas_v2 logic
                if not odps_conn:
                    st.error("Credential configuration error.")
                    return
                with odps_conn.execute_sql(sql).open_reader() as reader:
                     # Using standard reader to dataframe
                    data = [record.values for record in reader]
                    columns = [col.name for col in reader._schema.columns]
                    df = pd.DataFrame(data, columns=columns)
            else:
                conn = create_holo_conn(loc_key)
                if not conn:
                    st.error("Credential configuration error.")
                    return
                # Use pandas read_sql or cursor
                df = pd.read_sql(sql, conn)
                conn.close()

            if df is not None:
                st.dataframe(df.head(100))
                
                # Downloads
                st.subheader("Downloads")
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.download_button("Download CSV", df.to_csv(index=False).encode('utf-8'), f"data_{datetime.now().strftime('%Y%m%d')}.csv", "text/csv")
                with col2:
                    st.download_button("Download Excel", to_excel(df), f"data_{datetime.now().strftime('%Y%m%d')}.xlsx", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
                with col3:
                    st.download_button("Download TXT", df.to_csv(index=False, sep='\t').encode('utf-8'), f"data_{datetime.now().strftime('%Y%m%d')}.txt", "text/plain")

        except Exception as e:
            st.error(f"Execution Error: {e}")

def to_excel(df):
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output.getvalue()
