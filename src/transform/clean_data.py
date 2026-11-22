import json
from datetime import datetime
from src.main import logger


def parse_datetime(value):
    """ED: Convert GitHub ISO timestamps to Python datetime."""

    if not value:
        return None
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def transform(repositories):

    cleaned_repositories = []
    seen_ids = set()
    rejected = 0
    duplicates = 0

    for repo in repositories:
        # ED: Validate required fields
        repo_id = repo.get("id")
        name = repo.get("name")
        full_name = repo.get("full_name")

        if not repo_id or not name or not full_name:
            rejected += 1
            continue

        # ED: Remove duplicates
        if repo_id in seen_ids:
            duplicates += 1
            continue

        seen_ids.add(repo_id)

        # ED: Validate numeric fields
        numeric_fields = [
            "stargazers_count",
            "forks_count",
            "open_issues_count",
            "size"
        ]

        values = {}
        invalid = False

        for field in numeric_fields:
            value = repo.get(field)
            if value is None:
                value = 0

            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                invalid = True
                break
            values[field] = value

        if invalid:
            rejected += 1
            continue

        # ED: Prepare cleaned record
        cleaned = {
            "repository_id": repo_id,
            "name": name.strip(),
            "full_name": full_name.strip(),
            "description": repo.get("description"),
            "html_url": repo.get("html_url"),
            "language": repo.get("language"),
            "stargazers_count": values["stargazers_count"],
            "forks_count": values["forks_count"],
            "open_issues_count": values["open_issues_count"],
            "size_kb": values["size"],
            "created_at": parse_datetime(repo.get("created_at")),
            "updated_at": parse_datetime(repo.get("updated_at")),
            "pushed_at": parse_datetime(repo.get("pushed_at")),
            "default_branch": repo.get("default_branch"),
            "is_fork": bool(repo.get("fork", False)),
            "is_archived": bool(repo.get("archived", False)),
            "topics_json": json.dumps(repo.get("topics") or [])
        }

        cleaned_repositories.append(cleaned)

    logger.info("Input repositories: %s", len(repositories))
    logger.info("Cleaned repositories: %s", len(cleaned_repositories))

    if rejected > 0:
        logger.warning("Rejected repositories: %s", rejected)

    if duplicates > 0:
        logger.warning("Duplicate repositories: %s", duplicates)

    return cleaned_repositories
