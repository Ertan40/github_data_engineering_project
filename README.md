# GitHub Repository Intelligence ETL Pipeline

An end-to-end Data Engineering project that extracts repository data from the GitHub REST API, stores raw responses in Microsoft SQL Server, transforms and validates the data, and builds analytical tables for reporting.

The pipeline uses **Python, Microsoft SQL Server, Apache Airflow, Docker, and Power BI** to demonstrate a practical ETL architecture based on the Medallion data model.

## Project Overview

The project collects GitHub repository information, including repository names, descriptions, programming languages, stars, forks, open issues, and timestamps.

The data flows through three layers:

- **Bronze:** Stores raw API responses in JSON format for traceability and future reprocessing.
- **Silver:** Contains cleaned, validated, and structured repository records.
- **Gold:** Stores daily repository snapshots to support historical analysis and reporting.

Apache Airflow orchestrates the ETL workflow, while Docker provides a consistent containerized environment.

## Architecture

```text
             GitHub REST API
                    |
                    v
             Python Extraction
                    |
                    v
          Bronze Layer (MSSQL)
             Raw JSON Data
                    |
                    v
          Python Transformation
          Data Cleaning & Validation
                    |
                    v
          Silver Layer (MSSQL)
          Structured Repository Data
                    |
                    v
             Gold Layer (MSSQL)
          Historical Daily Snapshots
                    |
                    v
              Power BI
          Analytics & Reporting


          Apache Airflow
          Workflow Orchestration
          Scheduling & Monitoring

          Docker
          Containerized Environment
```

## Technologies

| Technology | Purpose |
|---|---|
| Python | API extraction and data transformation |
| Requests | GitHub REST API communication |
| Pandas | Data processing |
| SQLAlchemy | Database connectivity |
| PyODBC | SQL Server connectivity |
| Microsoft SQL Server 2022 | Data storage |
| Apache Airflow 3.4.0 | Workflow orchestration |
| PostgreSQL | Airflow metadata database |
| Docker & Docker Compose | Containerization |
| Power BI Desktop | Data visualization |

## Project Structure

```text
github_data_engineering_project/
│
├── dags/
│   └── github_etl_dag.py
│
├── config/
│
├── logs/
│
├── plugins/
│
├── sql/
│
├── src/
│   ├── common/
│   │   └── logger.py
│   │
│   ├── extract/
│   │   └── github_api.py
│   │
│   ├── transform/
│   │   └── clean_data.py
│   │
│   ├── load/
│   │   └── mssql_loader.py
│   │
│   └── main.py
│
├── tests/
│
├── .env
├── .gitignore
├── Dockerfile
├── docker-compose.yml
└── requirements.txt
```

## ETL Process

### 1. Extraction

The extraction module communicates with the GitHub REST API.

Key features:

- Retrieves repository information using the GitHub Search API.
- Supports pagination to retrieve multiple pages of results.
- Uses `requests.Session()` for API communication.
- Supports GitHub authentication through an environment variable.
- Handles HTTP errors, connection errors, and timeouts.
- Includes rate-limit handling.
- Generates a unique batch ID for each extraction run.
- Captures raw API responses for the Bronze layer.

### 2. Bronze Layer – Raw Data

Raw API responses are stored in SQL Server without applying business transformations.

The Bronze table includes:

- Batch ID
- API endpoint
- Page number
- HTTP status code
- Extraction timestamp
- Raw JSON response

This layer preserves the original source data and provides traceability.

### 3. Transformation

The transformation module prepares repository records for analytical use.

Validation and cleaning include:

- Checking mandatory fields.
- Handling missing and null values.
- Validating numeric fields.
- Rejecting invalid or negative metrics.
- Removing duplicate repository IDs.
- Converting timestamps into appropriate datetime formats.
- Serializing repository topics into JSON.

### 4. Silver Layer – Cleaned Data

Validated repository records are loaded into the Silver layer.

The loading process uses SQL Server staging and `MERGE` operations to insert new repositories and update existing records.

