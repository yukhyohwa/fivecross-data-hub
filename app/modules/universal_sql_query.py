import streamlit as st
import re
import pandas as pd
import io
from app.modules.odps_query import create_odps_instance
import os
from datetime import datetime

# ==========================================
# Core Configuration
# ==========================================
# Base path for all game SQL templates
BASE_APP_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQL_TEMPLATES_BASE_DIR = os.path.join(BASE_APP_DIR, 'sql_templates')

# Export formats supported
EXPORT_FORMATS = ['CSV', 'TXT', 'Excel']

# ==========================================
# Helper Functions
# ==========================================

from app.games_config import GAMES_CONFIG

# ==========================================
# Helper Functions
# ==========================================

def get_game_options():
    """
    Returns a list of game keys based on usage config.
    """
    return list(GAMES_CONFIG.keys())

def load_templates_for_game(game_key):
    """
    Loads .sql files from a specific game's configured folder.
    """
    config = GAMES_CONFIG.get(game_key)
    if not config:
        return []

    folder_name = config.get('folder')
    game_dir = os.path.join(SQL_TEMPLATES_BASE_DIR, folder_name)
    
    if not os.path.exists(game_dir):
        return []

    templates = []
    files = [f for f in os.listdir(game_dir) if f.endswith('.sql')]
    
    for filename in files:
        file_path = os.path.join(game_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Metadata Parsing (Header)
            first_line = content.split('\n')[0].strip()
            display_name = filename.replace('.sql', '')
            key = display_name
            index = 999
            
            header_match = re.search(r'--\s+(.*?)\s+\(([^()]+)\)\s*$', first_line)
            
            if header_match:
                display_name = header_match.group(1).strip()
                
                idx_match = re.match(r'(\d+)\.', display_name)
                if idx_match:
                    index = int(idx_match.group(1))

            # Description Parsing
            desc_match = re.search(r'-- Description:\s+(.*?)\n', content)
            description = desc_match.group(1).strip() if desc_match else "No description available."
            
            templates.append({
                "label": display_name,
                "key": key,
                "filename": filename,
                "sql": content,
                "description": description,
                "index": index
            })
        except Exception:
            continue

    templates.sort(key=lambda x: x['index'])
    return templates

def extract_placeholders(sql):
    return set(re.findall(r'\{(\w+)\}', sql))

# ==========================================
# Main Module Logic
# ==========================================

def run():
    st.title("Game SQL Library")
    
    # 1. Select Game (From Config)
    game_keys = get_game_options()
    if not game_keys:
        st.warning(f"No games configured in games_config.py.")
        return

    selected_key = st.selectbox(
        "Select Game", 
        game_keys, 
        format_func=lambda x: GAMES_CONFIG[x]['label']
    )
    
    # Get Config for selected game
    game_config = GAMES_CONFIG[selected_key]
    location = game_config['environment'] # 'domestic' or 'overseas' 
    location_cn = "海外" if (location == 'overseas' or location == 'overseas_v2') else "国内"

    # 2. Load Templates
    templates = load_templates_for_game(selected_key)
    if not templates:
        st.info("No SQL templates found in this folder.")
        return

    template_map = {t['label']: t for t in templates}
    selected_label = st.selectbox("Select Report Module", list(template_map.keys()))
    
    if selected_label:
        template = template_map[selected_label]
        st.info(f"**{template['description']}**")
        
        with st.expander("View SQL"):
            st.code(template['sql'], language='sql')
        
        # 3. Parameters
        params = {}
        
        # Auto-inject Game ID from config
        if 'game_id' in game_config:
            params['game_id'] = game_config['game_id']

        placeholders = extract_placeholders(template['sql'])
        
        # Filter out auto-injected keys (like game_id) from the user input form
        user_placeholders = {p for p in placeholders if p not in params}

        if user_placeholders:
            st.markdown("---")
            st.write("#### Configure Parameters")
            cols = st.columns(min(len(user_placeholders), 4))
            for i, p in enumerate(sorted(user_placeholders)):
                with cols[i % 4]:
                    # Robust Logic: Only treat params with 'day' or 'date' as Date inputs.
                    # Default all others (id, name, amount, etc.) to Text inputs.
                    name_lower = p.lower()
                    if 'day' in name_lower or 'date' in name_lower:
                        val = st.date_input(f"{p}", key=f"d_{p}")
                        params[p] = val.strftime("%Y%m%d") # Format to 8-digit Integer-String (e.g., 20250101)
                    else:
                        # Use text input for IDs, names, counters, etc.
                        val = st.text_input(f"{p}", key=f"t_{p}")
                        params[p] = val

        st.markdown("---")
        
        # 4. Output Format Selection
# 4. Execution Area
    if st.button("Run Query", type="primary"):
        try:
            final_sql = template['sql'].format(**params)
            
            # Debug: Show the actual SQL being run (to verify date formats)
            with st.expander("Debug: Final Executed SQL (Check Date Format)", expanded=False):
                st.code(final_sql, language='sql')

            # Extract project override if configured
            project_override = game_config.get('odps_project')
            
            o = create_odps_instance(location, project_override)
            if not o:
                st.stop()
                
            with st.spinner(f"Running query on {location}..."):
                with o.execute_sql(final_sql).open_reader() as reader:
                    data = [record.values for record in reader]
                    columns = [col.name for col in reader._schema.columns]
                    df = pd.DataFrame(data, columns=columns)
                    
                    # Store result in session state
                    st.session_state['uni_query_result'] = df
                    st.session_state['uni_query_game'] = selected_key
                    st.session_state['uni_query_template'] = template['key']
                    st.session_state['uni_query_time'] = datetime.now()
                    
                    st.rerun() # Rerun to refresh the state and show results

        except Exception as e:
            st.error(f"Error: {e}")

    # 5. Result Display & Export
    if 'uni_query_result' in st.session_state:
        cached_df = st.session_state['uni_query_result']
        cached_game = st.session_state.get('uni_query_game', selected_key)
        cached_temp = st.session_state.get('uni_query_template', template['key'])
        cached_time = st.session_state.get('uni_query_time', datetime.now())

        # Display Result
        st.markdown("---")
        st.success(f"Query Successful! {len(cached_df)} rows. (Time: {cached_time.strftime('%H:%M:%S')})")
        st.dataframe(cached_df, use_container_width=True)
        
        # Export Section
        st.subheader("Export Config")
        
        ec1, ec2 = st.columns([1, 4])
        
        with ec1:
            export_format = st.radio("Export Format", EXPORT_FORMATS, key="res_export_fmt")
            
        with ec2:
            st.write("")
            st.write("")
            
            # Prepare file name based on the CACHED info
            file_base = f"{cached_game}_{cached_temp}_{cached_time.strftime('%Y%m%d_%H%M%S')}"
            
            data_bytes = None
            mime = "text/plain"
            ext = "txt"
            
            if export_format == 'CSV':
                data_bytes = cached_df.to_csv(index=False).encode('utf-8')
                mime = "text/csv"
                ext = "csv"
            elif export_format == 'TXT':
                data_bytes = cached_df.to_csv(index=False, sep='\t').encode('utf-8')
                mime = "text/plain"
                ext = "txt"
            elif export_format == 'Excel':
                buffer = io.BytesIO()
                with pd.ExcelWriter(buffer, engine='openpyxl') as writer:
                    cached_df.to_excel(writer, index=False)
                data_bytes = buffer.getvalue()
                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                ext = "xlsx"
            
            st.download_button(
                label=f"📥 Download .{ext}",
                data=data_bytes,
                file_name=f"{file_base}.{ext}",
                mime=mime,
                type="secondary"
            )
