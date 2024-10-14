import json
wetune_unable = []
with open("new_issue_copy.json", 'r', encoding='utf-8') as json_file:
    wetune_issue = json.load(json_file)
for entry in wetune_issue:
    if entry["wetune_result"] == "None":
        wetune_unable.append(entry)
    
with open("wetune_unable.json", 'w', encoding='utf-8') as out_file:
    json.dump(wetune_unable, out_file, ensure_ascii=False, indent=4)