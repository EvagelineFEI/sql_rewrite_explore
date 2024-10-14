import json
import re
import subprocess
import pymysql

input_file = 'analyse0.sql'
analyse_num = 0
# 定义数据库连接参数

db_config = {
    'host': 'localhost',  # 或者是你的数据库服务器地址
    'user': 'root',       # 替换为你的数据库用户名
    'password': '123456',  # 数据库密码
    'database': 'fei_test0',  # 数据库名称
    'port': 3308          # 数据库端口
}

def restart_mysql_container(container_name):
    try:
        # 使用 docker restart 命令重启 MySQL 容器
        result = subprocess.run(['docker', 'restart', container_name], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        print(f"Container {container_name} restarted successfully.")
        return result.stdout.decode('utf-8')
    except subprocess.CalledProcessError as e:
        print(f"Failed to restart container {container_name}: {e.stderr.decode('utf-8')}")
        return None
    
def add_drop_if_exists(sql):
    # 正则表达式匹配 CREATE TABLE 语句中的表名
    table_pattern = re.compile(r"CREATE TABLE\s+`?([a-zA-Z0-9_]+)`?\s*\(", re.IGNORECASE)
    # 找到所有表名
    tables = table_pattern.findall(sql)
    # 构造新的 SQL 语句：先删除表，再创建表
    drop_statements = []
    for table in tables:
        drop_statements.append(f"DROP TABLE IF EXISTS `{table}`;")
    # 把原来的sql建表语句差分为单个sql; 将删除语句加在原来的 SQL 语句前
    schema_sqls = sql.split(';')
    for schema_sql in schema_sqls:
        if schema_sql != " ":
            drop_statements.append(schema_sql.strip()+';') 
    return drop_statements, schema_sqls
 
# 从文件中读取每条sql
# sql_data = []
# with open(input_file, 'r', encoding='utf-8') as file:
#     lines = file.readlines()
#     current_comment = None
#     current_query = []
#     queries = {}
    
#     for line in lines:
#         if line.startswith("--"):
#             if current_comment and current_query:
#                 entry = {
#                 "case source": current_comment,
#                 "sql": " ".join(current_query).strip()
#                 }
#                 sql_data.append(entry)
#                 current_query = []
#             current_comment = line[2:].strip()  # Extract the comment without '--'
#         else:
#             if line:  # Collect non-empty SQL lines
#                 current_query.append(line.strip())
#     # Adding the last query after the loop
#     if current_comment and current_query:
#         entry = {
#                 "case source": current_comment,
#                 "sql": " ".join(current_query).strip()
#                 }
#         sql_data.append(entry)

#     with open("single_exec_res.json", 'w') as json_file:
#         json.dump(sql_data, json_file, indent=4)

# 连接数据库，检查表是否存在，删表，建表
# 根据建表语句，提取关键词，生成测试数据；生成插入语句，填充到数据库里
wetune_unable = []
with open('wetune_unable.json', 'r', encoding='utf-8') as file:
    wetune_unable = json.load(file)
schema_sql = wetune_unable[analyse_num]["schema"]
sql_list, schema_sqls = add_drop_if_exists(schema_sql)
print(sql_list)
try:
    connection = pymysql.connect(**db_config)
    with connection.cursor() as cursor: 
        for sql in sql_list:
            cursor.execute(sql) # 一次只能执行一条哦
            # 提交更改
            connection.commit()
        print("Table created successfully")
except pymysql.MySQLError as e:
    print(f"Error: {e}")

# for 依次执行sql； 注意排除查询缓存影响；并记录sql的执行时间

 