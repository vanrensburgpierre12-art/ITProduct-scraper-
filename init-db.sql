-- Initialize the electronics database
-- This script runs when the PostgreSQL container starts for the first time

-- Create database if it doesn't exist (already handled by POSTGRES_DB env var)
-- CREATE DATABASE electronics_db;

-- Create extensions
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";

-- Set timezone
SET timezone = 'UTC';

-- Create indexes for better performance (will be created by SQLAlchemy, but good to have)
-- These will be created by the application, but we can add some additional ones here if needed

-- Grant permissions
GRANT ALL PRIVILEGES ON DATABASE electronics_db TO electronics_user;