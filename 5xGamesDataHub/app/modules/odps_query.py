import pandas as pd
from odps import ODPS
import streamlit as st
from datetime import datetime, time
import app.config as config
from app.utils import validate_date_format, validate_datetime_format, calculate_date_difference

def create_odps_instance(location):
    creds = config.get_odps_credentials(location)
    if not creds:
        st.error(f"No credentials found for location: {location}")
        return None
    return ODPS(creds['access_id'], creds['access_key'], creds['project'], creds['endpoint'])

@st.cache_resource
def load_config_from_odps(location, company_filter=None):
    o = create_odps_instance(location)
    if not o:
        return pd.DataFrame()
    
    query = '''SELECT location,project_id,table_name,table_name_cn,table_description,parameters,day_limit,REPLACE(sql_template,'"','') AS sql_template FROM dm_platform_dev.dim_table_query_info'''
    
    if company_filter:
        query += f" WHERE company = '{company_filter}';"
    else:
        query += " WHERE company != '';"

    try:
        with o.execute_sql(query).open_reader() as reader:
            records = [record.values for record in reader]
            columns = [col.name for col in reader._schema.columns]
            return pd.DataFrame(records, columns=columns)
    except Exception as e:
        st.error(f"Error loading configuration from ODPS: {e}")
        return pd.DataFrame()

def handle_special_parameters(param, value, index):
    unique_key = f"{param}_{index}"
    
    if '日期' in param:
        date_value = st.date_input(param, key=f"date_{unique_key}")
        return date_value.strftime('%Y%m%d')
        
    elif param == '开始时间':
        time_value = st.time_input(param, key=f"time_{unique_key}", step=60, value=time(0, 0))
        formatted_time = time_value.strftime('%H:%M:%S')
        return formatted_time if formatted_time.endswith(":00") else formatted_time + ":00"
        
    elif param == '结束时间':
        time_value = st.time_input(param, key=f"time_{unique_key}", step=60, value=time(23, 59))
        formatted_time = time_value.strftime('%H:%M:%S')
        if not formatted_time.endswith(":59"):
             formatted_time = formatted_time[:-2] + "59"
        return formatted_time
        
    elif param in ['LCX ID', '角色ID', 'DeNA ID']:
        choice = st.radio(f"Input method for {param}:", ('Text Input', 'Upload File'), key=f"choice_{unique_key}")
        if choice == 'Text Input':
            raw_input = st.text_input(f"Enter {param} (comma separated):", key=f"text_{unique_key}")
            if raw_input:
                ids = [id.strip() for id in raw_input.split(',')]
                formatted_ids = [f"'{id}'" if not id.startswith("'") else id for id in ids]
                return ','.join(formatted_ids)
            return ''
        else:
            uploaded_file = st.file_uploader(f"Upload file for {param}:", type=['csv', 'txt'], key=f"upload_{unique_key}")
            if uploaded_file is not None:
                df = pd.read_csv(uploaded_file, header=None)
                values = df.iloc[:,0].apply(lambda x: f"'{x}'" if not str(x).startswith("'") else str(x)).tolist()
                return ','.join(values)
            return ''
    else:
        return st.text_input(param, value, key=f"param_{unique_key}")

def render(company_filter=None, title='ODPS Query Tool'):
    st.title(title)

    if st.button('Refresh Cache'):
        st.cache_resource.clear()
        st.success('Cache refreshed!')

    config_df = load_config_from_odps('domestic', company_filter)
    
    if config_df.empty:
        st.warning("No configuration data found.")
        return

    project_list = config_df['project_id'].unique()
    selected_project = st.selectbox('Select Project', project_list)
    
    project_tables = config_df[config_df['project_id'] == selected_project]
    table_display_names = [f"{row['table_name_cn']}-{row['table_name']}" if row['table_name_cn'] else row['table_name'] for index, row in project_tables.iterrows()]
    
    selected_table_display = st.selectbox('Select Table', table_display_names)
    selected_table = selected_table_display.split("-")[-1]
    
    row_data = project_tables[project_tables['table_name'] == selected_table].iloc[0]
    st.write(f"Description: {row_data['table_description']}")
    
    selected_location = row_data['location']
    # Map chinese location to config keys if needed, but config handles it.
    
    o = create_odps_instance(selected_location)
    table_config = config_df[(config_df['project_id'] == selected_project) & (config_df['table_name'] == selected_table)].iloc[0]
    
    params = table_config['parameters'].split(';') if isinstance(table_config['parameters'], str) else []
    sql_template = table_config['sql_template']
    day_limit = table_config['day_limit']

    param_values, errors = {}, []

    for index, param in enumerate(params):
        processed_value = handle_special_parameters(param, '', index)
        if processed_value is not None:
            param_values[param] = processed_value

    # Validate dates
    start_date = param_values.get('开始日期', '')
    end_date = param_values.get('结束日期', '')
    if start_date and end_date:
        if calculate_date_difference(start_date, end_date) > day_limit:
            errors.append(f'Date range cannot exceed {day_limit} days.')

    for error in errors:
        st.error(error)

    if st.button('Run Query') and not errors:
        try:
            query = sql_template.format(**param_values)
            
            display_query = query if len(query) <= 2000 else f"{query[:2000]}... (truncated)"
            st.text("Executing SQL:")
            st.code(display_query, language='sql')
            
            with o.execute_sql(query).open_reader() as reader:
                data = [record.values for record in reader]
                columns = [col.name for col in reader._schema.columns]
                df = pd.DataFrame(data, columns=columns)
                st.dataframe(df)
                
                # Download button
                csv_data = df.to_csv(index=False).encode('utf-8')
                st.download_button(
                    "Download CSV",
                    csv_data,
                    f"query_result_{datetime.now().strftime('%Y%m%d%H%M%S')}.csv",
                    "text/csv"
                )
        except Exception as e:
            st.error(f"Query Execution Failed: {e}")
