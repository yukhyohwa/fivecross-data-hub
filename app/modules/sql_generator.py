import streamlit as st
def run():
	st.title('Cloud报表SQL生成器')

	# 用户输入表名
	table_name = st.text_input('输入表名', value="")

	# 用户粘贴字段信息
	st.subheader('字段信息')
	fields_info = st.text_area('在这里粘贴字段信息', value="", height=200)

	# 解析字段信息并创建选择小数位数的输入框
	fields = []
	name_concat_parts = []
	try:
		# 假设每行一个字段，字段之间由制表符或空格分隔
		for line in fields_info.split('\n'):
			if line.strip():  # 忽略空行
				parts = line.split('\t')
				if len(parts) == 3:
					field_name, field_type, field_desc = parts
					fields.append((field_name.strip(), field_type.strip(), field_desc.strip()))
					if '|' in field_desc:
						name_concat_parts.append(field_name.strip())
				else:
					st.error('请确保每行包含三个由制表符分隔的部分：字段名，字段类型，字段描述。')
					break
	except Exception as e:
		st.error('解析字段信息时出错。请检查输入格式。')

	# 如果字段是数字类型，则创建一个输入框来选择小数位数
	decimal_fields = [(name, desc) for name, typ, desc in fields if typ.lower() in ['double', 'float']]
	decimals = {name: st.number_input(f'为"{desc}"设置小数点保留位数', min_value=0, max_value=10, key=name) for name, desc in decimal_fields}

	# 生成SQL
	if st.button('生成 SQL'):
		select_clauses = []
		for field_name, field_type, field_desc in fields:
			alias = f'"{field_desc}"'  # 直接使用包含“|”的描述作为别名
			if field_type.lower() in ['double', 'float'] and field_name in decimals:
				select_clauses.append(f'ROUND({field_name}::NUMERIC, {decimals[field_name]}) AS {alias}')
			else:
				select_clauses.append(f'{field_name} AS {alias}')

		# 如果有字段描述包含“|”，则在SELECT语句末尾添加一个额外的字段
		if name_concat_parts:
			name_field = 'CONCAT_WS(\'.\', ' + ', '.join(name_concat_parts) + ') AS "name"' if len(name_concat_parts) > 1 else f'{name_concat_parts[0]} AS "name"'
			select_clauses.append(name_field)
		
		select_statement = ',\n    '.join(select_clauses)
		
		sql = f"""
	SELECT {select_statement}
	FROM {table_name}
	WHERE game_id = [app_id]
		AND day >= '[st]'
		AND day <= '[et]'
	ORDER BY group_type_name, group_id
	"""
		st.text_area("生成的 SQL", sql, height=200)
		
		
# 运行应用
if __name__ == "__main__":
    run()
