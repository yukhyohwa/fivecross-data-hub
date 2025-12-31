import streamlit as st
import re

def run():
    st.title('SQL Generator 🛠️')
    st.caption("Generate standard reporting SQL from field lists.")

    col1, col2 = st.columns([1, 2])
    
    with col1:
        table_name = st.text_input('Table Name', value="dm_platform.example_table")
        
        st.write("###### Input Format:")
        st.caption("field_name [tab] type [tab] description")
        
        fields_info = st.text_area('Field Definitions', height=400, 
                                   placeholder="user_id\tbigint\tUser ID\nrevenue\tdouble\tPayment")
                                   
    with col2:
        if not table_name or not fields_info:
            st.info("Please fill in table name and fields to generate SQL.")
            return

        # Parsing Logic
        fields = []
        parse_errors = []
        
        for line in fields_info.split('\n'):
            line = line.strip()
            if not line: continue
            
            parts = [p.strip() for p in re.split(r'[\t,]+', line) if p.strip()] # more flexible split
            
            if len(parts) >= 3:
                fields.append({
                    "name": parts[0],
                    "type": parts[1].lower(),
                    "desc": parts[2]
                })
            elif len(parts) > 0:
                parse_errors.append(line)
        
        if parse_errors:
            st.warning(f"Skipped {len(parse_errors)} malformed lines.")

        # Decimal Config
        decimal_fields = [f for f in fields if f['type'] in ['double', 'float', 'decimal']]
        decimals_map = {}
        
        if decimal_fields:
            st.write("###### Precision Settings")
            cols = st.columns(3)
            for i, f in enumerate(decimal_fields):
                with cols[i % 3]:
                    decimals_map[f['name']] = st.number_input(f"Decimals: {f['name']}", 0, 10, 2, key=f"dec_{f['name']}")
        
        # Generation
        selects = []
        for f in fields:
            alias = f['desc'].replace("'", "")
            col_expr = f['name']
            
            # Formatting logic
            if f['name'] in decimals_map:
                col_expr = f"ROUND({col_expr}::NUMERIC, {decimals_map[f['name']]})"
            
            selects.append(f"{col_expr} AS \"{alias}\"")
            
        sql = f"""SELECT 
    {', \n    '.join(selects)}
FROM {table_name}
WHERE game_id = [app_id]
  AND part_date >= '[start_date]'
ORDER BY 1"""

        st.subheader("Generated SQL")
        st.code(sql, language="sql")

if __name__ == '__main__':
    run()
