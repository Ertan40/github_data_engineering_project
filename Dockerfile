
FROM apache/airflow:3.4.0-python3.12

# Install Microsoft ODBC Driver 18
USER root

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        ca-certificates \
        gnupg \
        unixodbc-dev \
        libgssapi-krb5-2 \
    && curl -sSL \
        https://packages.microsoft.com/config/debian/13/packages-microsoft-prod.deb \
        -o packages-microsoft-prod.deb \
    && dpkg -i packages-microsoft-prod.deb \
    && rm packages-microsoft-prod.deb \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install -y --no-install-recommends msodbcsql18 \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Switch back to the Airflow user
USER airflow

# Install Python dependencies using Airflow constraints
COPY requirements.txt /requirements.txt

RUN pip install --no-cache-dir \
    "apache-airflow==${AIRFLOW_VERSION}" \
    -r /requirements.txt \
    --constraint "https://raw.githubusercontent.com/apache/airflow/constraints-${AIRFLOW_VERSION}/constraints-3.12.txt"

# Copy the ETL application
COPY --chown=airflow:root src/ /opt/airflow/src/

ENV PYTHONPATH="/opt/airflow"
