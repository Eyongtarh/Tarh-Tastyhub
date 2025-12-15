import json

# Path to your original fixture
INPUT_FILE = "data.json"
# Path for cleaned fixture
OUTPUT_FILE = "data_clean.json"

# List of Django internal models to remove
EXCLUDE_MODELS = [
    "contenttypes.contenttype",
    "auth.permission",
    "admin.logentry",
    "sessions.session",
]

# Load original fixture
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    data = json.load(f)

# Filter out internal models
cleaned_data = [obj for obj in data if obj["model"] not in EXCLUDE_MODELS]

# Save cleaned fixture
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(cleaned_data, f, indent=2)

print(f"Cleaned fixture saved to {OUTPUT_FILE}")
print(f"Original objects: {len(data)}, Cleaned objects: {len(cleaned_data)}")
