import json
import os


def beautify_json_file(file_path):
    with open(file_path, "r") as f:
        data = json.load(f)
    with open(file_path, "w") as f:
        json.dump(data, f, indent=4)


# Directory containing your JSON files
directory = "agents"

for filename in os.listdir(directory):
    if filename.endswith(".json"):
        file_path = os.path.join(directory, filename)
        beautify_json_file(file_path)
        print(f"Beautified {file_path}")
