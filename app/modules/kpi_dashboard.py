import streamlit as st
import pandas as pd
from app.modules.udf_utils import execute_sql
import os

def run():
    # Streamlit 应用程序标题
    st.title('KPI Dashboard')
    
    # 表单输入
    with st.form(key='date_form'):
        start_month = st.text_input('Start Month (YYYYMM):', '202401')
        end_month = st.text_input('End Month (YYYYMM):', '202405')
        submit_button = st.form_submit_button(label='Calculate')
    
    # Cache handled by streamlit on function level usually, but here logic is inside run.
    # We can separate data fetching if needed, but keeping it simple.

    if submit_button:
        # 定义 SQL 查询语句
        sql_query = f"""    
        SELECT a.app_id, 
            app_name, 
            region, 
            obt_start_date,
            data_date, 
            num_login_accounts_total,
            num_login_accounts_nuu,
            CAST(purchase AS INT) AS purchase
        FROM
        (
            SELECT CAST(app_id AS INT) AS app_id, 
                SUBSTR(TO_DATE(month, 'yyyyMM'), 1, 10) AS data_date, 
                COUNT(DISTINCT lcm_id) AS num_login_accounts_total,
                COUNT(DISTINCT CASE WHEN user_type = 'nuu' THEN lcm_id ELSE NULL END) AS num_login_accounts_nuu,
                SUM(purchase) AS purchase
            FROM dm_platform.monthly_lcx_user_info
            WHERE month >= '{start_month}'
                AND month <= '{end_month}'
                AND is_water = '不是水'
            GROUP BY CAST(app_id AS INT), SUBSTR(TO_DATE(month, 'yyyyMM'), 1, 10)
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
    
        try:
            # 获取国内数据
            domestic_data = execute_sql('odps', 'domestic', sql_query)
        
            # 获取海外数据
            overseas_data = execute_sql('odps', 'overseas', sql_query)
        
            # 合并国内外数据
            data = pd.concat([domestic_data, overseas_data])
        
            # 重命名各列
            data.columns = ['Game ID', 'Game Name', 'Region', 'OBT Date', 'Month', 'MAU', 'NUU', 'Revenue']
            
            # 获取各游戏最新月份的数据
            latest_data = data.sort_values('Month').drop_duplicates(subset=['Game ID'], keep='last')
        
            # 准备图表数据
            chart_data = data[['Game ID', 'Month', 'MAU', 'NUU', 'Revenue']].copy()
        
            # 将MAU、NUU、收入数据转换为列表形式
            mau_series = chart_data.groupby('Game ID')['MAU'].apply(list).reset_index()
            nuu_series = chart_data.groupby('Game ID')['NUU'].apply(list).reset_index()
            revenue_series = chart_data.groupby('Game ID')['Revenue'].apply(list).reset_index()
        
            # 合并图表数据到最新数据
            latest_data = latest_data.merge(mau_series, on='Game ID', suffixes=('', '_series'))
            latest_data = latest_data.merge(nuu_series, on='Game ID', suffixes=('', '_series'))
            latest_data = latest_data.merge(revenue_series, on='Game ID', suffixes=('', '_series'))
        
            # 使用 Streamlit column_config 展示图表列
            st.subheader('1. Latest Month Data', divider='rainbow')
            st.dataframe(
                latest_data,
                column_config={
                    'Game ID': st.column_config.TextColumn('Game ID', width="small"),
                    'Game Name': st.column_config.TextColumn('Game Name', width="medium"),
                    'Region': st.column_config.TextColumn('Region', width="small"),
                    'OBT Date': st.column_config.TextColumn('OBT Date', width="small"),
                    'Month': st.column_config.TextColumn('Month', width="small"),
                    'MAU': st.column_config.NumberColumn('MAU', width="small"),
                    'NUU': st.column_config.NumberColumn('NUU', width="small"),
                    'Revenue': st.column_config.NumberColumn('Revenue', width="small", format="¥%d",),
                    'MAU_series': st.column_config.AreaChartColumn(
                        'MAU Trend', 
                        width="medium",
                        y_min=0,
                    ),
                    'NUU_series': st.column_config.BarChartColumn(
                        'NUU Trend', 
                        width="medium",
                        y_min=0
                    ),
                    'Revenue_series': st.column_config.LineChartColumn(
                        'Revenue Trend', 
                        width="medium",
                        y_min=0
                    )
                },
                hide_index=True
            )
            
            st.subheader('2. Detailed Monthly Data', divider='rainbow')
            st.dataframe(data, hide_index=True)
            
        except Exception as e:
            st.error(f"Error fetching data: {e}")

if __name__ == "__main__":
    run()
