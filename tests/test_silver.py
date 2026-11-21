
from src.extract.github_api import extract
from src.load.mssql_loader import load_silver
from src.transform.clean_data import transform
# from src.load.load_silver
from collections import Counter


# ED: Extract
result = extract(max_results=250)
repositories = result["repositories"]

# ED: Check duplicate repository IDs
ids = [repo.get("id") for repo in repositories]
id_counts = Counter(ids)

duplicate_ids = {
    repo_id: count
    for repo_id, count in id_counts.items()
    if count > 1
}

# ED: Check duplicate full names
names = [repo.get("full_name") for repo in repositories]
name_counts = Counter(names)

duplicate_names = {
    name: count
    for name, count in name_counts.items()
    if count > 1
}

print("Total extracted:", len(repositories))
print("Unique repository IDs:", len(set(ids)))
print("Duplicate IDs:", len(duplicate_ids))
print("Duplicate ID occurrences:",
      sum(duplicate_ids.values()) - len(duplicate_ids))

print("Duplicate full names:", len(duplicate_names))

# ED: Transform
cleaned = transform(result["repositories"])

# ED: Load into Silver
total = load_silver(cleaned)

print(f"Silver total: {total}")
