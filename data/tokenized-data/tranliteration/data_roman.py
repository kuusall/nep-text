import pandas as pd
import json

# Function to load JSONL (JSON lines) file into a list of dictionaries
def load_json_lines(file_path):
    with open(file_path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]

# File paths
test_path = "nep_test.json"
valid_path = "nep_valid.json"
train_path = "nep_train.json"

# Load the JSONL files
test_data = load_json_lines(test_path)
valid_data = load_json_lines(valid_path)
train_data = load_json_lines(train_path)

# Convert to DataFrames and keep only native word and english word
df_test = pd.DataFrame(test_data)[["native word", "english word"]]
df_valid = pd.DataFrame(valid_data)[["native word", "english word"]]
df_train = pd.DataFrame(train_data)[["native word", "english word"]]

# Combine datasets
df_combined = pd.concat([df_test, df_valid,df_train], ignore_index=True)

# Save to CSV with exact words preserved
df_combined.to_csv("neplai_roman_pairs.csv", index=False, encoding="utf-8-sig")

print("✅ CSV saved as native_english_pairs.csv")
