import streamlit as st
import pandas as pd
from app.modules.udf_utils import execute_sql
import altair as alt

# --- Caching Data Fetching ---
# Using cache_data to prevent repetitive queries during session
@st.cache_data(ttl=3600)
def fetch_kpi_data(start_month, end_month):
    """
    Fetches KPI data from both Domestic and Overseas ODPS, merging them.
    Cached for 1 hour to improve performance on recurring view.
    """
    sql_query = f"""    
    SELECT a.app_id, 
        app_name, 
        region, 
        obt_start_date,
        data_date, 
        num_login_accounts_total,
        num_login_accounts_nuu,
        CAST(purchase AS DOUBLE) AS purchase
    FROM
    (
        SELECT CAST(app_id AS BIGINT) AS app_id, 
            SUBSTR(TO_DATE(month, 'yyyyMM'), 1, 10) AS data_date, 
            COUNT(DISTINCT lcm_id) AS num_login_accounts_total,
            COUNT(DISTINCT CASE WHEN user_type = 'nuu' THEN lcm_id ELSE NULL END) AS num_login_accounts_nuu,
            SUM(purchase) AS purchase
        FROM dm_platform.monthly_lcx_user_info
        WHERE month >= '{start_month}'
            AND month <= '{end_month}'
            AND is_water = '不是水'
        GROUP BY CAST(app_id AS BIGINT), SUBSTR(TO_DATE(month, 'yyyyMM'), 1, 10)
    ) a
    INNER JOIN
    (
        SELECT app_id, app_name, region, obt_start_date, NVL(obt_end_date, '2099-12-31') AS obt_end_date
        FROM dm_platform_dev.dim_app_info
        WHERE company = 'DeNA'
    ) b ON a.app_id = b.app_id
    WHERE SUBSTR(data_date, 1, 7) >= SUBSTR(obt_start_date, 1, 7) AND SUBSTR(data_date, 1, 7) <= SUBSTR(obt_end_date, 1, 7)
    ORDER BY app_id, data_date
    """
    
    frames = []
    
    # Domestic Fetch
    try:
        df_dom = execute_sql('odps', 'domestic', sql_query)
        if df_dom is not None and not df_dom.empty:
            df_dom['Environment'] = 'Domestic'
            frames.append(df_dom)
    except Exception as e:
        # Log via warning but don't crash
        st.warning(f"Domestic Data Fetch Warning: {e}")

    # Overseas Fetch
    try:
        df_ovs = execute_sql('odps', 'overseas', sql_query)
        if df_ovs is not None and not df_ovs.empty:
            df_ovs['Environment'] = 'Overseas'
            frames.append(df_ovs)
    except Exception as e:
        st.warning(f"Overseas Data Fetch Warning: {e}")

    if not frames:
        return pd.DataFrame()

    # Merge Results
    data = pd.concat(frames, ignore_index=True)
    
    # Standardize Column Names
    data.columns = ['Game ID', 'Game Name', 'Region', 'OBT Date', 'Month', 'MAU', 'NUU', 'Revenue', 'Environment']
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
            st.error("No data returned. Please check ODPS connections or date range.")
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
        cols_to_show = ['Game Name', 'Region', 'Month', 'Revenue', 'Revenue_List', 'MAU', 'MAU_List', 'NUU', 'NUU_List']
        
        st.dataframe(
            viz_df[cols_to_show],
            use_container_width=True,
            column_config={
                'Game Name': st.column_config.TextColumn("Game Project", width="medium"),
                'Region': st.column_config.TextColumn("Region", width="small"),
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
                    tooltip=['Game Name', 'Region', 'Month', alt.Tooltip('Revenue', format=',.0f')]
                ).interactive()
                st.altair_chart(rev_chart, use_container_width=True)
            
        with chart_tab2:
            if not data.empty:
                mau_chart = alt.Chart(data).mark_bar(opacity=0.7).encode(
                    x=alt.X('Month:T', axis=alt.Axis(format='%Y-%m')),
                    y=alt.Y('MAU', title='Monthly Active Users'),
                    color='Game Name',
                    tooltip=['Game Name', 'Region', 'Month', alt.Tooltip('MAU', format=',')]
                ).interactive()
                st.altair_chart(mau_chart, use_container_width=True)

    else:
        st.info("Plese click 'Generate Report' in the sidebar to load data.")

if __name__ == "__main__":
    run()
