import json

# Input file and output file names
input_file = 'issue.txt'
output_file = 'output.json'

# Initialize an empty list to hold the parsed data
data = []

# Read the input file line by line
with open(input_file, 'r', encoding='utf-8') as file:
    for line in file:
        # Split the line based on tab characters
        parts = line.split('\t')
        if len(parts) == 6:
            entry = {
                "case source": parts[1],
                "rewrite rule": parts[2],
                "link": parts[3],
                "original-sql": parts[4],
                "rewritten-sql": parts[5].strip()  # Remove any trailing newlines or spaces
            }
            data.append(entry)

# Write the data to a JSON file
with open(output_file, 'w', encoding='utf-8') as json_file:
    json.dump(data, json_file, ensure_ascii=False, indent=4)

