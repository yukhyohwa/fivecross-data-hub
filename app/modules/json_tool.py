import streamlit as st
import json

def run():
    st.title("JSON Toolkit 🔧")
    
    # 2-Column Layout for Editor
    col1, col2 = st.columns([1, 1])
    
    with col1:
        st.subheader("Input")
        json_input = st.text_area("Paste JSON here", height=500, key="json_input")
        
    with col2:
        st.subheader("Output / Viewer")
        
        if json_input:
            try:
                parsed = json.loads(json_input)
                
                # Operations Bar
                action = st.radio("Display Mode", ["Pretty Print", "Compact", "Tree View"], horizontal=True)
                
                if action == "Pretty Print":
                    st.code(json.dumps(parsed, indent=4, ensure_ascii=False), language="json")
                elif action == "Compact":
                    st.code(json.dumps(parsed, separators=(',', ':'), ensure_ascii=False), language="json")
                elif action == "Tree View":
                    st.json(parsed)
                    
                st.success("Valid JSON ✅")
                
            except json.JSONDecodeError as e:
                st.error(f"Invalid JSON ❌\n{e}")
        else:
            st.info("Waiting for input...")

if __name__ == "__main__":
    run()
