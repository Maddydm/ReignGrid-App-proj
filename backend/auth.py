from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from backend.config import (
    JWT_SECRET_KEY,
    JWT_ALGORITHM,
    ACCESS_TOKEN_EXPIRE_MINUTES,
    INSPECTOR_EMAIL,
    LEGACY_INSPECTOR_EMAIL,
    INSPECTOR_PASSWORD,
    INSPECTOR_NAME,
    INSPECTOR_TITLE,
)
from backend.models import UserProfile

security = HTTPBearer(auto_error=False)

def authenticate_user(username_or_email: str, password: str) -> Optional[UserProfile]:
    """Verify inspector credentials."""
    valid_usernames = [INSPECTOR_EMAIL.lower(), LEGACY_INSPECTOR_EMAIL.lower(), "inspector"]
    if username_or_email.lower() in valid_usernames and password == INSPECTOR_PASSWORD:
        return UserProfile(
            email=INSPECTOR_EMAIL,
            name=INSPECTOR_NAME,
            role="inspector",
            title=INSPECTOR_TITLE,
        )
    return None

def create_access_token(user: UserProfile) -> str:
    """Create a signed JWT access token."""
    now = datetime.now(timezone.utc)
    expire = now + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    payload = {
        "sub": user.email,
        "name": user.name,
        "role": user.role,
        "title": user.title,
        "iat": int(now.timestamp()),
        "exp": int(expire.timestamp()),
    }
    return jwt.encode(payload, JWT_SECRET_KEY, algorithm=JWT_ALGORITHM)

def decode_access_token(token: str) -> dict:
    """Decode and validate a JWT access token."""
    try:
        payload = jwt.decode(token, JWT_SECRET_KEY, algorithms=[JWT_ALGORITHM])
        return payload
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired. Please log in again.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

def get_current_user(credentials: Optional[HTTPAuthorizationCredentials] = Depends(security)) -> UserProfile:
    """Dependency: Require a valid authenticated user."""
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Authentication credentials required. Please provide a Bearer token.",
            headers={"WWW-Authenticate": "Bearer"},
        )
    payload = decode_access_token(credentials.credentials)
    return UserProfile(
        email=payload.get("sub", ""),
        name=payload.get("name", "Cadastral Inspector"),
        role=payload.get("role", "inspector"),
        title=payload.get("title", "Inspector"),
    )

def require_inspector(user: UserProfile = Depends(get_current_user)) -> UserProfile:
    """Dependency: Require an authenticated user with role == 'inspector'."""
    if user.role != "inspector":
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access restricted: Inspector privileges required.",
        )
    return user
