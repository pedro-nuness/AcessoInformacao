# Hackaton - Participa DF

## n8n (Workflow Automation) — Docker Compose

This project includes a ready-to-run `docker-compose.yml` to start an n8n instance backed by Postgres.

- Compose file: [docker-compose.yml](docker-compose.yml)
- Environment: [.env](.env)

Quick start:

```bash
docker compose up -d
```

Open n8n at http://localhost:5678 and log in with the credentials from `.env`.

Data directories created locally:

- `postgres-data/` — Postgres database files
- `n8n-data/` — n8n runtime data

Security notes:

- Update `N8N_BASIC_AUTH_PASSWORD` and `POSTGRES_PASSWORD` in [.env](.env) before exposing the service publicly.
- For production, consider using a managed Postgres, TLS termination, and a reverse proxy.
# Hackaton - Participa DF