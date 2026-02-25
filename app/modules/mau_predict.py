import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import os
import sys
from app.modules.udf_utils import execute_sql

# Path to Client project for importing analytics services
CLIENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fivecross-data-client"))
if CLIENT_PATH not in sys.path:
    sys.path.append(CLIENT_PATH)

try:
    from src.core.services.analytics.mau_service import MAUService
    from src.core.services.analytics.validator import DataValidator
except ImportError:
    st.error(f"Cannot link to Data Client at: {CLIENT_PATH}.")

@st.cache_data
def execute_sql_query(engine, region, sql):
    return execute_sql(engine, region, sql)

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    return output

def run():
    st.title("MAU Prediction Tool 📈")
    st.markdown("Forecast Monthly Active Users based on retention and user acquisition.")

    st.subheader("1. Extract Historical Data", divider='blue')
    from app.games_config import GAMES_CONFIG
    
    with st.form(key='query_form'):
        col1, col2, col3 = st.columns(3)
        with col1:
            selected_key = st.selectbox("Select Project", list(GAMES_CONFIG.keys()), format_func=lambda x: GAMES_CONFIG[x]['label'])
            game_conf = GAMES_CONFIG[selected_key]
        with col2:
            start_month = st.text_input("History Start (YYYYMM)", "202401")
        with col3:
            end_month = st.text_input("History End (YYYYMM)", "202406")
        
        submit_btn = st.form_submit_button("Fetch Data", type="primary")

    if submit_btn:
        with st.status("Querying Engine..."):
            template_path = os.path.join(os.path.dirname(__file__), "..", "sql_templates", "system", "mau_predict_history.sql")
            with open(template_path, 'r', encoding='utf-8') as f:
                sql = f.read().format(app_id=game_conf['game_id'], start_month=start_month, end_month=end_month)
            
            df_raw = execute_sql_query('odps', game_conf['environment'], sql)
            
            if not df_raw.empty:
                st.session_state.mau_history = df_raw
                st.success(f"Retrieved {len(df_raw)} months of history.")
            else:
                st.error("No data found for this range.")

    if 'mau_history' in st.session_state:
        st.write("Historical Baseline:", st.session_state.mau_history)
        
        st.subheader("2. Configure Prediction", divider='green')
        col_p1, col_p2 = st.columns(2)
        with col_p1:
            months = st.slider("Months to Predict:", 1, 24, 12)
        with col_p2:
            growth = st.slider("New User Growth Factor:", 0.5, 3.0, 1.0, help="1.0 = Stability, >1.0 = Growth")

        if st.button("Run Forecasting Engine"):
            try:
                # Use Client Validator
                clean_df = DataValidator.clean_mau_data(st.session_state.mau_history)
                
                # Use Client Service
                service = MAUService(clean_df)
                result_df = service.predict(months_to_predict=months, growth_factor=growth)
                
                # --- Visuals ---
                st.divider()
                st.subheader("📊 Forecast Analytics")
                
                # Metric tiles
                last_m = result_df.iloc[-1]
                prev_m = result_df[~result_df['is_predicted']].iloc[-1]
                delta = (last_m['mau'] - prev_m['mau']) / prev_m['mau'] * 100
                st.metric("Proj. MAU (End)", f"{last_m['mau']:,.0f}", f"{delta:+.1f}% vs Current")

                # Chart
                fig = px.line(result_df, x='data_date', y=['mau', 'nuu'], 
                             title="MAU Growth Projection",
                             color_discrete_map={'mau': '#1f77b4', 'nuu': '#ff7f0e'})
                fig.add_vrect(x0=prev_m['data_date'], x1=last_m['data_date'], fillcolor="green", opacity=0.1, annotation_text="Forecast Zone")
                st.plotly_chart(fig, use_container_width=True)
                
                # Raw Table
                st.dataframe(result_df, use_container_width=True)
                
            except Exception as e:
                st.error(f"Prediction Error: {e}")

if __name__ == "__main__":
    run()