This supports repeatable ETL execution without creating duplicate repository records.

### 5. Gold Layer – Historical Snapshots

The Gold layer stores daily repository snapshots.

It captures metrics such as:

- Stars
- Forks
- Open issues
- Repository size
- Programming language

A composite primary key consisting of `repository_id` and `snapshot_date` prevents duplicate daily snapshots.

This enables historical analysis of repository growth and activity.

## Airflow Orchestration

Apache Airflow 3.4.0 is deployed using Docker Compose with the LocalExecutor.

The DAG `github_repository_etl` orchestrates the Python ETL pipeline through the `execute_etl` task.

Airflow provides:

- Workflow execution and monitoring.
- Manual DAG triggering.
- Task-level execution logs.
- Failure visibility.
- Retry and execution management.

The Airflow metadata database runs separately in PostgreSQL, while the actual ETL data is stored in Microsoft SQL Server.

1. <b>Airflow</b>:
    - <p><img src="images/Github_Airflow.png" alt="Github_Airflow" width="800px"></p>

## Database Architecture

The project uses three SQL Server schemas:

| Schema | Purpose |
|---|---|
| `bronze` | Raw API responses |
| `silver` | Cleaned repository records |
| `gold` | Historical repository snapshots |

The database is named `GitHubAnalyticsDB`.

## Configuration

Sensitive credentials and environment-specific settings are managed through a local `.env` file.

Example configuration (use your own values):

```env
# SQL Server
MSSQL_HOST=your_host
MSSQL_PORT=1433
MSSQL_DATABASE=your_db
MSSQL_USER=your_username
MSSQL_PASSWORD=your_password
MSSQL_DRIVER=ODBC Driver 18 for SQL Server

# Airflow metadata database
AIRFLOW_DB_USER=your_airflow_user
AIRFLOW_DB_PASSWORD=your_airflow_password
AIRFLOW_DB_NAME=airflow

# Airflow security
AIRFLOW_FERNET_KEY=your_fernet_key
AIRFLOW_JWT_SECRET=your_jwt_secret
AIRFLOW_ADMIN_USER=admin
```

**Important:** Never commit your `.env` file, API tokens, passwords, or encryption keys to GitHub.

## Running the Project

### Prerequisites

- Docker Desktop
- Docker Compose
- Microsoft SQL Server 2022 container
- Git
- GitHub account (optional API token for authenticated requests)

### 1. Clone the repository

```bash
git clone https://github.com/ertan40/github_data_engineering_project.git

cd github_data_engineering_project
```

### 2. Configure environment variables

Create your local `.env` file and configure the required database and Airflow settings.

### 3. Start the Airflow environment

```bash
docker compose up -d --build
```

### 4. Access Airflow

Open:

```text
http://localhost:8080
```

Locate the `github_repository_etl` DAG and trigger a manual run.

### 5. Monitor execution

Monitor the `execute_etl` task through the Airflow UI and inspect task logs to verify the pipeline execution.

### 6. Verify SQL Server data

Connect to SQL Server using SQL Server Management Studio or another SQL client.

Check the Bronze, Silver, and Gold tables to verify the loaded data.

## Logging and Error Handling

The project implements centralized Python logging to track ETL execution.

Logging covers:

- Pipeline execution stages.
- Extraction progress.
- Data validation results.
- Database loading operations.
- Exceptions and failures.

Database operations use SQLAlchemy transactions to help maintain data consistency. Exceptions are logged and re-raised so Airflow can detect task failures.

## Future Improvements

Potential extensions include:

- Implementing automated incremental extraction using GitHub repository update timestamps.
- Adding automated data quality tests with pytest.
- Implementing more advanced historical analytics.
- Building Power BI dashboards for repository growth and programming language trends.
- Adding automated monitoring and failure notifications.
- Improving API retry strategies and pipeline observability.

## Author

**Ertan Donmez**

Data Engineering | Python | SQL | ETL | Apache Airflow

GitHub: [ertan40](https://github.com/ertan40)


