import streamlit as st
import pandas as pd
from app.modules.udf_utils import execute_sql
import altair as alt
from app.games_config import GAMES_CONFIG

# --- Caching Data Fetching ---
# Using cache_data to prevent repetitive queries during session
@st.cache_data(ttl=3600)
def fetch_kpi_data(start_month, end_month):
    """
    Fetches KPI data from both Domestic and Overseas ODPS, merging them.
    Also fetches from ThinkingData (TA) if configured.
    Cached for 1 hour to improve performance on recurring view.
    """
    # Load SQL from template
    import os
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    template_path_odps = os.path.join(base_dir, 'sql_templates', 'system', 'kpi_overview.sql')
    template_path_ta = os.path.join(base_dir, 'sql_templates', 'system', 'kpi_overview_ta.sql')
    
    with open(template_path_odps, 'r', encoding='utf-8') as f:
        raw_sql_odps = f.read()

    # If we have TA games, read TA template
    raw_sql_ta = ""
    if os.path.exists(template_path_ta):
         with open(template_path_ta, 'r', encoding='utf-8') as f:
            raw_sql_ta = f.read()
        
    # Format SQL for ODPS
    sql_query_odps = raw_sql_odps.format(start_month=start_month, end_month=end_month)
    
    frames = []
    
    # --- 1. ODPS Fetch (Domestic) ---
    try:
        df_dom = execute_sql('odps', 'domestic', sql_query_odps)
        if df_dom is not None and not df_dom.empty:
            df_dom['Environment'] = 'Domestic'
            df_dom['Source'] = 'ODPS'
            frames.append(df_dom)
    except Exception as e:
        # Log via warning but don't crash
        st.warning(f"Domestic Data Fetch Warning: {e}")

    # --- 2. ODPS Fetch (Overseas) ---
    try:
        df_ovs = execute_sql('odps', 'overseas', sql_query_odps)
        if df_ovs is not None and not df_ovs.empty:
            df_ovs['Environment'] = 'Overseas'
            df_ovs['Source'] = 'ODPS'
            frames.append(df_ovs)
    except Exception as e:
        st.warning(f"Overseas Data Fetch Warning: {e}")

    # --- 3. ThinkingData Fetch ---
    # Iterate over configured games to see if any use TA engine
    for key, config in GAMES_CONFIG.items():
        if config.get('engine') == 'ta':
            try:
                # Format TA SQL for this specific game
                # Assuming TA SQL template uses game-specific placeholders
                sql_query_ta = raw_sql_ta.format(
                    game_id=config.get('game_id'),
                    game_name=config.get('label'),
                    start_month=start_month,
                    end_month=end_month
                )

                # Execute against TA
                # Region/Environment for TA is usually handled by the URL in config
                # We can pass 'global' or the config's environment
                df_ta = execute_sql('ta', config.get('environment', 'global'), sql_query_ta)

                if df_ta is not None and not df_ta.empty:
                    # Standardize columns to match ODPS result
                    # ODPS result columns: app_id, app_name, region, obt_start_date, data_date, num_login_accounts_total, num_login_accounts_nuu, purchase
                    # TA SQL should return same alias
                    df_ta['Environment'] = 'Global (TA)'
                    df_ta['Source'] = 'ThinkingData'
                    frames.append(df_ta)
            except Exception as e:
                st.warning(f"ThinkingData Fetch Warning for {config.get('label')}: {e}")

    if not frames:
        return pd.DataFrame()

    # Merge Results
    data = pd.concat(frames, ignore_index=True)
    
    # Standardize Column Names
    # Note: Ensure the column order/names align with the ODPS query output
    # ODPS Query Selects: app_id, app_name, region, obt_start_date, data_date, num_login_accounts_total, num_login_accounts_nuu, purchase
    # We appended 'Environment' and 'Source'

    # Check if columns match expected length before renaming
    # Expected: 8 original + 2 added = 10 columns
    if len(data.columns) >= 10:
        # We rename the first 8 columns explicitly to display names, keeping the last ones
        data.rename(columns={
            'app_id': 'Game ID',
            'app_name': 'Game Name',
            'region': 'Region',
            'obt_start_date': 'OBT Date',
            'data_date': 'Month',
            'num_login_accounts_total': 'MAU',
            'num_login_accounts_nuu': 'NUU',
            'purchase': 'Revenue'
        }, inplace=True)

    return data

