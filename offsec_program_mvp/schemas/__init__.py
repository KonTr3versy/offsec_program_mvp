"""Pydantic schemas used for request and response validation.

Each module in this package defines Pydantic models for the
corresponding domain objects (e.g. Engagement, Asset, Finding).  These
schemas are used by FastAPI to validate incoming data and to serialise
database models into JSON for responses.
"""