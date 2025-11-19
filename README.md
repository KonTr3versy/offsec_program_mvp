# Internal Offensive Security Program MVP

This repository contains a minimal backend application for managing an internal
offensive security / penetration testing program. It is built with:

- **FastAPI** (Python web framework)
- **SQLAlchemy** (ORM)
- **Pydantic** (request/response validation)
- **SQLite or PostgreSQL** (database, depending on configuration)

## High-level features

- Manage **program years** and **engagements** (Infra, Web App, PCI, OT, External, Purple)
- Track **intake requests** from internal stakeholders
- Define **assets** in scope for each engagement
- Record **findings** with:
  - severity, status, remediation status, due dates
  - detection status (for purple teaming with the SOC)
  - affected assets
- Log **timeline events** and **comments** for collaboration
- Maintain a library of **finding templates**
- Generate a structured JSON **engagement report** via `/engagements/{id}/report`

## Project layout

```text
offsec_program_mvp/
  main.py               # FastAPI application entrypoint
  db.py                 # Database engine & session
  models.py             # SQLAlchemy ORM models
  routers/              # FastAPI routers (users, engagements, findings, assets, etc.)
  schemas/              # Pydantic schemas
requirements.txt         # Python dependencies
DEPLOYMENT_README.md     # Additional deployment notes
deploy/                  # Deployment-related configs (systemd, nginx, docker, terraform)
scripts/                 # Utility scripts (e.g. database seeding)
```

## Running locally (dev)

1. Create and activate a virtual environment:

   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

2. Install dependencies:

   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

3. Run the app (SQLite dev mode):

   ```bash
   export REQUIRE_API_KEY=false
   export DATABASE_URL=sqlite:///./offsec_program.db
   uvicorn offsec_program_mvp.main:app --reload
   ```

4. Open the docs in your browser:

   - http://127.0.0.1:8000/docs

## Configuration

Configuration is managed via environment variables (see `offsec_program_mvp/config.py`):

- `DATABASE_URL` – SQLAlchemy database URL  
  - Dev default: `sqlite:///./offsec_program.db`
  - Example Postgres: `postgresql+psycopg2://user:password@host:5432/offsec_program`
- `REQUIRE_API_KEY` – `true` or `false`  
  - `false` in local dev allows a fallback to the first user  
  - `true` in staging/production enforces the `X-API-Key` header
- `OFFSEC_ENV` – environment name (`dev`, `test`, `prod`, etc.)

## Authentication & roles

- On first run, the app seeds a default admin user (e.g. "malcolm") with an API key, printed to the logs.
- Clients should include `X-API-Key: <value>` on all requests in non-dev environments.
- Users have a `role` field (`admin`, `red`, `blue`, `manager`, etc.).
- RBAC helpers are provided so that certain endpoints can be restricted to specific roles.

## Deployment

See the `deploy/` directory for examples:

- `deploy/systemd/offsec-program.service` – run the app as a systemd service
- `deploy/nginx/offsec-program.conf` – example reverse proxy configuration
- `deploy/docker/Dockerfile` – Docker image definition
- `deploy/docker/docker-compose.yml` – simple Compose setup
- `deploy/terraform/ec2/main.tf` – example AWS EC2 provisioning

For a simple test deployment on AWS EC2:

1. Launch an Ubuntu EC2 instance.
2. Install Git and Python.
3. Clone this repo and install dependencies.
4. Set environment variables (`DATABASE_URL`, `REQUIRE_API_KEY`, etc.).
5. Use the provided systemd and nginx configs under `deploy/`.

## Scripts

- `scripts/seed_db.py` – example script to seed roles/users or other reference data.

## Disclaimer

This is an internal tool MVP intended for controlled environments.  
Before using in production, ensure authentication, authorization, logging, backup,
and monitoring are configured according to your organization’s standards.
