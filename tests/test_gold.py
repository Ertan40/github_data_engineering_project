
from src.load.mssql_loader import load_gold_snapshot

total = load_gold_snapshot()

print(f"Gold snapshot total: {total}")
