"""Database configuration for the Offensive Security Program MVP.

This module defines the SQLAlchemy engine, session factory and declarative base
classes. It is used by the models and routers to obtain a database session
bound to a SQLite file on disk. Changing the connection string here will
allow you to use a different database engine (for example PostgreSQL) in
the future.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Use a local SQLite database. To migrate to another engine (e.g. Postgres),
# change this connection string accordingly.
SQLALCHEMY_DATABASE_URL = "sqlite:///./offsec_program.db"

# For SQLite we need to disable thread checking so the same connection can be
# shared across threads. For other engines, remove the connect_args.
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},  # Only for SQLite
)

# SessionLocal is a factory that will create new Session objects connected to
# our engine.  autocommit=False and autoflush=False ensure we have explicit
# control over transactions and flushing.
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base class for our SQLAlchemy models.  All models will inherit from this
# class which keeps track of tables and columns in the metadata.
Base = declarative_base()


def get_db():
    """FastAPI dependency that yields a database session.

    A new Session is created for each request. The session is yielded to
    the caller and then properly closed once the request is completed.
    """
    from sqlalchemy.orm import Session

    db: Session = SessionLocal()
    try:
        yield db
    finally:
        db.close()