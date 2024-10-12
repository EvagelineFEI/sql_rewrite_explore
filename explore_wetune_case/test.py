def format_sql_string(sql_response):
    # 去掉最前面的sql\n和两头的"""
    if sql_response.startswith("```sql\n"):
        sql_response = sql_response[7:]  # 去掉 "```sql\n"
    
    # 去掉末尾的```
    if sql_response.endswith("```"):
        sql_response = sql_response[:-3]
    
    # 将 \n 转化为实际的换行符
    formatted_sql = sql_response.replace("\\n", "\n")
    
    return formatted_sql

# 示例
gpt_response = '''```sql\nCREATE TABLE `child_themes`(\\n    `id` int(11) NOT NULL AUTO_INCREMENT,\\n    `parent_theme_id` int(11) NOT NULL,\\n    PRIMARY KEY (`id`),\\n    FOREIGN KEY (`parent_theme_id`) REFERENCES parent_themes(id)\\n);\n```'''
formatted_sql = format_sql_string(gpt_response)

print(formatted_sql)
