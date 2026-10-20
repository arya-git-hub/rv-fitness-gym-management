"""
app/core/security.py
Supabase JWT verification + role-based access control.

How it works:
  1. Supabase signs JWTs with its JWT secret (SUPABASE_JWT_SECRET).
  2. We verify the token locally — no network call needed.
  3. The `sub` claim is the Supabase user UUID, stored in profiles.id.
  4. We load the profile from DB to get the role.

Usage in a router:
    from app.core.security import get_current_user, require_role

    @router.get("/admin-only")
    def admin_view(user = Depends(require_role("admin"))):
        ...
"""

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import settings
from app.core.database import get_db

bearer_scheme = HTTPBearer()

ALGORITHM = "HS256"


def _decode_token(token: str) -> dict:
    """Decode and verify a Supabase JWT. Raises 401 on any failure."""
    try:
        payload = jwt.decode(
            token,
            settings.SUPABASE_JWT_SECRET,
            algorithms=[ALGORITHM],
            audience="authenticated",
        )
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token.",
            headers={"WWW-Authenticate": "Bearer"},
        )


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(bearer_scheme),
    db: Session = Depends(get_db),
):
    """
    FastAPI dependency.
    Returns the Profile ORM object for the authenticated user.
    Raises 401 if the token is invalid or the profile is missing/inactive.
    """
    # Import here to avoid circular imports (models import Base from database).
    from app.models.all_models import Profile

    payload = _decode_token(credentials.credentials)
    user_id: str = payload.get("sub")
    if not user_id:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload.")

    profile = db.query(Profile).filter(Profile.id == user_id).first()
    if not profile:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User profile not found.")
    if not profile.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account is inactive.")

    return profile


def require_role(*roles: str):
    """
    Factory that returns a FastAPI dependency enforcing one of the given roles.

    Example:
        Depends(require_role("admin"))
        Depends(require_role("admin", "trainer"))
    """
    def _check(user=Depends(get_current_user)):
        if user.role not in roles:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Access denied. Required role: {' or '.join(roles)}.",
            )
        return user
    return _check
