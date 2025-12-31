import os
import io
import base64
import pandas as pd
import streamlit as st
from useful_udf import load_config, execute_sql
from pygwalker.api.streamlit import StreamlitRenderer


query_text = '''
SELECT *
FROM g13001230.dm_standard_daily_role_label 
WHERE game_id = 13001230
    AND day = '20230405'
ORDER BY total_payment DESC 
LIMIT 50
'''

# 读取 TOML 配置文件
current_dir = os.path.dirname(os.path.abspath(__file__))
config_path = os.path.join(current_dir, 'config.toml')
config = load_config(config_path)

# 缓存 Pygwalker 渲染器
@st.cache_resource
def get_pyg_renderer(df: pd.DataFrame) -> "StreamlitRenderer":
    # 如果需要保存图表配置，可以设置 `spec_io_mode="rw"`
    return StreamlitRenderer(df, spec_io_mode="rw")

def run():
    st.title("数据可视化探索")

    # 选择环境和运行引擎
    env = st.selectbox('选择环境', ('domestic', 'overseas'))
    engine = st.selectbox('选择运行引擎', ('odps', 'holo'))

    # 输入SQL并执行
    sql = st.text_area("输入SQL语句", key="my_text_area", value=query_text, height=None)
    
    if st.button('执行'):
        try:
            # 执行SQL并获取结果
            df = execute_sql(engine, env, sql, config)
        except Exception as e:
            st.error(f"查询执行失败: {e}")
            return

        # 下载CSV文件
        csv = df.to_csv(index=False, encoding='utf-8')
        b64_csv = base64.b64encode(csv.encode()).decode()
        href_csv = f'<a href="data:file/csv;base64,{b64_csv}" download="data.csv">下载 CSV 文件</a>'
        st.markdown(href_csv, unsafe_allow_html=True)
    
        # 下载XLSX文件
        xlsx = io.BytesIO()
        with pd.ExcelWriter(xlsx, engine='xlsxwriter') as writer:
            df.to_excel(writer, index=False, sheet_name='data')
        xlsx.seek(0)
        b64_xlsx = base64.b64encode(xlsx.read()).decode()
        href_xlsx = f'<a href="data:application/vnd.openxmlformats-officedocument.spreadsheetml.sheet;base64,{b64_xlsx}" download="data.xlsx">下载 Excel 文件</a>'
        st.markdown(href_xlsx, unsafe_allow_html=True)
        
        # 使用pygwalker展示数据
        renderer = get_pyg_renderer(df)
        renderer.explorer()
    
# 运行应用
if __name__ == "__main__":
    run()
