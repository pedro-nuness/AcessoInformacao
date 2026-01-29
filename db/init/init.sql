-- Init script for Postgres (runs during container initialization)
-- Creates an example `items` table and inserts a sample row.
-- Init script for Postgres (runs during container initialization)
-- Creates example `items` table (kept for backwards compatibility)
CREATE TABLE IF NOT EXISTS items (
  id SERIAL PRIMARY KEY,
  name TEXT NOT NULL,
  description TEXT,
  price NUMERIC(10,2) NOT NULL,
  tax NUMERIC(10,2)
);

INSERT INTO items (name, description, price, tax)
SELECT 'Sample', 'Initialized row', 9.99, 0.99
WHERE NOT EXISTS (SELECT 1 FROM items WHERE name = 'Sample' AND price = 9.99);

-- Enable gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enums for statuses (safe, idempotent)
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'status_enum') THEN
      CREATE TYPE status_enum AS ENUM ('received','processing','waiting_human_review','ready_to_ship','on_shipment','finished','error');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'register_process_status_enum') THEN
        CREATE TYPE register_process_status_enum AS ENUM ('not_queued','on_queue','processing','completed','error_retry','error_fatal');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'shipment_status_enum') THEN
      CREATE TYPE shipment_status_enum AS ENUM ('not_ready','ready','sent','error_retry','error_fatal');
    END IF;
END$$;

-- processing table (replaces register_process)
CREATE TABLE IF NOT EXISTS processing (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  status register_process_status_enum NOT NULL DEFAULT 'not_queued',
  attempt_count integer NOT NULL DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- shipment table
CREATE TABLE IF NOT EXISTS shipment (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  status shipment_status_enum NOT NULL DEFAULT 'not_ready',
  attempt_count integer NOT NULL DEFAULT 0,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

-- processing_status table linking to shipment and register_process
CREATE TABLE IF NOT EXISTS register_process_event (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  status status_enum NOT NULL DEFAULT 'received',
  shipment_id uuid REFERENCES shipment(id) ON DELETE SET NULL,
  register_process_id uuid REFERENCES processing(id) ON DELETE SET NULL,
  result jsonb,
  external_id TEXT,
  original_text TEXT,
  created_at timestamptz DEFAULT now(),
  updated_at timestamptz DEFAULT now()
);

CREATE INDEX IF NOT EXISTS idx_register_process_event_shipment_id ON register_process_event (shipment_id);
CREATE INDEX IF NOT EXISTS idx_register_process_event_status ON register_process_event (status);
