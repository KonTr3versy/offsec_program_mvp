"""Utility script to seed the database with initial data.

This can be used to create default roles, users and example program years or
engagements. Run it in the same environment where your application runs:

    python -m scripts.seed_db
"""

from datetime import datetime
from sqlalchemy.orm import Session

from offsec_program_mvp.db import SessionLocal, Base, engine
from offsec_program_mvp import models

import secrets


def seed():
    Base.metadata.create_all(bind=engine)
    db: Session = SessionLocal()

    try:
        # Ensure at least one admin user exists
        admin = (
            db.query(models.User)
            .filter(models.User.username == "malcolm")
            .first()
        )
        if not admin:
            api_key = secrets.token_urlsafe(32)
            admin = models.User(
                username="malcolm",
                full_name="Malcolm Green",
                email="malcolm@example.com",
                role="admin",
                password_hash="fakehash",  # placeholder
                api_key=api_key,
            )
            db.add(admin)
            db.commit()
            db.refresh(admin)
            print(f"Seeded admin user 'malcolm' with API key: {api_key}")
        else:
            print("Admin user 'malcolm' already exists; not creating a new one.")

        # Example: ensure a current program year exists
        year = datetime.utcnow().year
        py = db.query(models.ProgramYear).filter(models.ProgramYear.year == year).first()
        if not py:
            py = models.ProgramYear(
                year=year,
                theme="Default program year",
                objectives="Seeded program year for initial testing.",
            )
            db.add(py)
            db.commit()
            print(f"Created ProgramYear for {year}")
        else:
            print(f"ProgramYear for {year} already exists.")

    finally:
        db.close()


if __name__ == "__main__":
    seed()
