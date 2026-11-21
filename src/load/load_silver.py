# import pyodbc
# from sqlalchemy import text
# from src.load.mssql_loader import get_engine
# You CAN DELETE!!!
#
# def load_silver(repositories):
#
#     if not repositories:
#         print("No repositories to load into Silver.")
#         return 0
#
#     engine = get_engine()
#
#     create_staging = text("""
#         CREATE TABLE #repository_staging (
#             repository_id BIGINT NOT NULL,
#             name NVARCHAR(255) NOT NULL,
#             full_name NVARCHAR(500) NOT NULL,
#             description NVARCHAR(2000) NULL,
#             html_url NVARCHAR(1000) NULL,
#             language NVARCHAR(100) NULL,
#             stargazers_count INT NOT NULL,
#             forks_count INT NOT NULL,
#             open_issues_count INT NOT NULL,
#             size_kb INT NOT NULL,
#             created_at DATETIMEOFFSET NULL,
#             updated_at DATETIMEOFFSET NULL,
#             pushed_at DATETIMEOFFSET NULL,
#             default_branch NVARCHAR(255) NULL,
#             is_fork BIT NOT NULL,
#             is_archived BIT NOT NULL,
#             topics_json NVARCHAR(MAX) NULL
#         );
#     """)
#
#     insert_staging = text("""
#         INSERT INTO #repository_staging (
#             repository_id, name, full_name, description,
#             html_url, language, stargazers_count, forks_count,
#             open_issues_count, size_kb, created_at, updated_at,
#             pushed_at, default_branch, is_fork, is_archived,
#             topics_json
#         )
#         VALUES (
#             :repository_id, :name, :full_name, :description,
#             :html_url, :language, :stargazers_count, :forks_count,
#             :open_issues_count, :size_kb, :created_at, :updated_at,
#             :pushed_at, :default_branch, :is_fork, :is_archived,
#             :topics_json
#         );
#     """)
#
#     merge_query = text("""
#         MERGE silver.repositories AS target
#         USING #repository_staging AS source
#             ON target.repository_id = source.repository_id
#
#         WHEN MATCHED THEN
#             UPDATE SET
#                 target.name = source.name,
#                 target.full_name = source.full_name,
#                 target.description = source.description,
#                 target.html_url = source.html_url,
#                 target.language = source.language,
#                 target.stargazers_count = source.stargazers_count,
#                 target.forks_count = source.forks_count,
#                 target.open_issues_count = source.open_issues_count,
#                 target.size_kb = source.size_kb,
#                 target.created_at = source.created_at,
#                 target.updated_at = source.updated_at,
#                 target.pushed_at = source.pushed_at,
#                 target.default_branch = source.default_branch,
#                 target.is_fork = source.is_fork,
#                 target.is_archived = source.is_archived,
#                 target.topics_json = source.topics_json,
#                 target.last_synced_at = SYSUTCDATETIME()
#
#         WHEN NOT MATCHED BY TARGET THEN
#             INSERT (
#                 repository_id, name, full_name, description,
#                 html_url, language, stargazers_count, forks_count,
#                 open_issues_count, size_kb, created_at, updated_at,
#                 pushed_at, default_branch, is_fork, is_archived,
#                 topics_json
#             )
#             VALUES (
#                 source.repository_id, source.name, source.full_name,
#                 source.description, source.html_url, source.language,
#                 source.stargazers_count, source.forks_count,
#                 source.open_issues_count, source.size_kb,
#                 source.created_at, source.updated_at,
#                 source.pushed_at, source.default_branch,
#                 source.is_fork, source.is_archived,
#                 source.topics_json
#             );
#     """)
#
#     try:
#
#         with engine.begin() as conn:
#             conn.execute(create_staging)
#             # ED: Insert all transformed records into staging
#             conn.execute(insert_staging, repositories)
#
#             # ED: Merge staging records into Silver
#             conn.execute(merge_query)
#
#             # ED: Count records in Silver
#             total = conn.execute(
#                 text("SELECT COUNT(*) FROM silver.repositories")
#             ).scalar_one()
#
#         print(
#             f"Silver loading completed. "
#             f"Total repositories in Silver: {total}"
#         )
#
#         return total
#
#     finally:
#         engine.dispose()
