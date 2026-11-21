from src.extract.github_api import extract
from src.transform.clean_data import transform


result = extract(max_results=250)

cleaned = transform(result["repositories"])

print("\nFirst transformed repository:")
print(cleaned[0])