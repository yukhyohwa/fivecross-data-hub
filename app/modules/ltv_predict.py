import streamlit as st
import pandas as pd
from scipy.optimize import curve_fit
import numpy as np
import plotly.express as px
import requests
import os
import base64

# 定义幂函数模型
def power_function(num_day, a, b):
    return a * num_day**b

# Streamlit应用
def run():
  
    # 读取本地示例文件
    import os
    current_dir = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    file_path = os.path.join(current_dir, 'data', 'ltv预测文件.csv')
    
    try:
        with open(file_path, 'rb') as f:
            file_content = f.read()
            
        # 在Streamlit应用中创建下载按钮
        st.download_button(
            label="Download Upload Template",
            data=file_content,
            file_name="ltv_predict_sample.csv",
            mime="text/csv",
        )
    except FileNotFoundError:
        st.warning("Sample file not found in database/ directory.")
    
    # 文件上传
    uploaded_file = st.file_uploader("Upload CSV File", type="csv")

    if uploaded_file is not None:
        # 读取上传的文件
        data = pd.read_csv(uploaded_file)

        # 用户输入ecpnu和net_rate
        ecpnu = st.number_input("Enter ECPNU:", min_value=0.0, value=50.0, step=1.0)
        net_rate = st.number_input("Enter Net Rate:", min_value=0.0, value=0.35, step=0.01)

        if st.button("Calculate"):
            with st.spinner('Calculating...'):
                # 处理数据
                # 留存率预测部分
                retention_data_for_prediction = data.dropna(subset=['actual_rr'])
                retention_data_for_prediction = retention_data_for_prediction[retention_data_for_prediction['num_day'] != 1]
                x_data_retention = retention_data_for_prediction['num_day'].values - 1
                y_data_retention = retention_data_for_prediction['actual_rr'].values

                # 使用curve_fit拟合留存率数据
                params_retention, _ = curve_fit(power_function, x_data_retention, y_data_retention)
                a_fit_retention, b_fit_retention = params_retention

                # 计算留存率预测值
                y_pred_retention = np.where(data['num_day'] == 1, 1, power_function(data['num_day'] - 1, a_fit_retention, b_fit_retention))

                # ARPU预测部分
                arpu_data_for_prediction = data.dropna(subset=['actual_arpu'])
                x_data_arpu = arpu_data_for_prediction['num_day'].values
                actual_arpu = arpu_data_for_prediction['actual_arpu'].values

                # 初始化预测ARPU和累计误差数组
                predicted_arpu = np.zeros_like(data['actual_arpu'])
                cumulative_error = np.zeros_like(data['actual_arpu'])
                cumulative_actual_arpu = np.zeros_like(data['actual_arpu'])
                cumulative_predicted_arpu = np.zeros_like(data['actual_arpu'])

                # 预测ARPU
                for i in range(len(x_data_arpu)):
                    if i == 0:
                        predicted_arpu[i] = actual_arpu[i]
                    else:
                        history_length = min(i, 7)
                        predicted_arpu[i] = np.mean(actual_arpu[i-history_length:i]) * (1 - cumulative_error[i-1])
                    
                    cumulative_actual_arpu[i] = np.sum(actual_arpu[:i+1])
                    cumulative_predicted_arpu[i] = np.sum(predicted_arpu[:i+1])
                    cumulative_error[i] = cumulative_predicted_arpu[i] / cumulative_actual_arpu[i] - 1

                # 合并预测结果到DataFrame
                predictions_df = pd.DataFrame({
                    "Day Number": data['num_day'],
                    "Actual Retention Rate": data['actual_rr'],
                    "Predicted Retention Rate": y_pred_retention,
                    "Actual ARPU": data['actual_arpu'],
                    "Predicted ARPU": predicted_arpu
                })

                # 使用预测的ARPU和留存率计算每日的LTV
                ltv = np.cumsum(predictions_df["Predicted ARPU"] * predictions_df["Predicted Retention Rate"])

                # 将LTV添加到预测DataFrame中
                predictions_df["Predicted LTV"] = ltv

                # 计算每日的growth_rate
                last_ltv = predictions_df["Predicted LTV"].iloc[-1]
                growth_rate = last_ltv / predictions_df["Predicted LTV"]

                # 计算每日的Required LTV
                required_ltv = ecpnu / net_rate / growth_rate

                # 将Required LTV添加到DataFrame中
                predictions_df["Required LTV"] = required_ltv

                # 选择特定行（第1, 3, 7, 14, 30, 60, 90行）
                selected_rows = [0, 2, 6, 13, 29, 59, 89]  # DataFrame的行索引是从0开始的
                selected_df = predictions_df.iloc[selected_rows]

                col_left, col_right = st.columns(2)
            
                with col_left:
                    st.write("Full Forecast:", predictions_df)
            
                with col_right:
                    st.write("Benchmarks:", selected_df)


                # 创建三列，每列放一个图表
                col1, col2, col3 = st.columns(3)
            
                # 第一列：留存率折线图
                with col1:
                    fig1 = px.line(
                        predictions_df, 
                        x="Day Number", 
                        y=["Actual Retention Rate", "Predicted Retention Rate"],
                        title="Actual vs Predicted Daily Retention"
                    )
                    st.plotly_chart(fig1, use_container_width=True)
            
                # 第二列：ARPU折线图
                with col2:
                    fig2 = px.line(
                        predictions_df, 
                        x="Day Number", 
                        y=["Actual ARPU", "Predicted ARPU"],
                        title="Actual vs Predicted Daily ARPU"
                    )
                    st.plotly_chart(fig2, use_container_width=True)
            
                # 第三列：LTV折线图
                with col3:
                    fig3 = px.line(
                        predictions_df, 
                        x="Day Number", 
                        y=["Predicted LTV", "Required LTV"],
                        title="Predicted LTV vs Required LTV"
                    )
                    st.plotly_chart(fig3, use_container_width=True)



# 运行应用
if __name__ == "__main__":
    run()
