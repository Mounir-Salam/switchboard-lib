# Switchboard Data Platform Library

Switchboard is a Python data engineering tool designed to isolate pipeline business logic from underlying multi-cloud infrastructure. By enforcing a unified interface contract, Switchboard gives the ability to seamlessly swap storage engines and database destinations using simple environment configurations—transitioning instantly from a local offline Docker development sandbox to live, production-scale cloud infrastructure.

## Core Architecture

1. **Strict Interface Contracts**: Every storage engine implements `StorageProvider` and every database engine implements `DatabaseProvider`. The core application logic never adapts to an SDK; the connectors adapt to the application.

2. **Border Guard Configuration**: Input arguments are heavily scrutinized by Pydantic schemas at initialization, preventing downstream runtime failures due to misconfigured connection strings or typing errors.

3. **Structured System Telemetry**: Standard string logging is banned. Every operation emits JSON-parseable, key-value context tracking (`structlog`) to maintain clear visibility during orchestration.

4. **Resilience & Resource Safety**: Connections leverage context managers (`with` blocks) to guarantee that network transport handles and database session thread pools are cleanly torn down upon execution completion.

## The Switchboard Architecture Matrix
The library is split into two foundational layers: **Blob Storage Providers** and **Relational / Warehouse Database Providers**.

```
                         +------------------------+
                         |    Application Code    |
                         +-----------+------------+
                                     |
                       [ Switchboard Factory Entry ]
                                     |
            +------------------------+------------------------+
            |                                                 |
            v                                                 v
   [ Storage Providers ]                             [ Database Providers ]
   |-- Local File System                             |-- PostgreSQL (Local Mirror)
   |-- Google Cloud Storage (GCS)                    |-- Google BigQuery
   |-- AWS S3 / LocalStack                           |-- AWS Redshift
                                                     |-- ClickHouse
```

## How it works

Your code always calls the same methods — `storage.read()`, `storage.write()`, `db.execute()`, `db.write_table()`, ... — regardless of whether you're reading from a local file, S3, or GCS, or writing to DuckDB, Postgres, or BigQuery.

The `Switchboard` factory reads `STORAGE_TYPE` and `DB_TYPE` from your `.env` file and hands back the right connector. Connections are cached by name, so calling `get_storage()` twice returns the same instance since it will return the default instance. Multiple connection can be created by passing a `name` to `get_storage(name = "my-connection")` or `get_db(name = "my-connection")`.

## Quick start

Copy `.sample.env` to `.env` and leave the defaults — this gives you local file storage and a local DuckDB database, no Docker needed.

```bash
cp .sample.env .env
```

```python
import pandas as pd
import io
from switchboard.factory import Switchboard
from switchboard.utils.logging import configure_logging

configure_logging(production_mode = False)

with Switchboard.get_storage() as storage, Switchboard.get_db() as db:
    # Write a file to storage
    storage.write("raw/samples.csv", "id,name\n1,Alice\n2,Bob")

    # Read it back
    content = storage.read("raw/samples.csv")
    df = pd.read_csv(io.BytesIO(content))

    # Load into a database table
    db.write_table(df, "samples", mode = "replace")

    # Query it
    result = db.get_as_dataframe("SELECT * FROM samples")
    print(result)
```

The `with` block ensures connections are closed cleanly when the block exits.

## Default Configuration

The default configurations are done through environment variables (`.env` file). The two most important ones are:

| Variable | Default | Options |
|---|---|---|
| `STORAGE_TYPE` | `LOCAL` | `LOCAL`, `MINIO`, `GCS`, `S3` |
| `DB_TYPE` | `DUCKDB` | `DUCKDB`, `POSTGRES`, `CLICKHOUSE`, `BIGQUERY`, `REDSHIFT` |

To switch backends, just change these two variables. Your pipeline code stays the same.

### Full `.env` reference

```bash
# --- Active backends ---
STORAGE_TYPE=LOCAL
DB_TYPE=DUCKDB

# --- Local storage ---
LOCAL_STORAGE_PATH=./data/files

# --- DuckDB ---
DUCKDB_PATH=./data/main.db

# --- Postgres ---
POSTGRES_URL=postgresql://postgres:postgres@localhost:5432/postgres

# --- MinIO (S3-compatible, self-hosted) ---
MINIO_ENDPOINT="http://localhost:9000"
MINIO_ACCESS_KEY="admin"
MINIO_SECRET_KEY="password123"
MINIO_BUCKET_NAME="switchboard-bucket"

# --- ClickHouse ---
CLICKHOUSE_HOST="localhost"
CLICKHOUSE_PORT=8123
CLICKHOUSE_USER="default"
CLICKHOUSE_PASSWORD=""

# --- Google Cloud (GCS + BigQuery share the same credentials) ---
GOOGLE_APPLICATION_CREDENTIALS="./secrets/google_service_account.json"
GCS_BUCKET_NAME="your-gcs-bucket-name"
BQ_PROJECT_ID="your-gcp-project-id"
BQ_DATASET_ID="switchboard_dev"

# --- AWS (S3 + Redshift) ---
AWS_ACCESS_KEY_ID="your-key"
AWS_SECRET_ACCESS_KEY="your-secret"
AWS_REGION="us-east-1"
AWS_S3_BUCKET_NAME="your-bucket"
# Uncomment to redirect S3 traffic to LocalStack instead of real AWS:
# AWS_ENDPOINT_URL="http://localhost:4566"

# --- Redshift ---
REDSHIFT_HOST="localhost"
REDSHIFT_PORT=5439
REDSHIFT_DATABASE="dev"
REDSHIFT_USER="awsuser"
REDSHIFT_PASSWORD="password"
```

