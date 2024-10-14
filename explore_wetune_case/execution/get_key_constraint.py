import re
import json
import re
import json

def extract_table_and_keys(create_table_statements):
    tables = {}
    foreign_keys = {}

    # 正则表达式匹配表名、主键和外键
    table_pattern = re.compile(r'CREATE TABLE\s+`?(\w+)`?\s*\(', re.IGNORECASE)
    primary_key_pattern = re.compile(r'PRIMARY KEY\s*\(`?(\w+)`?\)', re.IGNORECASE)
    foreign_key_pattern = re.compile(r'FOREIGN KEY\s*\(`?(\w+)`?\)\s*REFERENCES\s+`?(\w+)`?\s*\(`?(\w+)`?\)', re.IGNORECASE)
    
    # 遍历所有 CREATE TABLE 语句
    for statement in create_table_statements:
        table_match = table_pattern.search(statement)
        if table_match:
            table_name = table_match.group(1)
            tables[table_name] = {
                "primary_key": None, 
                "foreign_keys": [], 
                "referenced_by": []
            }

            # 提取主键
            primary_key_match = primary_key_pattern.search(statement)
            if primary_key_match:
                primary_key = primary_key_match.group(1)
                tables[table_name]["primary_key"] = primary_key

            # 提取外键及引用关系
            for fk_match in foreign_key_pattern.findall(statement):
                fk_column, ref_table, ref_column = fk_match
                tables[table_name]["foreign_keys"].append({
                    "column": fk_column,
                    "references_table": ref_table,
                    "references_column": ref_column
                })

                # 记录被引用的表
                if ref_table not in tables:
                    tables[ref_table] = {"primary_key": None, "foreign_keys": [], "referenced_by": []}
                tables[ref_table]["referenced_by"].append({
                    "table": table_name,
                    "column": fk_column,
                    "references_column": ref_column
                })

    return tables

def save_to_json(tables, output_file):
    with open(output_file, 'w') as f:
        json.dump(tables, f, indent=4)


# Example CREATE TABLE statements
create_table_statements = [
    """
    CREATE TABLE `posts`(`id` int(11) NOT NULL AUTO_INCREMENT,`topic_id` int(11) NOT NULL, PRIMARY KEY (`id`), UNIQUE (`topic_id`));
    """,
    """
    CREATE TABLE `topic_allowed_groups`(`id` int(11) NOT NULL AUTO_INCREMENT, `topic_id` int(11) NOT NULL,PRIMARY KEY (`id`), FOREIGN KEY (`topic_id`) REFERENCES posts(`topic_id`) ON DELETE CASCADE);
    """,
    """
    CREATE TABLE `topic_allowed_users`( `id` int(11) NOT NULL AUTO_INCREMENT, `topic_id` int(11) NOT NULL, `user_id` int(11) NOT NULL, PRIMARY KEY (`id`), FOREIGN KEY (`topic_id`) REFERENCES posts(`topic_id`) ON DELETE CASCADE);
    """
]


# 提取主键和外键关系并保存为 JSON 文件
tables = extract_table_and_keys(create_table_statements)
save_to_json(tables, "table_relationships.json")



# Extract keys and save to JSON
# tables = extract_table_and_keys(create_table_statements)
# save_to_json(tables, "table_relationships.json")