def run():
    st.title('KPI Dashboard 📊')
    
    # --- Sidebar Controls ---
    with st.sidebar:
        st.header("Report Parameters")
        with st.form(key='kpi_form'):
            start_month = st.text_input('Start Month (YYYYMM)', '202401', help="Format: 202401")
            end_month = st.text_input('End Month (YYYYMM)', '202405', help="Format: 202405")
            submit = st.form_submit_button("Generate Report", type="primary")

    # --- Main Logic ---
    # Trigger on submit
    if submit:
        st.divider()
        with st.spinner("Analyzing Global Data... (This may take a moment)"):
            data = fetch_kpi_data(start_month, end_month)
        
        if data.empty:
            st.error("No data returned. Please check ODPS/TA connections or date range.")
            return

        # 1. High Level Summary (Aggregated for Latest Month)
        latest_month = data['Month'].max()
        summary_df = data[data['Month'] == latest_month]
        
        st.markdown(f"### 🌏 Global Overview ({latest_month})")
        
        col1, col2, col3 = st.columns(3)
        total_rev = summary_df['Revenue'].sum()
        total_mau = summary_df['MAU'].sum()
        total_nuu = summary_df['NUU'].sum()
        
        col1.metric("Total Revenue", f"¥{total_rev:,.0f}")
        col2.metric("Total MAU", f"{total_mau:,.0f}")
        col3.metric("Total NUU", f"{total_nuu:,.0f}")
        
        st.divider()

        # 2. Detailed Game Performance Table with Sparklines
        st.subheader("🚀 Game Performance Matrix")
        
        # Prepare Data for Sparklines
        sorted_data = data.sort_values(['Game ID', 'Month'])
        
        # Latest snapshot
        latest_snapshot = sorted_data.drop_duplicates(subset=['Game ID'], keep='last').copy()
        
        # Group to get trends (lists)
        mau_trend = sorted_data.groupby('Game ID')['MAU'].apply(list).reset_index(name='MAU_List')
        nuu_trend = sorted_data.groupby('Game ID')['NUU'].apply(list).reset_index(name='NUU_List')
        rev_trend = sorted_data.groupby('Game ID')['Revenue'].apply(list).reset_index(name='Revenue_List')
        
        # Join trends back to snapshot
        viz_df = latest_snapshot.merge(mau_trend, on='Game ID')\
                                .merge(nuu_trend, on='Game ID')\
                                .merge(rev_trend, on='Game ID')
                                
        # Select and Rename for Display
        cols_to_show = ['Game Name', 'Region', 'Source', 'Month', 'Revenue', 'Revenue_List', 'MAU', 'MAU_List', 'NUU', 'NUU_List']
        
        st.dataframe(
            viz_df[cols_to_show],
            use_container_width=True,
            column_config={
                'Game Name': st.column_config.TextColumn("Game Project", width="medium"),
                'Region': st.column_config.TextColumn("Region", width="small"),
                'Source': st.column_config.TextColumn("Source", width="small"),
                'Month': st.column_config.TextColumn("Data Month", width="small"),
                'Revenue': st.column_config.NumberColumn("Revenue (Latest)", format="¥%d"),
                'Revenue_List': st.column_config.AreaChartColumn("Revenue Trend", y_min=0, width="small"),
                'MAU': st.column_config.NumberColumn("MAU (Latest)", format="%d"),
                'MAU_List': st.column_config.LineChartColumn("MAU Trend", y_min=0, width="small"),
                'NUU': st.column_config.NumberColumn("NUU (Latest)", format="%d"),
                'NUU_List': st.column_config.BarChartColumn("NUU Trend", y_min=0, width="small"),
            },
            hide_index=True,
            height=400
        )
        
        st.divider()

        # 3. Interactive Charts
        st.subheader("📈 Visualization Analysis")
        
        chart_tab1, chart_tab2 = st.tabs(["Revenue Breakdown", "User Growth"])
        
        with chart_tab1:
            if not data.empty:
                rev_chart = alt.Chart(data).mark_line(point=True).encode(
                    x=alt.X('Month:T', axis=alt.Axis(format='%Y-%m', title='Month')),
                    y=alt.Y('Revenue', title='Revenue (CNY)'),
                    color='Game Name',
                    tooltip=['Game Name', 'Region', 'Source', 'Month', alt.Tooltip('Revenue', format=',.0f')]
                ).interactive()
                st.altair_chart(rev_chart, use_container_width=True)
            
        with chart_tab2:
            if not data.empty:
                mau_chart = alt.Chart(data).mark_bar(opacity=0.7).encode(
                    x=alt.X('Month:T', axis=alt.Axis(format='%Y-%m')),
                    y=alt.Y('MAU', title='Monthly Active Users'),
                    color='Game Name',
                    tooltip=['Game Name', 'Region', 'Source', 'Month', alt.Tooltip('MAU', format=',')]
                ).interactive()
                st.altair_chart(mau_chart, use_container_width=True)

        # 4. Integrated Predictive Analytics (New)
        st.divider()
        st.subheader("🔮 Predictive Insights")
        pred_tab1, pred_tab2 = st.tabs(["MAU Forecasting", "LTV Benchmarks"])

        with pred_tab1:
            st.info("Showing projected growth based on current retention trends.")
            # Interface with Client output data
            base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            client_output_dir = os.path.abspath(os.path.join(base_dir, "..", "fivecross-data-client", "data", "output"))
            mau_reports = glob.glob(os.path.join(client_output_dir, "MAU_Report_*.xlsx"))
            if mau_reports:
                latest_mau = max(mau_reports, key=os.path.getmtime)
                df_mau = pd.read_excel(latest_mau)
                st.line_chart(df_mau, x='data_date', y='mau')
                st.caption(f"Source: {os.path.basename(latest_mau)}")
            else:
                st.warning("No MAU reports found in Client output. Run 'fetch' and 'predict' in Client first.")

        with pred_tab2:
            st.info("Real-time LTV decay and recovery analysis.")
            ltv_reports = glob.glob(os.path.join(client_output_dir, "LTV_Report_*.xlsx"))
            if ltv_reports:
                latest_ltv = max(ltv_reports, key=os.path.getmtime)
                df_ltv = pd.read_excel(latest_ltv)
                st.area_chart(df_ltv, x='num_day', y='predicted_ltv')
            else:
                st.warning("No LTV reports found in Client output.")

    else:
        st.info("Please click 'Generate Report' in the sidebar to load data.")

import glob
import os

if __name__ == "__main__":
    run()
