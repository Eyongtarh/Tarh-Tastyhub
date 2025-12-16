import json

INPUT_FILE = "data.json"

OUTPUT_FILE = "data_clean.json"

EXCLUDE_MODELS = [
    "contenttypes.contenttype",
    "auth.permission",
    "admin.logentry",
    "sessions.session",
]

with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

cleaned_data = [obj for obj in data if obj["model"] not in EXCLUDE_MODELS]

with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2)

print(f"Cleaned fixture saved to {OUTPUT_FILE}")
print(f"Original objects: {len(data)}, Cleaned objects: {len(cleaned_data)}")
