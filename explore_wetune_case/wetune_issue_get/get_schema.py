from openai import OpenAI
import json
import os
# import tiktoken
# os.environ['http_proxy'] = 'http://192.168.10.3:7890'
# os.environ['HTTPS_PROXY'] = 'http://192.168.10.3:7890'
client = OpenAI(
    # This is the default and can be omitted
    api_key="your api key"
)

def query_turbo_model(prompt):
    message_ = [
    {"role": "system", "content": "You are a helpful assistant."},
    {"role": "user", "content": prompt}  # 将 prompt 放入 user 角色的消息中
    ]
    chat_completion = client.chat.completions.create(
        messages=message_,
        model="gpt-4o",
        temperature=0,
    )
    # print(chat_completion)
    return chat_completion.choices[0].message.content

def generate_prompt(sql_query):
    prompt = f"""
    Given the sql: {sql_query},
    you are required to give sql statement for schema construction based on the sql. For example:
    sql: SELECT `taggings`.`tag_id` FROM `taggings` INNER JOIN `tags` ON `tags`.`id` = `taggings`.`tag_id` WHERE `taggings`.`taggable_id` = 1234;
    sql statement for schema: 
    CREATE TABLE `tags`(
        `id` int(11) NOT NULL,
        PRIMARY KEY (`id`)
    ) ;
    CREATE TABLE `taggings`(
        `id` int(11) NOT NULL AUTO_INCREMENT,
        `tag_id` int(11) NOT NULL,
        `taggable_id` int(11)      DEFAULT NULL,
        `tagger_id` int(11)      DEFAULT NULL,
        FOREIGN KEY (tag_id) REFERENCES tags(id));
    Note: The only content that you give back to me is the sql for schema construction. Extra content is not allowed.
    """
    return prompt
def format_sql_string(sql_response):
    # 去掉最前面的sql\n和两头的"""
    if sql_response.startswith("```sql\n"):
        sql_response = sql_response[7:]  # 去掉 "```sql\n"
    # 去掉末尾的```
    if sql_response.endswith("```"):
        sql_response = sql_response[:-3]
    # 将 \n 转化为实际的换行符
    formatted_sql = sql_response.replace("\n", " ")
    return formatted_sql

new_data = []
with open("output.json", 'r', encoding='utf-8') as json_file:
    old_data = json.load(json_file)
for entry in old_data:
    sql = entry["original-sql"]
    prompt = generate_prompt(sql)
    schema = query_turbo_model(prompt)
    formatted_schema = format_sql_string(schema)
    # print(formatted_schema)
    entry["schema"] = formatted_schema
    entry["wetune_result"] = ""
    new_data.append(entry)
    
with open("new_issue.json", 'w', encoding='utf-8') as out_file:
    json.dump(new_data, out_file, ensure_ascii=False, indent=4)