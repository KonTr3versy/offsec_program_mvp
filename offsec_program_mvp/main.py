"""Entry point for the FastAPI application.

This module sets up the FastAPI app, creates the database tables and
seeds an initial user for demonstration purposes.  It includes all
routers defined in the ``routers`` package.  To run the application
locally use ``uvicorn offsec_program_mvp.main:app --reload``.
"""

import secrets
from fastapi import FastAPI

from .db import engine, SessionLocal
from .models import Base, User
from .routers import (
    users,
    intake,
    engagements,
    findings,
    assets,
    timeline_comments,
    finding_templates,
)


app = FastAPI(title="Internal Offensive Security Program MVP")

# Create tables at startup.  In production you would handle this via
# migrations.
Base.metadata.create_all(bind=engine)


def seed_user():
    """Seed an initial user if none exist.

    The seeded user has the username ``malcolm`` and role ``admin``.
    Passwords are not enforced in this MVP.  In a real system you
    should hash user passwords and use proper authentication.
    An API key is generated for the seeded user for API access.
    """
    with SessionLocal() as db:
        if not db.query(User).first():
            api_key = secrets.token_urlsafe(32)
            user = User(
                username="malcolm",
                full_name="Malcolm Green",
                email="malcolm@example.com",
                role="admin",
                password_hash="fakehash",  # do not use plain text in production
                api_key=api_key,
            )
            db.add(user)
            db.commit()
            print(f"Seeded user 'malcolm' with API key: {api_key}")
            print("Save this API key - it won't be displayed again!")


# Run the seed function at import time
seed_user()

# Include routers for API endpoints
app.include_router(users.router)
app.include_router(intake.router)
app.include_router(engagements.router)
app.include_router(findings.router)
app.include_router(assets.router)
app.include_router(timeline_comments.router)
app.include_router(finding_templates.router)