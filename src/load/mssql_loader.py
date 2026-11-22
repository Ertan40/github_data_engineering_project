
import os
import json
import pyodbc
from sqlalchemy import URL, create_engine, text
from src.main import logger


def get_engine():
    # ED This is production ready:
    db_url = URL.create(
        drivername="mssql+pyodbc",
        username=os.getenv("MSSQL_USER"),
        password=os.getenv("MSSQL_PASSWORD"),
        host="localhost",
        port=1433,
        database="GitHubAnalyticsDB",
        query={
            "driver": os.getenv(
                "MSSQL_DRIVER",
                "ODBC Driver 18 for SQL Server"
            ),
            "TrustServerCertificate": "yes"
        }
    )
    engine = create_engine(db_url)
    return engine


def load_bronze(raw_pages):

    if not raw_pages:
        logger.info("No raw API responses to load.")
        return 0

    insert_query = text("""
        INSERT INTO bronze.api_responses (
            batch_id,
            endpoint,
            page_number,
            http_status,
            response_json
        )
        VALUES (
            :batch_id,
            :endpoint,
            :page_number,
            :http_status,
            :response_json
        )
    """)

    engine = get_engine()

    try:
        records = []

        for page in raw_pages:

            records.append({
                "batch_id": page["batch_id"],
                "endpoint": page["endpoint"],
                "page_number": page["page_number"],
                "http_status": page["http_status"],
                "response_json": json.dumps(
                    page["response_json"]
                )
            })

        # ED: One transaction for the complete batch
        with engine.begin() as conn:
            conn.execute(insert_query, records)

        logger.info("Bronze loading completed. API responses loaded: %s", len(records))
        return len(records)

    finally:
        engine.dispose()


def load_silver(repositories):

    if not repositories:
        logger.info("No repositories to load into Silver.")
        return 0

    engine = get_engine()

    create_staging = text("""
        CREATE TABLE #repository_staging (
            repository_id BIGINT NOT NULL,
            name NVARCHAR(255) NOT NULL,
            full_name NVARCHAR(500) NOT NULL,
            description NVARCHAR(2000) NULL,
            html_url NVARCHAR(1000) NULL,
            language NVARCHAR(100) NULL,
            stargazers_count INT NOT NULL,
            forks_count INT NOT NULL,
            open_issues_count INT NOT NULL,
            size_kb INT NOT NULL,
            created_at DATETIMEOFFSET NULL,
            updated_at DATETIMEOFFSET NULL,
            pushed_at DATETIMEOFFSET NULL,
            default_branch NVARCHAR(255) NULL,
            is_fork BIT NOT NULL,
            is_archived BIT NOT NULL,
            topics_json NVARCHAR(MAX) NULL
        );
    """)

    insert_staging = text("""
        INSERT INTO #repository_staging (
            repository_id, name, full_name, description,
            html_url, language, stargazers_count, forks_count,
            open_issues_count, size_kb, created_at, updated_at,
            pushed_at, default_branch, is_fork, is_archived,
            topics_json
        )
        VALUES (
            :repository_id, :name, :full_name, :description,
            :html_url, :language, :stargazers_count, :forks_count,
            :open_issues_count, :size_kb, :created_at, :updated_at,
            :pushed_at, :default_branch, :is_fork, :is_archived,
            :topics_json
        );
    """)

    merge_query = text("""
        MERGE silver.repositories AS target
        USING #repository_staging AS source
            ON target.repository_id = source.repository_id

        WHEN MATCHED THEN
            UPDATE SET
                target.name = source.name,
                target.full_name = source.full_name,
                target.description = source.description,
                target.html_url = source.html_url,
                target.language = source.language,
                target.stargazers_count = source.stargazers_count,
                target.forks_count = source.forks_count,
                target.open_issues_count = source.open_issues_count,
                target.size_kb = source.size_kb,
                target.created_at = source.created_at,
                target.updated_at = source.updated_at,
                target.pushed_at = source.pushed_at,
                target.default_branch = source.default_branch,
                target.is_fork = source.is_fork,
                target.is_archived = source.is_archived,
                target.topics_json = source.topics_json,
                target.last_synced_at = SYSUTCDATETIME()

        WHEN NOT MATCHED BY TARGET THEN
            INSERT (
                repository_id, name, full_name, description,
                html_url, language, stargazers_count, forks_count,
                open_issues_count, size_kb, created_at, updated_at,
                pushed_at, default_branch, is_fork, is_archived,
                topics_json
            )
            VALUES (
                source.repository_id, source.name, source.full_name,
                source.description, source.html_url, source.language,
                source.stargazers_count, source.forks_count,
                source.open_issues_count, source.size_kb,
                source.created_at, source.updated_at,
                source.pushed_at, source.default_branch,
                source.is_fork, source.is_archived,
                source.topics_json
            );
    """)

    try:

        with engine.begin() as conn:
            conn.execute(create_staging)
            # ED: Insert all transformed records into staging
            conn.execute(insert_staging, repositories)

            # ED: Merge staging records into Silver
            conn.execute(merge_query)

            # ED: Count records in Silver
            total = conn.execute(
                text("SELECT COUNT(*) FROM silver.repositories")
            ).scalar_one()

        logger.info("Silver loading completed. Total repositories in Silver: %s", total)

        return total

    finally:
        engine.dispose()


def load_gold_snapshot():
    merge_query = text("""
        SET NOCOUNT ON;
        DECLARE @snapshot_date DATE = CONVERT(DATE, SYSUTCDATETIME());

        MERGE gold.repository_snapshots AS target
        USING (
            SELECT
                repository_id,
                @snapshot_date AS snapshot_date,
                stargazers_count,
                forks_count,
                open_issues_count,
                size_kb,
                language
            FROM silver.repositories
        ) AS source
        ON target.repository_id = source.repository_id
           AND target.snapshot_date = source.snapshot_date

        WHEN MATCHED THEN
            UPDATE SET
                stargazers_count = source.stargazers_count,
                forks_count = source.forks_count,
                open_issues_count = source.open_issues_count,
                size_kb = source.size_kb,
                language = source.language,
                snapshot_at = SYSUTCDATETIME()

        WHEN NOT MATCHED BY TARGET THEN
            INSERT (
                repository_id,
                snapshot_date,
                stargazers_count,
                forks_count,
                open_issues_count,
                size_kb,
                language
            )
            VALUES (
                source.repository_id,
                source.snapshot_date,
                source.stargazers_count,
                source.forks_count,
                source.open_issues_count,
                source.size_kb,
                source.language
            );

        SELECT COUNT(*)
        FROM gold.repository_snapshots
        WHERE snapshot_date = @snapshot_date;
    """)

    engine = get_engine()

    try:
        with engine.begin() as conn:
            conn.execute(merge_query)
            total = conn.execute(
                text("""
                    SELECT COUNT(*)
                    FROM gold.repository_snapshots
                    WHERE snapshot_date = CONVERT(DATE, SYSUTCDATETIME())
                """)
            ).scalar_one()

        # print(
        #     f"Gold snapshot completed. "
        #     f"Repositories in today's snapshot: {total}"
        # )
        logger.info("Gold snapshot completed. Repositories in today's snapshot: %s", total)

        return total

    finally:
        engine.dispose()
