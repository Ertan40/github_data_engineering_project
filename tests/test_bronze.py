
from src.extract.github_api import extract
from src.load.mssql_loader import load_bronze

result = extract(max_results=250)

loaded = load_bronze(result["raw_pages"])

print(f"Batch ID: {result['batch_id']}")
print(f"Raw pages loaded: {loaded}")
