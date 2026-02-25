import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import os
import sys

# Path to Client project for importing analytics services
CLIENT_PATH = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fivecross-data-client"))
if CLIENT_PATH not in sys.path:
    sys.path.append(CLIENT_PATH)

try:
    from src.core.services.analytics.ltv_service import LTVService
    from src.core.services.analytics.validator import DataValidator
except ImportError:
    st.error(f"Cannot link to Data Client at: {CLIENT_PATH}. Ensure the directory exists.")

def run():
    st.title("LTV Prediction 📈")
    st.markdown("Professional LTV projection using power-function retention fitting.")

    # 1. Template Download
    st.sidebar.subheader("Templates")
    sample_path = os.path.join(CLIENT_PATH, "data", "input", "ltv_predict_sample.csv")
    if os.path.exists(sample_path):
        with open(sample_path, 'rb') as f:
            st.sidebar.download_button("Download LTV Template", f, "ltv_template.csv", "text/csv")

    # 2. File Upload
    uploaded_file = st.file_uploader("Upload Growth Data (CSV)", type="csv")

    if uploaded_file is not None:
        data = pd.read_csv(uploaded_file)
        
        col1, col2 = st.columns(2)
        with col1:
            ecpnu = st.number_input("ECPNU (CPA):", value=50.0, step=1.0)
        with col2:
            net_rate = st.number_input("Net Rev Rate (e.g. 0.35):", value=0.35, step=0.01)

        if st.button("Run Analytics Engine", type="primary"):
            with st.spinner('Engine processing...'):
                try:
                    # Clean and Validate using Client logic
                    clean_df = DataValidator.clean_ltv_data(data)
                    
                    # Compute using Client service
                    service = LTVService(clean_df)
                    result_df = service.predict(ecpnu=ecpnu, net_rate=net_rate)
                    benchmarks = service.get_summary_benchmarks()

                    # --- UI Presentation ---
                    st.divider()
                    c_left, c_right = st.columns(2)
                    with c_left:
                        st.subheader("📊 Forecast Table")
                        st.dataframe(result_df, height=300)
                    with c_right:
                        st.subheader("🏆 Key Benchmarks")
                        st.table(benchmarks[['num_day', 'predicted_rr', 'predicted_ltv', 'required_ltv']])

                    # --- Charts ---
                    st.subheader("💹 Visualization")
                    tab1, tab2, tab3 = st.tabs(["Retention Curve", "ARPU Decay", "LTV vs Target"])
                    
                    with tab1:
                        fig1 = px.line(result_df, x="num_day", y=["actual_rr", "predicted_rr"], title="Retention Fitting")
                        st.plotly_chart(fig1, use_container_width=True)
                    
                    with tab2:
                        fig2 = px.line(result_df, x="num_day", y=["actual_arpu", "predicted_arpu"], title="ARPU Trend")
                        st.plotly_chart(fig2, use_container_width=True)
                        
                    with tab3:
                        fig3 = px.line(result_df, x="num_day", y=["predicted_ltv", "required_ltv"], title="ROI Projection")
                        st.plotly_chart(fig3, use_container_width=True)

                except Exception as e:
                    st.error(f"Engine Error: {e}")

if __name__ == "__main__":
    run()
