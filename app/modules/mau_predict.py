# app.py
import streamlit as st
import pandas as pd
from io import BytesIO
import plotly.express as px
import os
from useful_udf import load_config, execute_sql

# 读取 TOML 配置文件
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.toml')
config = load_config(config_path)

@st.cache_data
def execute_sql_query(engine, region, sql, config):
    df = execute_sql(engine, region, sql, config)
    return df

def cache_dataframe(df):
    return df

def to_excel(df):
    output = BytesIO()
    with pd.ExcelWriter(output, engine='openpyxl') as writer:
        df.to_excel(writer, index=False, sheet_name='Sheet1')
    processed_data = output.getvalue()
    output.seek(0)
    return output

def validate_data(df):
    required_columns = ['月份', 'NUU', 'RUU', 'NUU次月留存率', 'OUU次月留存率', 'RUU次月留存率']
    if not all(column in df.columns for column in required_columns):
        return "缺少必要的列。请确保所有必要数据已经填写完整。"

    for index, row in df.iterrows():
        if any(not (0 <= row[col] <= 1) for col in ['NUU次月留存率', 'OUU次月留存率', 'RUU次月留存率']):
            return f"第{index+1}行的留存率数据不在0到1之间。"
    return None

def calculate_ouu(df):
    first_missing_ouu_index = df['OUU'].first_valid_index()
    if first_missing_ouu_index is None:
        return df

    for i in range(first_missing_ouu_index, len(df)):
        if i == 0:
            continue
        df.at[i, 'OUU'] = int(
            df.at[i-1, 'NUU'] * df.at[i-1, 'NUU次月留存率'] +
            df.at[i-1, 'OUU'] * df.at[i-1, 'OUU次月留存率'] +
            df.at[i-1, 'RUU'] * df.at[i-1, 'RUU次月留存率']
        )

    df['MAU'] = (df['NUU'] + df['OUU'] + df['RUU']).astype(int)
    df['RUU'] = (df['RUU']).astype(int)

    return df

def round_numeric_columns(df):
    numeric_columns = ['NUU', 'OUU', 'RUU']
    for column in numeric_columns:
        if column in df.columns:
            df[column] = df[column].fillna(0).astype(int)
    return df

def create_interactive_plot(df):
    fig = px.line(df, x='月份', y=['MAU', 'NUU', 'OUU', 'RUU'], 
                  labels={'value': '用户数', 'variable': '类型'},
                  title="月度活跃用户量变化")
    fig.update_layout(xaxis_title='月份', yaxis_title='用户数量',
                      yaxis=dict(range=[0, None]))
    fig.update_xaxes(tickangle=-45)
    return fig

def calculate_metrics(df):
    avg_mau = df['MAU'].mean()
    avg_nuu_retention = df['NUU次月留存率'].mean()
    avg_ouu_retention = df['OUU次月留存率'].mean()
    avg_ruu_retention = df['RUU次月留存率'].mean()
    return avg_mau, avg_nuu_retention, avg_ouu_retention, avg_ruu_retention

