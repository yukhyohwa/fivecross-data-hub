import streamlit as st
import re
import pandas as pd
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

def get_game_folders():
    """
    Scans the sql_templates directory for subfolders (each representing a game/project).
    Returns a list of folder names.
    Rules: Folder names should be lowercase snake_case (e.g., 'slamdunk_overseas', 'onepiece_domestic').
    """
    if not os.path.exists(SQL_TEMPLATES_BASE_DIR):
        return []
    
    # Filter only directories
    items = os.listdir(SQL_TEMPLATES_BASE_DIR)
    folders = [d for d in items if os.path.isdir(os.path.join(SQL_TEMPLATES_BASE_DIR, d))]
    return sorted(folders)

def load_templates_for_game(game_folder):
    """
    Loads .sql files from a specific game folder.
    Returns sorted templates.
    """
    templates = []
    game_dir = os.path.join(SQL_TEMPLATES_BASE_DIR, game_folder)
    
    if not os.path.exists(game_dir):
        return []

    files = [f for f in os.listdir(game_dir) if f.endswith('.sql')]
    
    for filename in files:
        file_path = os.path.join(game_dir, filename)
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Metadata Parsing (Header)
            # Standard: -- Index. Title (key)
            first_line = content.split('\n')[0].strip()
            # Default values
            display_name = filename.replace('.sql', '')
            key = display_name
            index = 999
            
            header_match = re.search(r'--\s+(.*?)\s+\(([^()]+)\)\s*$', first_line)
            
            if header_match:
                # Update display name from header (e.g. "1. VIP Distribution")
                display_name = header_match.group(1).strip()
                # Do NOT overwrite key from header (which is just 'weeklyreport_vip')
                # We want key to be the filename 'g33002013_weeklyreport_vip'
                # key = header_match.group(2).strip() 
                
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
    
    # 1. Select Game (Folder)
    games = get_game_folders()
    if not games:
        st.warning(f"No game SQL folders found in {SQL_TEMPLATES_BASE_DIR}. Please create a folder like 'slamdunk_overseas' and add .sql files.")
        return

    # Use session state to remember selection if needed, but simple selectbox is fine
    selected_game = st.selectbox("Select Game Project", games, format_func=lambda x: x.replace('_', ' ').title())
    
    # determine stats based on folder name (heuristic: naming convention 'name_location')
    # fallback to 'overseas' if not specified
    if 'domestic' in selected_game:
        location = 'domestic'
    else:
        location = 'overseas' 

    # 2. Load Templates
    templates = load_templates_for_game(selected_game)
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
        placeholders = extract_placeholders(template['sql'])
        if placeholders:
            st.markdown("---")
            st.write("#### Configure Parameters")
            cols = st.columns(min(len(placeholders), 4))
            for i, p in enumerate(sorted(placeholders)):
                with cols[i % 4]:
                    val = st.date_input(f"{p}", key=f"d_{p}")
                    params[p] = val.strftime("%Y%m%d")

        st.markdown("---")
        
        # 4. Output Format Selection
        col1, col2 = st.columns([1, 3])
        with col1:
             export_format = st.radio("Export Format", EXPORT_FORMATS)
        
        # 5. Execution
        with col2:
            st.write("") # Spacer
            st.write("")
            if st.button("Run & Export", type="primary"):
                try:
                    final_sql = template['sql'].format(**params)
                    
                    o = create_odps_instance(location)
                    if not o:
                        st.stop()
                        
                    with st.spinner(f"Running query on {location.upper()} environment..."):
                        with o.execute_sql(final_sql).open_reader() as reader:
                            data = [record.values for record in reader]
                            columns = [col.name for col in reader._schema.columns]
                            df = pd.DataFrame(data, columns=columns)
                            
                            st.success(f"Success! {len(df)} rows.")
                            st.dataframe(df, use_container_width=True)
                            
                            # Handle Exports
                            file_base = f"{selected_game}_{template['key']}_{datetime.now().strftime('%Y%m%d')}"
                            
                            if export_format == 'CSV':
                                data_bytes = df.to_csv(index=False).encode('utf-8')
                                mime = "text/csv"
                                ext = "csv"
                            elif export_format == 'TXT':
                                data_bytes = df.to_csv(index=False, sep='\t').encode('utf-8')
                                mime = "text/plain"
                                ext = "txt"
                            elif export_format == 'Excel':
                                # Requires openpyxl
                                import io
                                buffer = io.BytesIO()
                                with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
                                    df.to_excel(writer, index=False)
                                data_bytes = buffer.getvalue()
                                mime = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                                ext = "xlsx"
                                
                            st.download_button(
                                label=f"Download .{ext}",
                                data=data_bytes,
                                file_name=f"{file_base}.{ext}",
                                mime=mime
                            )

                except Exception as e:
                    st.error(f"Error: {e}")
