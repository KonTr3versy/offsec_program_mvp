# Offensive Security Program MVP

This repository contains a minimal prototype for an internal offensive
security program manager.  The application is designed to help track
penetration testing engagements, intake requests, assets, findings,
timeline events and comments.  It exposes a JSON-based REST API
implemented with [FastAPI](https://fastapi.tiangolo.com/) and
[SQLAlchemy](https://www.sqlalchemy.org/).

## Features

* **Program years and engagements** – organise your penetration testing
  work by year and specific engagement (e.g. network test, web
  application test, PCI assessment).
* **Intake requests** – capture internal requests for testing and
  convert them into engagements.
* **Assets catalogue** – manage hosts, IP ranges, domains, apps and
  other assets that can be reused across engagements.
* **Findings and remediation tracking** – record issues discovered
  during an engagement along with their remediation and detection
  statuses.
* **Timeline events and comments** – log significant activities and
  collaborate with blue team members.
* **Structured report endpoint** – generate a JSON structure suitable
  for building a full report document.

This MVP does not include user authentication, report generation to
Word/PDF, or a front‑end UI.  It is intended to serve as a backend
service that can be extended and integrated into your tooling.

## Getting started

1. **Clone this repository** and navigate into the project directory:

   ```bash
   git clone <repository-url>
   cd offsec_program_mvp
   ```

2. **Create a virtual environment** (optional but recommended) and
   install dependencies.  For example using `venv` and `pip`:

   ```bash
   python -m venv venv
   source venv/bin/activate
   pip install fastapi uvicorn sqlalchemy "pydantic<2"
   ```

3. **Run the application** using Uvicorn:

   ```bash
   uvicorn offsec_program_mvp.main:app --reload
   ```

   The API will be available at `http://127.0.0.1:8000` with
   interactive documentation at `http://127.0.0.1:8000/docs`.

4. **Seed user**: On startup the application automatically seeds a
   default admin user (`malcolm` with no password).  Authentication is
   not enforced in this MVP.  All endpoints operate on behalf of this
   user.

## API overview

Below is a brief summary of the available endpoints.  For full
documentation open the Swagger UI at `/docs`.

| Method & path                         | Description                                   |
|--------------------------------------|-----------------------------------------------|
| `GET /users`                          | List users (admin only).                      |
| `POST /intake`                        | Create a new intake request.                 |
| `GET /intake`                         | List intake requests.                        |
| `POST /engagements`                   | Create a new engagement.                     |
| `GET /engagements`                    | List engagements with optional filters.      |
| `GET /engagements/{id}`               | Retrieve engagement details (with nested).   |
| `PATCH /engagements/{id}`             | Update an engagement.                        |
| `GET /engagements/{id}/report`        | Generate a structured JSON report.           |
| `POST /engagements/{id}/findings`     | Create a new finding for an engagement.      |
| `GET /engagements/{id}/findings`      | List findings for an engagement.             |
| `POST /assets`                        | Create a new asset.                          |
| `GET /assets`                         | List all assets.                             |
| `POST /engagements/{id}/timeline`     | Log a timeline event.                        |
| `GET /engagements/{id}/timeline`      | List timeline events for an engagement.      |
| `POST /engagements/{id}/comments`     | Add a comment to an engagement.              |

## Next steps

This MVP lays the groundwork for a more fully featured offensive
security program management platform.  Potential next steps include:

* Implementing proper authentication and role‑based access control.
* Adding endpoints to update and delete records.
* Building a front‑end UI or integrating with your existing reporting
  pipeline.
* Converting the JSON report into a formatted document using tools such
  as `python-docx` or `jinja2` templates.
* Adding support for purple team exercises, detection tracking and
  dashboards to visualise progress over time.

Contributions and suggestions are welcome!