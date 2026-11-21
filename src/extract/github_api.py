
import os
import time
import math
import uuid
import requests


def extract(max_results=1000):
    # ED: GitHub Search API maximum: 1,000 results per query
    if max_results <= 0:
        raise ValueError("max_results must be greater than zero")

    max_results = min(max_results, 1000)
    url = "https://api.github.com/search/repositories"

    per_page = 100
    max_pages = min(10, math.ceil(max_results / per_page))

    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GitHub_Data_Engineering_Project"
    }

    # ED: Optional authentication
    token = os.getenv("GITHUB_TOKEN")
    if token:
        headers["Authorization"] = f"Bearer {token}"

    repositories = []
    raw_pages = []

    page = 1
    batch_id = str(uuid.uuid4())

    with requests.Session() as session:

        while page <= max_pages and len(repositories) < max_results:

            params = {
                'q': 'topic:python',
                'sort': 'stars',
                'order': 'desc',
                'per_page': per_page,
                'page': page
            }

            while True:
                response = session.get(url, headers=headers, params=params, timeout=30)
                # ED: Handle GitHub rate limits
                if response.status_code in (403, 429):
                    remaining = response.headers.get("X-RateLimit-Remaining")

                    is_rate_limited = (
                        response.status_code == 429
                        or remaining == "0"
                        or "rate limit" in response.text.lower()
                    )

                    if not is_rate_limited:
                        response.raise_for_status()

                    retry_after = response.headers.get("Retry-After")
                    reset_time = response.headers.get("X-RateLimit-Reset")

                    if retry_after:
                        wait_seconds = int(retry_after)
                    elif reset_time:
                        wait_seconds = max(
                            1, int(reset_time) - int(time.time()) + 1
                        )
                    else:
                        wait_seconds = 60

                    print(
                        f"Rate limit reached. "
                        f"Waiting {wait_seconds} seconds..."
                    )

                    time.sleep(wait_seconds)
                    continue

                response.raise_for_status()
                break

            data = response.json()
            items = data.get("items") or []
            total_count = data.get("total_count", 0)

            if not items:
                break

            # ED: Preserve the original response for the Bronze layer
            raw_pages.append({
                "batch_id": batch_id,
                "endpoint": response.url,
                "page_number": page,
                "http_status": response.status_code,
                "response_json": data
            })

            repositories.extend(items)

            print(f"Page {page}: fetched {len(items)} total {len(repositories)}")

            if data.get("incomplete_results"):
                print("Warning: GitHub returned incomplete results.")

            # ED: Stop when we have reached the available results
            if page * per_page >= min(total_count, 1000):
                break

            page += 1

            # ED: Search API: approximately 10 requests/minute
            # without authentication, 30/minute with authentication
            time.sleep(2 if token else 6)

    return {
        "batch_id": batch_id,
        "repositories": repositories[:max_results],
        "raw_pages": raw_pages
    }


if __name__ == "__main__":

    result = extract(max_results=250)

    print("\nExtraction completed!")
    print("Batch ID:", result["batch_id"])
    print("Repositories:", len(result["repositories"]))
    print("Raw API pages:", len(result["raw_pages"]))
