import streamlit as st
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
from io import BytesIO
import plotly.express as px
import openpyxl

# Streamlit应用
def run():
    # Set page title
    st.title("DAU and Revenue Prediction (Daily Retention)")
    
    st.subheader('1. Forecast Date Range', divider='rainbow')

    # Step 1: User Input
    start_date = st.date_input("Start Date", datetime.today())
    end_date = st.date_input("End Date", datetime.today())

    if start_date < end_date:
        # 步骤2：生成并下载数据模板
        num_days = (end_date - start_date).days + 1
        dates = pd.date_range(start_date, end_date)
        df_template = pd.DataFrame(dates, columns=["注册日期"])
        df_template["注册日期"] = df_template["注册日期"].dt.strftime('%Y-%m-%d')  # 确保日期格式为 yyyy-MM-dd
        df_template["NUU"] = np.nan  # 新增NUU空列
        df_template["ARPU"] = np.nan  # 新增ARPU空列
        for n in range(num_days):
            df_template[f"RR{n}"] = np.nan
        df_template["RR0"].fillna(1, inplace=True)  # RR0列填充1

        # 将DataFrame转换为Excel
        output = BytesIO()
        with pd.ExcelWriter(output, engine="openpyxl") as writer:
            df_template.to_excel(writer, index=False)
        output.seek(0)

        # Provide download button
        st.download_button(label="Download Data Template", data=output, file_name="dau_template.xlsx", mime="application/vnd.ms-excel")

        # Step 3: Upload filled xlsx
        uploaded_file = st.file_uploader("Upload Filled Excel File", type=["xlsx"])
        if uploaded_file is not None:
            # 读取Excel文件
            df_uploaded = pd.read_excel(uploaded_file)
            df_uploaded['注册日期'] = pd.to_datetime(df_uploaded['注册日期']).dt.strftime('%Y-%m-%d')

            # Show uploaded table
            st.write("Uploaded Table Content:", df_uploaded)

            # 步骤4：优化计算DAU及其构成的逻辑，空值处理并确保RRn列正确排序
            dau_components = pd.DataFrame(index=dates)
            dau_components['DAU'] = 0.0  # 初始化DAU列，保留小数位
            dau_components['NUU'] = 0.0  # 新增NUU列初始化
            dau_components['ARPU'] = 0.0  # 新增ARPU列初始化
            dau_components['收入'] = 0.0  # 新增收入列初始化

            # 动态标记需要添加的RRn列
            needed_rr_columns = set()

            for i, row in df_uploaded.iterrows():
                nuu = row['NUU']
                arpu = row['ARPU']
                dau_components.iloc[i, dau_components.columns.get_loc('NUU')] += nuu  # 记录NUU
                dau_components.iloc[i, dau_components.columns.get_loc('ARPU')] = arpu  # 记录ARPU
                # 仅处理存在的RRn值
                for col in [c for c in df_uploaded.columns if c.startswith('RR') and pd.notnull(row[c])]:
                    n = int(col[2:])  # 提取RR后的数字n
                    if n >= 0:  # 忽略RR0
                        needed_rr_columns.add(col)  # 标记这个列名为需要的

            # 将needed_rr_columns转换为列表并按照RRn的n值排序
            needed_rr_columns = sorted(list(needed_rr_columns), key=lambda x: int(x[2:]))

            # 为实际存在数据的列添加列，并初始化为NaN
            for col in needed_rr_columns:
                dau_components[col] = np.nan

            # 填充DAU及RRn列
            for i, row in df_uploaded.iterrows():
                nuu = row['NUU']
                for col in needed_rr_columns:
                    n = int(col[2:])
                    if pd.notnull(row[col]):
                        rr_value = row[col]  # 直接使用小数形式的RRn值
                        if i + n < len(dau_components):
                            dau_val = nuu * rr_value
                            dau_components.at[dau_components.index[i + n], 'DAU'] += dau_val
                            dau_components.at[dau_components.index[i + n], col] = dau_val

            # 计算收入
            dau_components['收入'] = dau_components['DAU'] * dau_components['ARPU']

            # 转换日期格式并确保DAU值为整数形式
            dau_components.index.name = '日期'
            dau_components.reset_index(inplace=True)
            dau_components['日期'] = dau_components['日期'].dt.strftime('%Y-%m-%d')

            # 最终输出时排除RR0列
            if 'RR0' in dau_components.columns:
                dau_components.drop('RR0', axis=1, inplace=True)

            # 将DAU、NUU、收入和RRn列转换为整数，并保留NaN
            dau_components['DAU'] = dau_components['DAU'].round().astype(pd.Int64Dtype())
            dau_components['NUU'] = dau_components['NUU'].round().astype(pd.Int64Dtype())
            dau_components['收入'] = dau_components['收入'].round().astype(pd.Int64Dtype())
            rr_columns = [col for col in needed_rr_columns if col != 'RR0']
            dau_components[rr_columns] = dau_components[rr_columns].apply(lambda x: x.round().astype(pd.Int64Dtype()), axis=0)

            st.subheader('2. Daily Forecast Results', divider='rainbow')
            
            # Show DAU and components
            st.write("DAU and Components:", dau_components)

            # Show DAU & NUU Chart
            fig_dau_nuu = px.line(dau_components, x='日期', y=['DAU', 'NUU'], title='DAU & NUU Trends', markers=True)
            st.plotly_chart(fig_dau_nuu, use_container_width=True)

            # Show Revenue Chart
            fig_revenue = px.line(dau_components, x='日期', y='收入', title='Daily Revenue Trends', markers=True)
            st.plotly_chart(fig_revenue, use_container_width=True)

            st.subheader('3. Monthly Forecast Results', divider='rainbow')
            
            # 生成按自然月分割的表格
            dau_components['日期'] = pd.to_datetime(dau_components['日期'])
            
            monthly_stats = dau_components.resample('M', on='日期').agg({
                'DAU': 'mean',
                'NUU': 'sum',
                'ARPU': 'mean',
                '收入': 'sum'
            }).round().astype(pd.Int64Dtype()).reset_index()
            
            monthly_stats['日期'] = monthly_stats['日期'].dt.to_period('M').astype(str)
            monthly_stats.columns = ['Date', 'Avg DAU', 'Total NUU', 'Avg ARPU', 'Total Revenue']

            # 生成按每30天分割的表格
            def resample_30d(df):
                periods = (df.shape[0] // 30) + (1 if df.shape[0] % 30 != 0 else 0)
                stats = []
                for i in range(periods):
                    start_idx = i * 30
                    end_idx = min((i + 1) * 30, df.shape[0])
                    period_data = df[start_idx:end_idx]
                    period_stats = period_data.agg({
                        'DAU': 'mean',
                        'NUU': 'sum',
                        'ARPU': 'mean',
                        '收入': 'sum'
                    }).round().astype(pd.Int64Dtype())
                    period_stats['日期'] = f'第{i + 1}个月'
                    stats.append(period_stats)
                return pd.DataFrame(stats)
            
            period_30d_stats = resample_30d(dau_components)
            period_30d_stats.reset_index(drop=True, inplace=True)
            period_30d_stats = period_30d_stats[['日期', 'DAU', 'NUU', 'ARPU', '收入']]
            period_30d_stats.columns = ['Date', 'Avg DAU', 'Total NUU', 'Avg ARPU', 'Total Revenue']

            # Show two tables
            col1, col2 = st.columns(2)
            with col1:
                st.write("Stats by Calendar Month:")
                st.dataframe(monthly_stats)
            with col2:
                st.write("Stats by 30-Day Period:")
                st.dataframe(period_30d_stats)

    else:
        st.error("End date must be after start date")

# 运行应用
if __name__ == "__main__":
    run()
