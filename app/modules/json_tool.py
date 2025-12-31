import streamlit as st
import json

def run():
    st.title("JSON 编辑器")
    
    # 初始化 session state 中的 edited_json
    if "edited_json" not in st.session_state:
        st.session_state.edited_json = ""
    
    # 输入 JSON 文本
    
    json_input = st.text_area(":red[请输入JSON文本:]", height=100, key="input_json")
    
    
    # 尝试解析 JSON 文本
    if json_input:
        try:
            parsed_json = json.loads(json_input)
            st.success("JSON解析成功!")
            st.session_state.edited_json = json.dumps(parsed_json, indent=4)
        except json.JSONDecodeError as e:
            error_message = f"JSON解析错误: {str(e)}"
            st.error(error_message)
    
    # 显示解析后的 JSON 数据并允许编辑
    if st.session_state.edited_json:
        col1, col2 = st.columns(2)
    
        with col1:
            edited_json = st.text_area(":red[请在下方编辑JSON文本:]", st.session_state.edited_json, height=700, key="edited_json_area")
    
        with col2:
            try:
                parsed_edited_json = json.loads(st.session_state.edited_json)
                st.json(edited_json)
            except json.JSONDecodeError as e:
                st.error(f"编辑后的JSON解析错误: {str(e)}")
    
        # 更新 session state 中的 edited_json
        st.session_state.edited_json = edited_json
    
        # 验证和输出纯文本 JSON
        if st.button("验证并输出纯文本JSON"):
            try:
                parsed_edited_json = json.loads(st.session_state.edited_json)
                st.success("编辑后的JSON解析成功!")
                compact_json = json.dumps(parsed_edited_json, separators=(',', ':'))
                st.code(compact_json, language="json", line_numbers=False)
            except json.JSONDecodeError as e:
                st.error(f"编辑后的JSON解析错误: {str(e)}")
    
# 运行应用
if __name__ == "__main__":
    run()
