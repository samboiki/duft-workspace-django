"""
FileMaker to PostgreSQL Incremental Import Solution
====================================================
This module provides incremental data import from FileMaker databases to PostgreSQL.
First import brings all data elements including auditing attributes.
Subsequent imports use auditing attributes to only import changed data.
"""

import json
import logging
import os
from datetime import datetime
from typing import Optional, Dict, List, Any

import jaydebeapi
import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class FMQEImporter:
    """FileMaker to PostgreSQL Incremental Importer"""

    def __init__(self, config_path: str = None):
        """Initialize the importer with configuration."""
        if config_path is None:
            config_path = os.path.join(os.path.dirname(__file__), 'config.json')

        with open(config_path, 'r') as f:
            self.config = json.load(f)

        self.pg_config = self.config['dataConnectionParameters']['PostgreSQL']
        self.fm_config = self.config['dataConnectionParameters']['FileMaker']
        self.schemas = self.config['schemas']
        self.tables = self.config['tables']

        self.pg_engine: Optional[Engine] = None
        self.fm_connection = None

    def connect_postgresql(self) -> Engine:
        """Create PostgreSQL connection and ensure database exists."""
        # First connect to default postgres database to create our database if needed
        default_url = f"postgresql://{self.pg_config['username']}:{self.pg_config['password']}@{self.pg_config['server']}:{self.pg_config['port']}/postgres"
        default_engine = create_engine(default_url, isolation_level='AUTOCOMMIT')

        database = self.pg_config['database']

        with default_engine.connect() as conn:
            result = conn.execute(text(f"SELECT 1 FROM pg_database WHERE datname = '{database}'")).fetchone()
            if not result:
                conn.execute(text(f"CREATE DATABASE {database}"))
                logger.info(f"Database '{database}' created successfully")

        default_engine.dispose()

        # Now connect to our actual database
        connection_url = f"postgresql://{self.pg_config['username']}:{self.pg_config['password']}@{self.pg_config['server']}:{self.pg_config['port']}/{database}"
        self.pg_engine = create_engine(connection_url)
        logger.info(f"Connected to PostgreSQL database: {database}")

        return self.pg_engine

    def connect_filemaker(self):
        """Create FileMaker JDBC connection."""
        driver_jar = self.fm_config.get('driver_jar', 'fmjdbc.jar')
        driver_class = self.fm_config.get('driver_class', 'com.filemaker.jdbc.Driver')
        server = self.fm_config['server']
        username = self.fm_config['username']
        password = self.fm_config['password']

        # Look for driver jar in multiple locations
        jar_locations = [
            driver_jar,
            os.path.join(os.path.dirname(__file__), driver_jar),
            os.path.join(os.path.dirname(__file__), 'drivers', driver_jar),
        ]

        jar_path = None
        for loc in jar_locations:
            if os.path.exists(loc):
                jar_path = loc
                break

        if jar_path is None:
            raise FileNotFoundError(f"FileMaker JDBC driver not found. Please place {driver_jar} in the fmqe folder or fmqe/drivers folder.")

        self.fm_connection = jaydebeapi.connect(
            driver_class,
            server,
            [username, password],
            jar_path
        )
        logger.info(f"Connected to FileMaker: {server}")
        return self.fm_connection

    def close_connections(self):
        """Close all database connections."""
        if self.fm_connection:
            self.fm_connection.close()
            logger.info("FileMaker connection closed")
        if self.pg_engine:
            self.pg_engine.dispose()
            logger.info("PostgreSQL connection closed")

    def setup_schemas(self):
        """Create necessary schemas in PostgreSQL."""
        with self.pg_engine.connect() as conn:
            for schema_name in self.schemas.values():
                conn.execute(text(f"CREATE SCHEMA IF NOT EXISTS {schema_name}"))
                conn.commit()
                logger.info(f"Schema '{schema_name}' ensured")

    def setup_import_tracking_table(self):
        """Create table to track import history for incremental imports."""
        schema = self.schemas['staging']

        create_table_sql = f"""
        CREATE TABLE IF NOT EXISTS {schema}.import_history (
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

        with self.pg_engine.connect() as conn:
            conn.execute(text(create_table_sql))
            conn.commit()
            logger.info("Import tracking table created/verified")

    def get_last_import_timestamp(self, table_name: str) -> Optional[datetime]:
        """Get the last successful import timestamp for a table."""
        schema = self.schemas['staging']

        query = f"""
        SELECT last_modification_timestamp
        FROM {schema}.import_history
        WHERE table_name = :table_name
          AND status = 'completed'
        ORDER BY import_completed_at DESC
        LIMIT 1
        """

        with self.pg_engine.connect() as conn:
            result = conn.execute(text(query), {'table_name': table_name}).fetchone()

        if result and result[0]:
            return result[0]
        return None

    def record_import_start(self, table_name: str, import_type: str) -> int:
        """Record the start of an import operation."""
        schema = self.schemas['staging']

        insert_sql = f"""
        INSERT INTO {schema}.import_history (table_name, import_type, records_imported, import_started_at, status)
        VALUES (:table_name, :import_type, 0, :started_at, 'running')
        RETURNING id
        """

        with self.pg_engine.connect() as conn:
            result = conn.execute(text(insert_sql), {
                'table_name': table_name,
                'import_type': import_type,
                'started_at': datetime.now()
            })
            import_id = result.fetchone()[0]
            conn.commit()

        return import_id

    def record_import_complete(self, import_id: int, records_imported: int,
                               last_timestamp: Optional[datetime], error_message: str = None):
        """Record the completion of an import operation."""
        schema = self.schemas['staging']

        status = 'completed' if error_message is None else 'failed'

        update_sql = f"""
        UPDATE {schema}.import_history
        SET records_imported = :records,
            last_modification_timestamp = :last_ts,
            import_completed_at = :completed_at,
            status = :status,
            error_message = :error
        WHERE id = :import_id
        """

        with self.pg_engine.connect() as conn:
            conn.execute(text(update_sql), {
                'records': records_imported,
                'last_ts': last_timestamp,
                'completed_at': datetime.now(),
                'status': status,
                'error': error_message,
                'import_id': import_id
            })
            conn.commit()

    def fetch_filemaker_data(self, query: str, params: Dict = None) -> pd.DataFrame:
        """Execute a query against FileMaker and return results as DataFrame."""
        cursor = self.fm_connection.cursor()
        try:
            cursor.execute(query)
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            df = pd.DataFrame(data, columns=columns)
            logger.info(f"Fetched {len(df)} rows from FileMaker")
            return df
        finally:
            cursor.close()

    def import_table(self, table_config: Dict, force_full: bool = False) -> Dict[str, Any]:
        """
        Import a single table from FileMaker to PostgreSQL.
        Uses incremental import if previous import exists, otherwise full import.
        """
        table_name = table_config['name']
        base_query = table_config['query']
        audit_columns = table_config.get('audit_columns', ['devModificationTimestamp'])
        primary_audit_col = audit_columns[-1] if audit_columns else None  # Use modification timestamp

        # Determine import type
        last_timestamp = None if force_full else self.get_last_import_timestamp(table_name)
        import_type = 'full' if last_timestamp is None else 'incremental'

        logger.info(f"Starting {import_type} import for table: {table_name}")

        # Record import start
        import_id = self.record_import_start(table_name, import_type)

        try:
            # Build query with incremental filter if applicable
            if import_type == 'incremental' and primary_audit_col:
                # Format timestamp for FileMaker
                ts_str = last_timestamp.strftime('%m/%d/%Y %H:%M:%S')
                query = f"{base_query} WHERE {primary_audit_col} > '{ts_str}'"
            else:
                query = base_query

            # Fetch data from FileMaker
            df = self.fetch_filemaker_data(query)

            if df.empty:
                logger.info(f"No new records to import for table: {table_name}")
                self.record_import_complete(import_id, 0, last_timestamp)
                return {
                    'table': table_name,
                    'import_type': import_type,
                    'records': 0,
                    'status': 'completed'
                }

            # Get the max modification timestamp from the imported data
            new_last_timestamp = None
            if primary_audit_col and primary_audit_col in df.columns:
                max_ts = df[primary_audit_col].max()
                if pd.notna(max_ts):
                    if isinstance(max_ts, str):
                        new_last_timestamp = pd.to_datetime(max_ts)
                    else:
                        new_last_timestamp = max_ts

            # Write to PostgreSQL
            staging_schema = self.schemas['staging']
            staging_table = f"{staging_schema}.{table_name}"

            if import_type == 'full':
                # Full import: replace entire table
                df.to_sql(
                    table_name,
                    self.pg_engine,
                    schema=staging_schema,
                    if_exists='replace',
                    index=False
                )
            else:
                # Incremental import: append or upsert
                primary_key = table_config.get('primary_key')

                if primary_key and primary_key in df.columns:
                    # Upsert logic: delete existing records and insert new ones
                    with self.pg_engine.connect() as conn:
                        pk_values = df[primary_key].tolist()
                        # Delete existing records with matching primary keys
                        if pk_values:
                            placeholders = ', '.join([f"'{v}'" if isinstance(v, str) else str(v) for v in pk_values])
                            delete_sql = f"DELETE FROM {staging_table} WHERE {primary_key} IN ({placeholders})"
                            conn.execute(text(delete_sql))
                            conn.commit()

                    # Insert new/updated records
                    df.to_sql(
                        table_name,
                        self.pg_engine,
                        schema=staging_schema,
                        if_exists='append',
                        index=False
                    )
                else:
                    # No primary key: append all records
                    df.to_sql(
                        table_name,
                        self.pg_engine,
                        schema=staging_schema,
                        if_exists='append',
                        index=False
                    )

            records_imported = len(df)
            logger.info(f"Successfully imported {records_imported} records to {staging_table}")

            self.record_import_complete(import_id, records_imported, new_last_timestamp)

            return {
                'table': table_name,
                'import_type': import_type,
                'records': records_imported,
                'status': 'completed',
                'last_timestamp': str(new_last_timestamp) if new_last_timestamp else None
            }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"Error importing table {table_name}: {error_msg}")
            self.record_import_complete(import_id, 0, last_timestamp, error_msg)
            return {
                'table': table_name,
                'import_type': import_type,
                'records': 0,
                'status': 'failed',
                'error': error_msg
            }

    def run_full_import(self, tables: List[str] = None):
        """
        Run a full import for all configured tables or specified tables.
        This brings in all data elements including auditing attributes.
        """
        logger.info("=" * 60)
        logger.info("Starting FULL IMPORT")
        logger.info("=" * 60)

        results = []
        tables_to_import = self.tables

        if tables:
            tables_to_import = [t for t in self.tables if t['name'] in tables]

        for table_config in tables_to_import:
            result = self.import_table(table_config, force_full=True)
            results.append(result)

        return results

    def run_incremental_import(self, tables: List[str] = None):
        """
        Run an incremental import for all configured tables or specified tables.
        Uses auditing attributes to only import changed data.
        """
        logger.info("=" * 60)
        logger.info("Starting INCREMENTAL IMPORT")
        logger.info("=" * 60)

        results = []
        tables_to_import = self.tables

        if tables:
            tables_to_import = [t for t in self.tables if t['name'] in tables]

        for table_config in tables_to_import:
            result = self.import_table(table_config, force_full=False)
            results.append(result)

        return results

    def get_import_history(self, table_name: str = None, limit: int = 10) -> pd.DataFrame:
        """Get import history for reporting."""
        schema = self.schemas['staging']

        query = f"""
        SELECT table_name, import_type, records_imported,
               last_modification_timestamp, import_started_at,
               import_completed_at, status, error_message
        FROM {schema}.import_history
        """

        if table_name:
            query += f" WHERE table_name = '{table_name}'"

        query += f" ORDER BY import_started_at DESC LIMIT {limit}"

        return pd.read_sql(query, self.pg_engine)


def main():
    """Main entry point for running imports."""
    import argparse

    parser = argparse.ArgumentParser(description='FileMaker to PostgreSQL Incremental Import')
    parser.add_argument('--mode', choices=['full', 'incremental', 'auto'], default='auto',
                        help='Import mode: full, incremental, or auto (default: auto)')
    parser.add_argument('--tables', nargs='+', help='Specific tables to import')
    parser.add_argument('--config', help='Path to config file')

    args = parser.parse_args()

    importer = FMQEImporter(config_path=args.config)

    try:
        # Connect to databases
        importer.connect_postgresql()
        importer.connect_filemaker()

        # Setup schemas and tracking
        importer.setup_schemas()
        importer.setup_import_tracking_table()

        # Run import based on mode
        if args.mode == 'full':
            results = importer.run_full_import(args.tables)
        elif args.mode == 'incremental':
            results = importer.run_incremental_import(args.tables)
        else:  # auto mode
            results = importer.run_incremental_import(args.tables)

        # Print summary
        print("\n" + "=" * 60)
        print("IMPORT SUMMARY")
        print("=" * 60)
        for r in results:
            status_emoji = "✓" if r['status'] == 'completed' else "✗"
            print(f"{status_emoji} {r['table']}: {r['records']} records ({r['import_type']})")

    finally:
        importer.close_connections()


if __name__ == '__main__':
    main()
