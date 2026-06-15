-- Run this in PostgreSQL before starting the API (tables match SQLAlchemy models)
CREATE DATABASE shopify_db;

\c shopify_db

CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Tables are created by your SQL script or Alembic migrations.
-- If using raw SQL, run your schema file here.
-- The FastAPI app expects the schema you provided to already exist.