## Manual Configuration
You can hold multiple connections at once by giving them names and the distinct connectors specific arguments:

The 2 mandatory arguments are:
- `get_storage(name, storage_type, **kwargs)`
- `get_db(name, db_type, **kwargs)`

The `**kwargs` are specific to the storage or database connector. Any required argument left blank will use the default value from the `.env` file.

```python
####### Manual Storge Configurations #######

local_storage = Switchboard.get_storage("local", storage_type = "LOCAL",
    path = "path/to/destination"
)

minio_storage = Switchboard.get_storage("minio", storage_type = "MINIO",
    bucket_name = "switchboard-bucket",
    endpoint = "http://localhost:9000",
    access_key = "admin",
    secret_key = "password123"
)

gcs_storage = Switchboard.get_storage("gcs", storage_type = "GCS",
    bucket_name = "your-gcs-bucket-name",
    credentials_path = "./secrets/google_service_account.json"
)

s3_storage = Switchboard.get_storage("s3", storage_type = "S3",
    bucket_name = "your-bucket",
    region_name = "us-east-1",
    access_key = "your-key",
    secret_key = "your-secret",
    endpoint_url = "http://localhost:4566" # optional for LocalStack
)
```

```python
####### Manual Database Configurations #######

duckdb = Switchboard.get_db("duckdb", db_type = "DUCKDB",
    connection_string = "path/to/duckdb.db"
)

postgres = Switchboard.get_db("postgres", db_type = "POSTGRES",
    connection_string = "postgresql://postgres:postgres@localhost:5432/postgres"
)

clickhouse = Switchboard.get_db("clickhouse", db_type = "CLICKHOUSE",
    host = "localhost",
    port = 8123,
    username = "default",
    password = "clickhouse-password"
)

bigquery = Switchboard.get_db("bigquery", db_type = "BIGQUERY",
    project_id = "your-gcp-project-id",
    dataset_id = "switchboard_dev",
    credentials_path = "./secrets/google_service_account.json"
)

redshift = Switchboard.get_db("redshift", db_type = "REDSHIFT",
    host = "localhost",
    port = 5439,
    database = "dev",
    username = "awsuser",
    password = "password"
)
```

Named instances are cached — calling `get_storage("raw")` again returns the same object.

## Available connectors

### Storage

| Name | `STORAGE_TYPE` | Best for |
|---|---|---|
| Local filesystem | `LOCAL` | Offline dev, unit tests |
| MinIO | `MINIO` | Self-hosted S3-compatible object store |
| Google Cloud Storage | `GCS` | GCP production workloads |
| AWS S3 / LocalStack | `S3` | AWS production or local sandbox via LocalStack |

### Storage Methods

All storage connectors implement the following methods:

```python
storage.write(path: str, data: Any) -> None
storage.read(path: str) -> bytes
storage.close() -> None  # called automatically in a `with` block
```

### Database

| Name | `DB_TYPE` | Best for |
|---|---|---|
| DuckDB | `DUCKDB` | Offline dev, local analytics |
| PostgreSQL | `POSTGRES` | Transactional workloads, local mirror |
| ClickHouse | `CLICKHOUSE` | High-throughput append, real-time analytics |
| Google BigQuery | `BIGQUERY` | GCP data warehouse |
| AWS Redshift | `REDSHIFT` | AWS data warehouse |

### Database Connectors

All database connectors implement the following methods:

```python
db.execute(query: str) -> Any              # run DDL or DML
db.get_as_dataframe(query: str) -> DataFrame  # SELECT → pandas DataFrame
db.write_table(df, table_name, mode = "replace")  # write DataFrame to table
db.close() -> None                         # called automatically in a `with` block
```

`mode` accepts:
- `"replace"` — truncates the table before writing (safe to retry)
- `"append"` — adds rows without truncating (runs exactly once without retries; crashes on failure to prevent duplicates)

## Logging
The tool uses `structlog` to log all operations, And has 2 different modes:
- Dev Mode: Logs are structured into human-readable format with color coding for easy debugging.
- Production Mode: Logs are structured into JSON for easy machine parsing.

```python
from switchboard.utils.logging import configure_logging
configure_logging(production_mode = True)
```