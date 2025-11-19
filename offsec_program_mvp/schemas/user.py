"""Pydantic schemas for users.

These schemas describe the public representation of users.  They are
used when returning user information from the API but do not expose
internal details such as password hashes.
"""

from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class UserOut(BaseModel):
    """Public representation of a user."""

    id: int
    username: str
    full_name: Optional[str]
    email: Optional[str]
    role: str
    created_at: datetime

    class Config:
        orm_mode = True