import streamlit as st
import json
import os
import glob

# Path to the Client's task configurations
CLIENT_CONFIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "fivecross-data-client", "tasks", "configs"))

def run():
    st.title("Task Configuration Manager ⚙️")
    st.markdown("Manage and edit task configurations for the Data Client.")

    if not os.path.exists(CLIENT_CONFIG_DIR):
        st.error(f"Cannot find Client config directory at: {CLIENT_CONFIG_DIR}")
        return

    # 1. File Selection
    st.subheader("📁 Browse Configs")
    
    # Recursive search for .json files
    json_files = glob.glob(os.path.join(CLIENT_CONFIG_DIR, "**", "*.json"), recursive=True)
    relative_files = [os.path.relpath(f, CLIENT_CONFIG_DIR) for f in json_files]
    
    if not relative_files:
        st.warning("No JSON configurations found.")
        return

    selected_rel_path = st.selectbox("Select Task File to Edit", relative_files)
    full_path = os.path.join(CLIENT_CONFIG_DIR, selected_rel_path)

    # 2. File Content
    try:
        with open(full_path, 'r', encoding='utf-8') as f:
            content = f.read()
            original_json = json.loads(content)
    except Exception as e:
        st.error(f"Error reading file: {e}")
        return

    # 3. Editor
    st.divider()
    st.subheader(f"📝 Editing: {selected_rel_path}")
    
    # Show as text area for bulk editing
    json_text = st.text_area("JSON Content", value=json.dumps(original_json, indent=4, ensure_ascii=False), height=400)
    
    # Validation Logic
    valid_json = None
    try:
        valid_json = json.loads(json_text)
        st.success("JSON Syntax Valid ✅")
    except Exception as e:
        st.error(f"JSON Syntax Error: {e}")

    # 4. Save Button
    col1, col2 = st.columns([1, 4])
    with col1:
        if st.button("Save Changes", type="primary", disabled=(valid_json is None)):
            try:
                with open(full_path, 'w', encoding='utf-8') as f:
                    json.dump(valid_json, f, indent=4, ensure_ascii=False)
                st.toast("File saved successfully!", icon="✅")
                st.balloons()
            except Exception as e:
                st.error(f"Failed to save: {e}")

    # 5. Visual Preview
    st.divider()
    st.subheader("🔍 Structure Preview")
    st.json(valid_json if valid_json else original_json)

if __name__ == "__main__":
    run()
