-- Init script for Postgres (runs during container initialization)
-- Creates an example `items` table and inserts a sample row.

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
