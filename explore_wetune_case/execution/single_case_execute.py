import json
import re
import subprocess
import pymysql
from faker import Faker
import random
from get_key_constraint import *
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
def get_sql_from_file():
    with open(input_file, 'r', encoding='utf-8') as file:
        lines = file.readlines()
        current_comment = None
        current_query = []
        queries = {}
        sql_data = []
        for line in lines:
            if line.startswith("--"):
                if current_comment and current_query:
                    entry = {
                    "case source": current_comment,
                    "sql": " ".join(current_query).strip()
                    }
                    sql_data.append(entry)
                    current_query = []
                current_comment = line[2:].strip()  # Extract the comment without '--'
            else:
                if line:  # Collect non-empty SQL lines
                    current_query.append(line.strip())
        # Adding the last query after the loop
        if current_comment and current_query:
            entry = {
                    "case source": current_comment,
                    "sql": " ".join(current_query).strip()
                    }
            sql_data.append(entry)

        with open("single_exec_res.json", 'w') as json_file:
            json.dump(sql_data, json_file, indent=4)

def build_test_db(sql_list):
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
    finally:
        if connection:
            connection.close()

def parse_create_table(sql):
    pattern = re.compile(r'`(\w+)` (\w+)\(?\d*\)?')
    columns = pattern.findall(sql)
    return columns

def generate_random_data(column_type, unique='False'):
    fake = Faker()
    if column_type == 'int':
        return random.randint(1, 200)  # 随机生成整数
    elif column_type == 'varchar':
        return fake.word()  # 随机生成单词
    elif column_type == 'date':
        return fake.date()  # 随机生成日期
    elif column_type == 'datetime':
        return fake.date_time()  # 随机生成日期时间
    elif column_type == 'float':
        return round(random.uniform(1.0, 100.0), 2)  # 随机生成浮点数，保留2位小数
    elif column_type == 'email':
        return fake.email()  # 随机生成电子邮件
    elif column_type == 'timestamp':
        return fake.unix_time()  # 随机生成时间戳
    else:
        return None
    
def connect_insert_data(table_name, columns, test_data):
    column_names = [col[0] for col in columns if col[0] != 'id']
    placeholders = ", ".join(["%s"] * len(column_names))
    insert_query = f"INSERT INTO {table_name} ({', '.join(column_names)}) VALUES ({placeholders})"
    # 将数据转换为元组形式以便执行插入
    data_to_insert = [
        tuple(row[col] for col in column_names)
        for row in test_data
    ]
    try:
        connection = pymysql.connect(**db_config)
        with connection.cursor() as cursor:
            # 批量插入数据
            cursor.executemany(insert_query, data_to_insert)
            connection.commit()
            print(f"Inserted {len(test_data)} rows into {table_name}")
    except pymysql.MySQLError as e:
        print(f"Error: {e}")
    finally:
        if connection:
            connection.close()      
    
            
            
def insert_test_data_single(schema_sqls, num_rows): # 目前实现的这个版本比较简易，不够灵活；如果要求数据类型灵活一些需要调用api和gpt联动
    table_relations = extract_table_and_keys(schema_sqls)
    constraintion = []
    constrainted_table = []
    for schema_sql in schema_sqls:
        if schema_sql == ' ':
            break
        pattern = re.compile(r'CREATE TABLE\s+`?(\w+)`?', re.IGNORECASE)
        match = pattern.search(schema_sql)
        if match:
            table_name = match.group(1)  # 提取表名
        else:
            print("-------------match table name failed-----------")   
        unique_pattern = re.compile(r'UNIQUE\s*\((.*?)\)', re.IGNORECASE)
        matches = unique_pattern.findall(schema_sql)
        unique_columns = [column.strip('`') for match in matches for column in match.split(',')]
        columns = parse_create_table(schema_sql)
        used_data = []
        if len(table_relations[table_name]["referenced_by"]) != 0:    
            test_data = []
            constraintion=[entry for entry in table_relations[table_name]["referenced_by"]]
            constrainted_table = [entry["table"] for entry in constraintion]
            # print("------------111111111111111----------------",constrainted_table)
            for _ in range(num_rows):
                row = {}
                for column_name, column_type in columns:
                    if column_name != 'id':  # 假设AUTO_INCREMENT列不需要生成
                        unique = False
                        if column_name in unique_columns:  # 检查是否需要唯一值
                            unique = True
                        generated_value = generate_random_data(column_type)
                        while unique and generated_value in used_data:
                            generated_value = generate_random_data(column_type, unique=unique)
                        if unique:
                            used_data.append(generated_value)
                        row[column_name] = generated_value
                        
                test_data.append(row)  

            #
            core_column = [entry["references_column"] for entry in constraintion]
            for c in core_column:
                value_set = [item[c] for item in test_data]
                for con in constraintion:
                    if con["references_column"] == c:
                        con["value_set"] = value_set
                        # print("------------con------------\n",con)  
        else:
            test_data = []
            # print(f"table_name: {table_name}, constrainted_table: {constrainted_table}")
            if table_name in constrainted_table:
                con_columns = [entry["column"] for entry in constraintion if entry["table"]==table_name]
                # print("------------111111111111111----------------",con_columns)
                for _ in range(num_rows):
                    row = {}
                    for column_name, column_type in columns:
                        if column_name in con_columns:
                            value_set = []
                            for entry in constraintion:
                                if entry["table"]==table_name and entry["column"]==column_name:
                                    value_set = entry["value_set"] 
                            generated_value = random.choice(value_set)
                            row[column_name] = generated_value
                        else:
                            if column_name != 'id':  # 假设AUTO_INCREMENT列不需要生成
                                unique = False
                                if column_name in unique_columns:  # 检查是否需要唯一值
                                    unique = True
                                generated_value = generate_random_data(column_type)
                                
                                while unique and generated_value in used_data:
                                    generated_value = generate_random_data(column_type, unique=unique)
                                if unique:
                                    used_data.add(generated_value)
                                row[column_name] = generated_value                   
                    test_data.append(row)  
            else:     
                for _ in range(num_rows):
                    row = {}
                    
                    for column_name, column_type in columns:
                        if column_name != 'id':  # 假设AUTO_INCREMENT列不需要生成
                            unique = False
                            if column_name in unique_columns:  # 检查是否需要唯一值
                                unique = True
                            generated_value = generate_random_data(column_type)
                            
                            while unique and generated_value in used_data:
                                generated_value = generate_random_data(column_type, unique=unique)
                            if unique:
                                used_data.add(generated_value)
                            row[column_name] = generated_value
                            
                    test_data.append(row)  
        # print("---------------test_data--------------\n",test_data)
        connect_insert_data(table_name, columns, test_data)

                  
# get_sql_from_file()

# 连接数据库，检查表是否存在，删表，建表
# 根据建表语句，提取关键词，生成测试数据；生成插入语句，填充到数据库里
wetune_unable = []
with open('wetune_unable.json', 'r', encoding='utf-8') as file:
    wetune_unable = json.load(file)
schema_sql = wetune_unable[analyse_num]["schema"]
sql_list, schema_sqls = add_drop_if_exists(schema_sql)


# save_to_json(tables, "table_relationships.json")

# build_test_db(sql_list)
insert_test_data_single(schema_sqls, 100)
# for 依次执行sql； 注意排除查询缓存影响；并记录sql的执行时间

 