def run():
    st.title('基于分类用户次月留存率的MAU预测工具')
    st.subheader('1.获取历史参考值', divider='rainbow')
    
    from app.games_config import GAMES_CONFIG
    
    with st.form(key='query_form'):
        # environment = st.radio("执行环境", ('domestic', 'overseas')) # Derived from config now
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
             # Create options list
            game_options = list(GAMES_CONFIG.keys())
            selected_key = st.selectbox(
                "Select Game", 
                game_options, 
                format_func=lambda x: GAMES_CONFIG[x]['label']
            )
            # Get config
            game_conf = GAMES_CONFIG[selected_key]
            app_id = game_conf.get('game_id', '')
            environment = game_conf.get('environment', 'domestic')

        with col2:
            start_month = st.text_input("历史开始月份", "202401")
        with col3:
            end_month = st.text_input("历史结束月份", "202404")
        with col4:
            predict_end_month = st.text_input("预测截止月份", "202410")
        
        submit_button = st.form_submit_button(label='查询数据')
    
    df = pd.DataFrame()
    
    if submit_button:
        # Load SQL from template
        import os
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        template_path = os.path.join(base_dir, 'sql_templates', 'system', 'mau_predict_history.sql')
        
        with open(template_path, 'r', encoding='utf-8') as f:
            raw_sql = f.read()

        sql = raw_sql.format(app_id=app_id, start_month=start_month, end_month=end_month)
        df = execute_sql_query('odps', environment, sql, config)
        df = df.rename(columns={
            'data_date': '月份',
            'nuu': 'NUU',
            'ouu': 'OUU',
            'ruu': 'RUU',
            'nuu_retention_rate': 'NUU次月留存率',
            'ouu_retention_rate': 'OUU次月留存率',
            'ruu_retention_rate': 'RUU次月留存率'
        })
        
        all_months = pd.date_range(start=start_month + "01", end=predict_end_month + "01", freq='MS').strftime('%Y-%m-01').tolist()
        all_months_df = pd.DataFrame(all_months, columns=['月份'])
        df = all_months_df.merge(df, on='月份', how='left')
    
        st.write(df)
        
        df = cache_dataframe(df)
        
        excel_data = to_excel(df)
        st.download_button(
            label="下载数据模版",
            data=excel_data,
            file_name="MAU数据.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
        st.markdown("<span style='color: red;'>请在下载后, 填写需要预测月份的 NUU, RUU, NUU/OUU/RUU的次月留存率, 然后再点击下方的上传按钮进行上传, 即可预测. </span>", unsafe_allow_html=True)
    
    st.subheader('2.进行预测', divider='rainbow')
        
    uploaded_file = st.file_uploader("上传Excel文件", type=['xlsx'])
    
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        error_message = validate_data(df)
        if error_message:
            st.error(error_message)
        else:
            df = round_numeric_columns(df)
            st.markdown("<span style='color: red;'>已上传的数据(可以直接在表格中修改值)： </span>", unsafe_allow_html=True)
            st.session_state.df = st.data_editor(df)
            
    if 'df' in st.session_state and st.session_state.df is not None and st.button('进行预测'):
        st.session_state.df = calculate_ouu(st.session_state.df)
    
        col_df, col_metrics, col_plot = st.columns([2, 1, 2])
    
        with col_df:
            st.write("预测后的数据：", st.session_state.df)
    
        with col_plot:
            plot = create_interactive_plot(st.session_state.df)
            st.plotly_chart(plot, use_container_width=True)
    
        last_month_data = st.session_state.df.iloc[-1]
        first_month_data = st.session_state.df.iloc[0]
        
        delta_mau = (last_month_data['MAU'] - first_month_data['MAU']) / first_month_data['MAU'] * 100
        delta_nuu_retention = (last_month_data['NUU次月留存率'] - first_month_data['NUU次月留存率']) / first_month_data['NUU次月留存率'] * 100
        delta_ouu_retention = (last_month_data['OUU次月留存率'] - first_month_data['OUU次月留存率']) / first_month_data['OUU次月留存率'] * 100
        delta_ruu_retention = (last_month_data['RUU次月留存率'] - first_month_data['RUU次月留存率']) / first_month_data['RUU次月留存率'] * 100
        
        with col_metrics:
            st.metric(label="最后一个月 MAU", value=f"{last_month_data['MAU']:.0f}", delta=f"{delta_mau:.0f}%")
            st.metric(label="最后一个月 NUU 次月留存率", value=f"{last_month_data['NUU次月留存率']:.1%}", delta=f"{delta_nuu_retention:.0f}%")
            st.metric(label="最后一个月 OUU 次月留存率", value=f"{last_month_data['OUU次月留存率']:.1%}", delta=f"{delta_ouu_retention:.0f}%")
            st.metric(label="最后一个月 RUU 次月留存率", value=f"{last_month_data['RUU次月留存率']:.1%}", delta=f"{delta_ruu_retention:.0f}%")

if __name__ == "__main__":
    run()
