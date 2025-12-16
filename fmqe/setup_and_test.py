"""
FMQE Setup and Test Script
==========================
Run this script to verify PostgreSQL connection and set up the database schema.
"""

import os
import sys

try:
    from sqlalchemy import create_engine, text
    print("[OK] sqlalchemy installed")
except ImportError:
    print("[ERROR] sqlalchemy not installed. Run: pip install sqlalchemy")
    sys.exit(1)

try:
    import psycopg2
    print("[OK] psycopg2 installed")
except ImportError:
    print("[ERROR] psycopg2 not installed. Run: pip install psycopg2-binary")
    sys.exit(1)

try:
    import pandas as pd
    print("[OK] pandas installed")
except ImportError:
    print("[ERROR] pandas not installed. Run: pip install pandas")
    sys.exit(1)

try:
    import jaydebeapi
    print("[OK] jaydebeapi installed")
except ImportError:
    print("[WARN] jaydebeapi not installed. Run: pip install jaydebeapi")
    print("       jaydebeapi is required for FileMaker connection")

# PostgreSQL Configuration
PG_CONFIG = {
    "server": "127.0.0.1",
    "username": "postgres",
    "password": "postgres",
    "port": "5432",
    "database": "qe_data"
}

STAGING_SCHEMA = "fm_staging"
PRODUCTION_SCHEMA = "fm_data"


def test_postgresql_connection():
    """Test connection to PostgreSQL."""
    print("\n" + "=" * 60)
    print("Testing PostgreSQL Connection")
    print("=" * 60)

    # First connect to default database
    default_url = f"postgresql://{PG_CONFIG['username']}:{PG_CONFIG['password']}@{PG_CONFIG['server']}:{PG_CONFIG['port']}/postgres"

    try:
        default_engine = create_engine(default_url, isolation_level='AUTOCOMMIT')
        with default_engine.connect() as conn:
            result = conn.execute(text("SELECT version()")).fetchone()
            print(f"[OK] Connected to PostgreSQL")
            print(f"     Version: {result[0][:60]}...")
        default_engine.dispose()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to connect to PostgreSQL: {e}")
        print("\nPlease ensure:")
        print("  1. PostgreSQL is installed and running")
        print("  2. User 'postgres' exists with password 'postgres'")
        print("  3. PostgreSQL is listening on port 5432")
        return False


def create_database():
    """Create qe_data database if it doesn't exist."""
    print("\n" + "=" * 60)
    print("Creating Database")
    print("=" * 60)

    default_url = f"postgresql://{PG_CONFIG['username']}:{PG_CONFIG['password']}@{PG_CONFIG['server']}:{PG_CONFIG['port']}/postgres"
    default_engine = create_engine(default_url, isolation_level='AUTOCOMMIT')

    try:
        with default_engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{PG_CONFIG['database']}'")).fetchone()
            if not result:
                conn.execute(text(f"CREATE DATABASE {PG_CONFIG['database']}"))
                print(f"[OK] Database '{PG_CONFIG['database']}' created")
            else:
                print(f"[OK] Database '{PG_CONFIG['database']}' already exists")
        default_engine.dispose()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create database: {e}")
        return False


def create_schemas():
    """Create schemas in qe_data database."""
    print("\n" + "=" * 60)
    print("Creating Schemas")
    print("=" * 60)

    connection_url = f"postgresql://{PG_CONFIG['username']}:{PG_CONFIG['password']}@{PG_CONFIG['server']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}"
    engine = create_engine(connection_url)

    try:
        with engine.connect() as conn:
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {STAGING_SCHEMA}"))
            conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {PRODUCTION_SCHEMA}"))
            conn.commit()
            print(f"[OK] Schema '{STAGING_SCHEMA}' created/verified")
            print(f"[OK] Schema '{PRODUCTION_SCHEMA}' created/verified")
        engine.dispose()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create schemas: {e}")
        return False


def create_import_tracking_table():
    """Create import history tracking table."""
    print("\n" + "=" * 60)
    print("Creating Import Tracking Table")
    print("=" * 60)

    connection_url = f"postgresql://{PG_CONFIG['username']}:{PG_CONFIG['password']}@{PG_CONFIG['server']}:{PG_CONFIG['port']}/{PG_CONFIG['database']}"
    engine = create_engine(connection_url)

    create_table_sql = f"""
    CREATE TABLE IF NOT EXISTS {STAGING_SCHEMA}.import_history (
        id SERIAL PRIMARY KEY,
        table_name VARCHAR(255) NOT NULL,
        import_type VARCHAR(50) NOT NULL,
        records_imported INTEGER NOT NULL,
        last_modification_timestamp TIMESTAMP,
        import_started_at TIMESTAMP NOT NULL,
        import_completed_at TIMESTAMP,
        status VARCHAR(50) DEFAULT 'running',
        error_message TEXT
    )
    """

    try:
        with engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            print(f"[OK] Import tracking table created/verified")
        engine.dispose()
        return True
    except Exception as e:
        print(f"[ERROR] Failed to create tracking table: {e}")
        return False


def check_jdbc_driver():
    """Check if FileMaker JDBC driver is available."""
    print("\n" + "=" * 60)
    print("Checking FileMaker JDBC Driver")
    print("=" * 60)

    driver_locations = [
        "fmjdbc.jar",
        os.path.join(os.path.dirname(__file__), "fmjdbc.jar"),
        os.path.join(os.path.dirname(__file__), "drivers", "fmjdbc.jar"),
    ]

    for loc in driver_locations:
        if os.path.exists(loc):
            print(f"[OK] FileMaker JDBC driver found: {loc}")
            return True

    print("[WARN] FileMaker JDBC driver (fmjdbc.jar) not found")
    print("\nTo get the JDBC driver:")
    print("  1. Download from FileMaker Server installation")
    print("  2. Or copy from an existing installation")
    print("  3. Place fmjdbc.jar in the fmqe folder")
    return False


def main():
    """Run all setup and tests."""
    print("=" * 60)
    print("FMQE Setup and Test")
    print("=" * 60)
    print(f"Working Directory: {os.getcwd()}")
    print()

    # Test PostgreSQL
    if not test_postgresql_connection():
        print("\n[FAIL] PostgreSQL connection failed. Please fix and retry.")
        return False

    # Create database
    if not create_database():
        print("\n[FAIL] Database creation failed.")
        return False

    # Create schemas
    if not create_schemas():
        print("\n[FAIL] Schema creation failed.")
        return False

    # Create tracking table
    if not create_import_tracking_table():
        print("\n[FAIL] Tracking table creation failed.")
        return False

    # Check JDBC driver
    check_jdbc_driver()

    print("\n" + "=" * 60)
    print("Setup Complete!")
    print("=" * 60)
    print("\nNext steps:")
    print("  1. Ensure fmjdbc.jar is in the fmqe folder")
    print("  2. Start FileMaker Server with the database file")
    print("  3. Open fmqe_import.ipynb in Jupyter")
    print("  4. Run the cells to import data")

    return True


if __name__ == "__main__":
    main()
