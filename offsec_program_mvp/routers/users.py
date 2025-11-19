"""Routers for user-related endpoints.

This module defines endpoints for listing users and retrieving the
current user.  In a real system you would extend this to support
creating users, updating profiles and proper authentication.  For
the MVP we seed a single admin user and use API key authentication.
"""

from typing import List, Optional
import secrets

from fastapi import APIRouter, Depends, HTTPException, Header, status
from sqlalchemy.orm import Session

from ..db import get_db
from .. import models
from ..schemas.user import UserOut

router = APIRouter(prefix="/users", tags=["users"])


def get_current_user(
    db: Session = Depends(get_db),
    x_api_key: Optional[str] = Header(None, alias="X-API-Key")
) -> models.User:
    """Retrieve the current user for authentication purposes.

    Authenticates using the X-API-Key header. If no API key is provided,
    falls back to returning the first user (for backward compatibility).
    In a production application you would require API keys for all requests.
    """
    if x_api_key:
        user = db.query(models.User).filter(models.User.api_key == x_api_key).first()
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid API key"
            )
        return user
    
    user = db.query(models.User).first()
    if not user:
        raise HTTPException(status_code=500, detail="No users in database")
    return user


@router.get("/", response_model=List[UserOut])
def list_users(db: Session = Depends(get_db)) -> List[UserOut]:
    """List all users in the system.

    Only returns non-sensitive fields.  For the MVP there is no
    authorisation logic; in a real system you would restrict this to
    administrators.
    """
    users = db.query(models.User).all()
    return [
        UserOut(
            id=u.id,
            username=u.username,
            full_name=u.full_name,
            email=u.email,
            role=u.role,
            created_at=u.created_at,
        )
        for u in users
    ]


@router.post("/{user_id}/regenerate-api-key", status_code=status.HTTP_200_OK)
def regenerate_api_key(
    user_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Regenerate API key for a user.

    Only administrators can regenerate API keys. Returns the new API key.
    This is the only time the API key will be shown, so save it securely.
    """
    if current_user.role != "admin":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only administrators can regenerate API keys"
        )
    
    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    new_api_key = secrets.token_urlsafe(32)
    user.api_key = new_api_key
    db.commit()
    
    return {
        "user_id": user.id,
        "username": user.username,
        "api_key": new_api_key,
        "message": "API key regenerated successfully. Save this key - it won't be shown again!"
    }