-- Initialize qe_data database
-- This script runs automatically when the container starts for the first time

-- Create database if it doesn't exist (this is handled by POSTGRES_DB env var)
-- Additional setup can be added here if needed

-- Set timezone
SET timezone = 'UTC';

-- Create any additional schemas, tables, or initial data here
-- Example:
-- CREATE SCHEMA IF NOT EXISTS app_schema;

-- Log successful initialization
DO $$
BEGIN
    RAISE NOTICE 'Database qe_data initialized successfully';
END $$;