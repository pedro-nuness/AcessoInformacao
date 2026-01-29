-- Migration to initialize processing_status table for RegisterProcessEvent model

CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Enums for statuses
DO $$ BEGIN
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'processing_status_enum') THEN
        CREATE TYPE processing_status_enum AS ENUM ('received','processing','waiting_human_review','ready_to_ship','on_shipment','finished','error');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'register_process_status_enum') THEN
        CREATE TYPE register_process_status_enum AS ENUM ('not_queued','on_queue','processing','completed','error_retry','error_fatal');
    END IF;
    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'shipment_status_enum') THEN
        CREATE TYPE shipment_status_enum AS ENUM ('not_ready','ready','sending','sent','error_retry','error_fatal');
    END IF;
END$$;

-- register_process table
CREATE TABLE IF NOT EXISTS register_process (
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

-- main processing table linking to shipment and register_process
DO $$
BEGIN
  IF NOT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = 'processing_status') THEN
    CREATE TABLE processing_status (
      id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
      status processing_status_enum NOT NULL DEFAULT 'received',
      shipment_id uuid REFERENCES shipment(id) ON DELETE SET NULL,
      register_process_id uuid REFERENCES register_process(id) ON DELETE SET NULL,
      result jsonb,
      external_id TEXT,
      original_text TEXT,
      created_at timestamptz DEFAULT now(),
      updated_at timestamptz DEFAULT now()
    );
  ELSE
    -- If table exists, ensure new columns exist
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='shipment_id') THEN
      ALTER TABLE processing_status ADD COLUMN shipment_id uuid;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='register_process_id') THEN
      ALTER TABLE processing_status ADD COLUMN register_process_id uuid;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='result') THEN
      ALTER TABLE processing_status ADD COLUMN result jsonb;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='external_id') THEN
      ALTER TABLE processing_status ADD COLUMN external_id text;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='original_text') THEN
      ALTER TABLE processing_status ADD COLUMN original_text text;
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='created_at') THEN
      ALTER TABLE processing_status ADD COLUMN created_at timestamptz DEFAULT now();
    END IF;
    IF NOT EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='updated_at') THEN
      ALTER TABLE processing_status ADD COLUMN updated_at timestamptz DEFAULT now();
    END IF;

    -- Migrate data from old jsonb columns if present
    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='shipment') THEN
      -- move shipment jsonb -> shipment table
      WITH moved AS (
        SELECT id as proc_id,
               gen_random_uuid() as new_shipment_id,
               (shipment->>'status') as s_status,
               COALESCE((shipment->>'attemptCount')::int, 0) as s_attempt
        FROM processing_status
        WHERE shipment IS NOT NULL
      )
      INSERT INTO shipment(id, status, attempt_count, created_at, updated_at)
      SELECT new_shipment_id, COALESCE(s_status,'not_ready')::shipment_status_enum, s_attempt, now(), now() from moved;

      -- link back
      UPDATE processing_status p
      SET shipment_id = m.new_shipment_id
      FROM moved m
      WHERE p.id = m.proc_id;

      -- drop old column
      ALTER TABLE processing_status DROP COLUMN IF EXISTS shipment;
    END IF;

    IF EXISTS (SELECT 1 FROM information_schema.columns WHERE table_name='processing_status' AND column_name='register_process') THEN
      WITH moved AS (
        SELECT id as proc_id,
               gen_random_uuid() as new_register_id,
               (register_process->>'status') as r_status,
               COALESCE((register_process->>'attemptCount')::int, 0) as r_attempt
        FROM processing_status
        WHERE register_process IS NOT NULL
      )
      INSERT INTO register_process(id, status, attempt_count, created_at, updated_at)
      SELECT new_register_id, COALESCE(r_status,'not_queued')::register_process_status_enum, r_attempt, now(), now() FROM moved;

      UPDATE processing_status p
      SET register_process_id = m.new_register_id
      FROM moved m
      WHERE p.id = m.proc_id;

      ALTER TABLE processing_status DROP COLUMN IF EXISTS register_process;
    END IF;
  END IF;
END$$;

CREATE INDEX IF NOT EXISTS idx_processing_status_shipment_id ON processing_status (shipment_id);
CREATE INDEX IF NOT EXISTS idx_processing_status_status ON processing_status (status);
